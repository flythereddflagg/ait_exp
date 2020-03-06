


from random import random, uniform
from time import sleep, time

def beep(*args):
    pass

class Serial():
    def __init__(self, port, baud_rate=0, timeout=0):
        self.time = time()
        self.port = port
    
    def isOpen(self):
        return True
    
    def write(self, *args, **kwargs):
        pass
    
    def open(self):
        print("SERIAL: Port is opening...")
    
    def close(self):
        print("SERIAL: Port is closing...")
        
    def readline(self):
        sleep(0.25)
        
        if self.port != "COM1":
        
            out = "|,{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}\n".format(
                (time() - self.time) * 1000,
                random()*1000,
                random(),
                random(),
                random(),
                uniform(0, 200))
        else:
            out = "{:.3f}".format(uniform(645.0, 650.0))
        return out.encode("ASCII")

        
        
class SerialException(Exception):
    def __init__(self, message):
        self.message = message


def comports():
    for port in ['COM1', 'COM2']:
        yield port
