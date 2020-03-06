from os import name as osname
from sys import exit

testing = True
if testing:
    if __name__ == '__main__':
        from test_mod import Serial, SerialException, comports
    else:
        from .test_mod import Serial, SerialException, comports
else:
    import serial
    from serial.tools.list_ports import comports
    Serial = serial.Serial
    SerialException = serial.SerialException



class TADASerial():

    def __init__(self, comport=None, baudrate=9600, timeout=1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self.comport = self.serial_port() if comport is None else comport
        if not self.connect(): 
            raise Exception("Unable to connect to Arduino")
    

    def connect(self):
        """
        Attempts to connect with Arduino using pyserial or equivalent object
        Returns True if successful False otherwise.
        """
        try:
            self.ser = Serial(
                self.comport, 
                self.baudrate,
                timeout=self.timeout)
            assert self.ser.isOpen(), "Main serial port is not open."
            return True
        except AssertionError as e1:
            print("Error:", e1)
            return False
        except SerialException as e2:
            print("SerialException:", e2)
            return False


    def serial_port(self):
        """
        returns a string of the first available port that is not COM 1
        excludes 'COM 1' because that is generally reserved for the 
        RS 232 interface from the barometer
        """
        for port in comports():
            try:
                s = Serial(port[0])
                s.close()
                return port[0]
            except SerialException as e:
                continue


    def collect_data(self):
        self.ser.write(b'1')
    

    def stop_collecting_data(self):
        self.ser.write(b'0')


    def sync_time(self, event=None):
        """
        Synchronizes computer time with the arduino.
        """
        if self.collect: return
        time_obj= localtime()
        serial_time = strftime("t%Y,%m,%d,%H,%M,%S", time_obj)
        print(serial_time)
        self.system_timestamp = f"\nSystem start time is: {serial_time}"
        print(serial_time.encode(encoding="ascii"))
        self.ser.write(serial_time.encode(encoding="ascii"))

       
    def get_data(self):
        """ 
        Get Data from the serial source and return it as a list.
        """
        data_string = self.ser.readline().decode()
        
        if len(data_string) == 0: # check for empty string
            return self.get_data()
        
        if   data_string[0] == '|' and data_string[-1] == '\n':
            # if the data_string is valid, process it
            data_string = data_string.strip()            
            data = data_string.split(',')            
            data = [float(val) for val in data[1:]]
                
            return data

        elif data_string[0] == '+' and data_string[-1] == '\n':
            # if the data_string is a valid time stamp, process it
            self.system_timestamp = "\nSystem start time is: "\
                "%s" % strftime("%Y/%m/%d %H:%M:%S", localtime())
            self.arduino_timestamp = data_string.strip()
            return self.arduino_timestamp
        
        elif data_string[0] == '/' and data_string[-1] == '\n':
            # if string begins with / then it is a debug message and should
            # just be returned
            return data_string.strip()
        else:
            # if the data_string is invalid, print it, and try again
            return self.get_data()
    



if __name__ == '__main__':
    ts = TADASerial()
    while True:
        try:
            print(ts.get_data())
        except KeyboardInterrupt:
            break
