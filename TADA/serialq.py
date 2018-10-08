

# Serial(
# self.serial_port(), 
# self.baud_rate,
# timeout=1.0)
from random import random, uniform
from time import clock

class Serial():
    def __init__(self, port, baud_rate, timeout=0):
        self.time = clock()
        self.port = port
    
    def isOpen(self):
        return True

    
    def open(self):
        print("SERIAL: Port is opening...")
    
    def close(self):
        print("SERIAL: Port is closing...")
        
    def readline(self):
    
        if self.port == "TADA Serial Port":
        
            out = "|,{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}\n".format(
                clock() - self.time,
                random(),
                random(),
                random(),
                random(),
                uniform(0, 200))
        else:
            out = "{:.3f}".format(uniform(645.0, 650.0))
        return out.encode("ASCII")
