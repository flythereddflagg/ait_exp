import serial
from time import sleep

channel = 'COM1'
baud_rate = 19200 
data_bits = serial.EIGHTBITS
stop_bits = serial.STOPBITS_ONE
parity_opt = serial.PARITY_NONE
flow_control = False
wait_time    = 1.0

out = False
while(not out):
    try:
        ser = serial.Serial(
            channel, 
            baud_rate,
            parity   = parity_opt,
            stopbits = stop_bits,
            timeout  = wait_time,
            xonxoff  = flow_control,
            rtscts   = flow_control,
            dsrdtr   = flow_control)
            
        out = True
    except serial.serialutil.SerialException as detail:
        
        print("\nSerialException: %s\n" % detail)
        input("Press ENTER to try again")



while True:
    x = ser.readline()
    print(x)



