import serial
from datetime import datetime as dt, timedelta as tdel
import csv
from tkinter import filedialog, Tk, messagebox
import sys

# correct for pressure transducer

READ_INTERVAL = 1.0 # seconds
PORT = 'COM5'
BAUDRATE = 9600
PARITY = serial.PARITY_ODD
TIMEOUT = 3.0

"""
Julabo bath
COM4
4800
parity even
flowcontrol hardware
data bits 7
stop bits 1

Omega pressure transducer
COM5
9600
databits 7
stopbits 1
parity odd
pressure in psi

viscometer
COM3
9600

E05  cde rs
E06  ab fghijklm opq tuvwxyz
none n
"""

ser = serial.Serial(
            port=PORT, 
            baudrate=BAUDRATE,
            bytesize=serial.SEVENBITS,
            parity=PARITY,
            timeout=TIMEOUT)

then = dt.now()

data = ['datetime', 'mass (grams)']

while True:
    try:
        # data = input('> ')
        ser.write('*V01\r'.encode())
        data_string = ser.readline().decode().strip()
        now = dt.now()
        # mass_list = mass_string.split(' ')
        
        # if mass_list[-1] != 'OK':
            # mass_datum = ''.join(mass_list[:-1])
        # else:
            # mass_datum = ''.join(mass_list[:-2])
        
        # if now - then >= tdel(seconds=READ_INTERVAL):
            # then = now
            # data.append([str(now), mass_datum])
        print(now, f'{data_string!r}')
    except KeyboardInterrupt:
        break



# Tk().withdraw()
# try:
    # filename = filedialog.asksaveasfilename(
        # initialdir = ".",
        # title = "Select where you want to save the data.",
        # filetypes = (
            # ("CSV","*.csv"),
            # ("all files","*.*")
            # )
        # )
    # assert filename, "WARNING: DATA NOT SAVED!"
# except AssertionError as e:
    # print(e)
    # yes = messagebox.askyesno("WARNING!", "Are you sure you want to discard these data?")
    # if not yes:
            # filename = filedialog.asksaveasfilename(
        # initialdir = ".",
        # title = "Select where you want to save the data.",
        # filetypes = (
            # ("CSV","*.csv"),
            # ("all files","*.*")
            # )
        # )
    # else:
        # sys.exit()

# filename += '.csv'
# with open(filename, 'w', newline="") as f:
    # writer = csv.writer(f)
    # for row in data:
        # writer.writerow(row)

# input("PRESS ENTER TO EXIT...")