"""
GoPro_timestamp_with_filewalker.py
Created by Chris Rillahan
Last Updated by Creator: 1/30/2015
Originally written with Python 2.7.2, OpenCV 2.4.8

The original script can be found at the following URL:
https://www.theeminentcodfish.com/gopro-timestamp/

The full project with all files can be found on GitHub:
https://github.com/EminentCodfish/GoPro-Timestamp

This script requires OpenCV and ffmpeg to run. Detailed instructions on how to
install OpenCV can be found at the following URLs:
http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_intro/py_intro.html#intro
Ubuntu 16.04: http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/
Fedora 18: http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_fedora/py_setup_in_fedora.html#install-opencv-python-in-fedora
Windows: http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows

ffmpeg may be downloaded and installed from the following URL:
https://www.ffmpeg.org/download.html

Modified by Mark Redd
Last Updated: 12 July 2017
Tested with Python 2.7.13, OpenCV 3.2.0, Ubuntu 16.04

This script is the same as the GoPro_timestamp.py except that it adds the
ability to batch process a series of files.  This script uses the os.walk()
function to create a list of all the files in a folder.  Each file is then
iterated through, if the file contains the extension .MP4 then the basic
timestamp script is executed on the file.

MODIFICATIONS:
 - This script will recursively go through all subdirectories looking for all 
.MP4 files.
 - It will automatically skip files that already have a .avi file with the 
same name in same folder. 
 - To manually skip a file, press ctrl-c. 
 - It keeps a progress percent at the bottom of each output.
"""

import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
from subprocess import call

#Creates a command call to ffprobe which returns the files metadata.  The
#metadata is then parsed to return the creation time only.

def creation_time(filename):

    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', 
        filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    print "==========output=========="
    print out
    if err:
        print "========= error ========"
        print err
    t = out.splitlines()
    time = str(t[14][18:37])
    return time

#Directory which contains the video files. 
## in this case, the same path the python file is in
indir = os.path.dirname(os.path.realpath(__file__))

#Filewalker function
for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        try:
            if f[-4:] == '.MP4':
                video_filename = "%s/%s" %(root,f)
                if os.path.exists(video_filename[:-4] + '.avi'):
                    print "\n%s already exists!" % (video_filename[:-4] +\
                        '.avi')
                    print "Skipping timestamp for %s ...\n" % video_filename
                    continue
                
                print('Starting to timestamp: ' + str(f))
                
                #Opens the video import and sets parameters
                video = cv2.VideoCapture(video_filename)

                #Checks to see if a the video was properly imported
                status = video.isOpened()

                if status == True: 
                    FPS = video.get(cv2.CAP_PROP_FPS)
                    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    size = (int(width), int(height))
                    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
                    #frame_lapse = (1/FPS)*1000

                    #Initializes the export video file
                    codec = cv2.VideoWriter_fourcc('D','I','V','X')
                    video_out = cv2.VideoWriter(video_filename[:-4] + '.avi', 
                        codec, FPS, size, 1)

                    #Initializes time origin of the video
                    t = creation_time(video_filename)
                    initial = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    timestamp = initial

                    #Initializes the frame counter
                    current_frame = 0

                    start = time.time()

                    #iterates through each frame and adds the timestamp before 
                    #sending the frame to the output file.
                    while current_frame < total_frames:
                        success, image = video.read()
                        elapsed_time = video.get(cv2.CAP_PROP_POS_MSEC)
                        current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
                        timestamp = initial + dt.timedelta(
                            microseconds = elapsed_time*1000)
                        t = timestamp + dt.timedelta(
                            microseconds = -timestamp.microsecond)
                        
                        cv2.putText(image, 'Date: ' + str(timestamp)[0:10], 
                            (50,int(height-150)), 
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                            2, (255, 255, 255), 3)
                            
                        cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], 
                            (50,int(height-100)), 
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                            2, (255, 255, 255), 3)
                         
                        video_out.write(image)

                        k = cv2.waitKey(1)
                        if k == 27:
                            video.release()
                            video_out.release()
                            cv2.destroyAllWindows()
                            sys.exit()

                        # print progress percent
                        progress = int(100.0 * current_frame / total_frames)
                        sys.stdout.flush()
                        print '\r',
                        print 'Time Stamping Progress... %d%%' % progress,

                    print '\n'
                    video.release()
                    video_out.release()
                    cv2.destroyAllWindows()

                    duration = (time.time()-float(start))/60

                    print("Video has been timestamped")
                    print('This video took:' + str(duration) + ' minutes\n')
                else:
                    print('Error: Video failed to load')
        except KeyboardInterrupt:
            print "\n\nSkipping...\n"
            continue
    #break
