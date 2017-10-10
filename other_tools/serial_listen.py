import serial
from time import sleep

usb_channel = 'COM3'

ser = serial.Serial(usb_channel, 9600, timeout=0.25)


while True:
    x = ser.readline()
    
    data = x.split(',')
    lst = list(x)
    
    #if len(lst) > 0:
    #    print x,
    #    if lst[0] == '|': sleep(0.05)
    #    else: sleep(0.05)
    
    if len(data) > 2 and float(data[1]) > 1000*60*20: # stop at 20 minutes
        break

raw_input("\n\nFinished listening to %s. Press Enter to quit...\n\n" \
    % usb_channel)
