# Data Extraction {#sec:data-extraction}

During experiments data are being recorded on the lab computer, the data logger and the camera. Both the camera and the data logger on the TADA have SD cards with a 32 GB storage capacity that allows multiple runs to be recorded without extraction. The following policies are in place to ensure ease of use, efficiency, and avoid common mistakes.

## General Policies {#sec:general-policies}

- All data, including video and raw temperature data should be extracted at least *daily*

- Video data should be extracted and properly renamed as often as  possible (i.e. between every run or every other run) to ensure the correct filenames are assigned to their corresponding video files

- The datalogger data is there as a redundant backup to the UI data in case of data loss. Therefore it will be mainly archived and used only when the  original data cannot be found

- After processing, all data should be organized according to the following conventions:
  - Path: `$PREFIX/compound_name/filename.ext`
    - `$PREFIX` for video data: `smb://pgl6ed.byu.edu/aitra/video`
    - `$PREFIX` for all other data: `/home/aitra/Documents/data`
  - All experiments should have a unique filename associated with them according to convention
  - All data from the experiment run should have the same filename but different extensions
  - The corresponding data from the datalogger will be archived and accessed as needed
    - Path: `/home/aitra/Documents/Data`
  - When processing is finished, all experiments should have the following 3 files with the same name preceding them
    - A .png/jpg) file (for temperature data with graphs and analysis)
    - A .csv file (TADA-generated)
    - A .avi/.mp4 file stored on the DIPPR Legacy Server
      (this video file will have a different path and extension but 
      the same filename)
  
- File naming convention: 

  - Filenames will be organized by the following values in order separated by underscores ('`_`')
    1. Compound name
    2. Date of experiment with the format "YYMMDD"
    3. Time of day that data collection began for that run using a 24 hour clock format "hhmm"
    4. Sample size in microliters (for liquids) or milligrams(for solids and gases)
    5. Test temperature in degrees Celsius (rounded to the nearest integer)
  - For example: The file name of an AIT experiment where 100 microliters of hexane were tested at 450 degrees Celsius on March 19, 2013 at 4:25 pm would be: `hexane_130319_1625_100_450.csv`

  - The corresponding video file would be named: `hexane_130319_1625_100_450.MP4"`



## Video Extraction {#sec:video-extraction}

The following procedure is necessary only if you have not or cannot extract and delete video via WiFi (See Section @sec:camera-operation).

1. Connect the camera to the computer via a micro USB cable (See Figure @fig:cam_diag)
1. Press the "info/wireless" button on the camera to connect the camera to the computer
1. A new icon should appear allowing you to access the SD card as if it were a USB drive.
1. Video files should be copied to the DIPPR Legacy Server (a.k.a. The Properties of Gases and Liquids 6th Edition Server) and organized as explained above
   - Path: `smb://pgl6ed.byu.edu/aitra/video`
   - Domain: `dipprleg`
   - Username: `aitra`
   - Password: `hotflame16`
1. Once you have ensured all video data have been have been properly saved in the appropriate data folder, delete all files from the camera

If you have trouble with the above method, you may remove the SD card and copy the video to the server using a similar method as below.


## Datalogger Extraction {#sec:datalogger-extraction}

To extract data from the datalogger:

1. Unplug the TADA from the computer
1. Pull out the SD card from the data logger and use the USB SD card adapter to copy the `DATALOG.CSV` file into the "raw_data" path and rename it to the original filename with the date tagged on in "YYMMMDD" format (e.g. `DATALOG_130319.CSV`)
   
1. Path: `/home/aitra/Documents/data/raw_data/`
   
1. Once you have ensured the data log file has been copied and renamed successfully, delete the `DATALOG.CSV` file on the SD card (the SD card should be empty)
1. Close all windows with the USB SD card adapter open (i.e. Windows Explorer etc.)
1. Pull out the SD card without ejecting the unit from the computer