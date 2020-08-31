from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports import comports
import time

class SerialDataSource():

    def __init__(self, comport=None, baudrate=9600, timeout=1.0):
            self.baudrate = baudrate
            self.timeout = timeout
            self.comport = self.serial_port() if not comport else comport
            if not self.connect(): 
                raise Exception(
                    f"Unable to connect to Serial Port: {self.comport!r}"
                )
            self.ser.reset_input_buffer()
            

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
            assert self.ser.isOpen(), "Port is not open."
            return True
        except AssertionError as e1:
            print("Error:", e1)
            return False
        except SerialException as e2:
            print("SerialException:", e2)
            return False


    def serial_port(self):
        """
        returns a string of the first available port
        """
        for port in comports():
            try:
                s = Serial(port[0])
                s.close()
                return port[0]
            except SerialException as e:
                continue


    def get_data(self):
        """ 
        Get Data from the serial source and return it as a list.
        """
        data_string = self.ser.readline().decode().strip()
        return [float(element) for element in data_string.split()]


    def reset(self):
        """Resets the serial port by closing it then opening it"""
        self.ser.close()
        self.ser.open()



class BaroDataSource(SerialDataSource):

    def __init__(self, comport=None, baudrate=9600, timeout=0.25):
            super().__init__(
                comport=comport, 
                baudrate=baudrate, 
                timeout=timeout
            )
            self.data = [0]


    def get_data(self):
        """ 
        Get Data from the serial source and return it as a list.
        """
        if self.ser.in_waiting:
            data_string = self.ser.readline().decode().strip()
            if not data_string: return self.data
            self.data = [
                float(element) for element in data_string.split()
            ]
            self.ser.reset_input_buffer()
        return self.data
        


class TADADataSource(SerialDataSource):

    def __init__(self, comport=None, baudrate=9600, timeout=1.0):
        super().__init__(comport=comport, baudrate=baudrate, timeout=timeout)
        self.reset_confirmed = False

    def reset(self):
        super().reset()
        self.reset_confirmed=False

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
        try:
            data_string = self.ser.readline().decode()
        except UnicodeDecodeError as e:
            return self.get_data()
        
        if not data_string: # check for empty string
            return self.get_data()
        
        if   data_string[0] == '|' and data_string[-1] == '\n' and\
                self.reset_confirmed:
            # if the data_string is valid, process it
            try:
                data_string = data_string.strip()            
                data = data_string.split(',')
                assert len(data) == 7, "Bad data Length"       
                data = [float(val) for val in data[1:]]
                data[0] /= 1000
                if self.ser.in_waiting: self.ser.reset_input_buffer()
                return data
            except (AssertionError, ValueError) as e:
                print("Error:", type(e), e)
                if self.ser.in_waiting: self.ser.reset_input_buffer()
                return self.get_data()


        elif data_string[0] == '+' and data_string[-1] == '\n' and\
                self.reset_confirmed:
            # if the data_string is a valid time stamp, process it
            # self.system_timestamp = "\nSystem start time is: "\
            #     "%s" % strftime("%Y/%m/%d %H:%M:%S", localtime())
            self.arduino_timestamp = data_string.strip()
            print(self.arduino_timestamp)
            return self.get_data()
        
        elif data_string[0] == '/' and data_string[-1] == '\n':
            # if string begins with / then it is a debug message and should
            # just be returned
            if "setup finished" in data_string.lower(): 
                self.reset_confirmed = True
            print(data_string.strip())
            return self.get_data()
        else:
            # if the data_string is invalid try again
            return self.get_data()



if __name__ == '__main__':
    print("Setting up arduino...")
    ts = TADADataSource(comport='/dev/ttyACM0', baudrate=9600)
    print("setting up baro...")
    baro = BaroDataSource(comport="/dev/ttyS0", baudrate=19200)
    print("starting loop.")
    while True:
        try:
            print(ts.get_data(), end=' ')
            print(baro.get_data())
        except KeyboardInterrupt:
            
            break
