import serial
from datetime import datetime as dt, timedelta as tdel
import csv
from tkinter import filedialog, Tk, messagebox
import sys


READ_INTERVAL = 1.0 # seconds
PORT = 'COM2'
BAUDRATE = 9600
TIMEOUT = 10.0


ser = serial.Serial(
            port=PORT, 
            baudrate=BAUDRATE,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_NONE,
            timeout=TIMEOUT)

then = dt.now()

data = ['datetime', 'mass (grams)']

while True:
    try:
        mass_string = ser.readline().decode().strip()
        now = dt.now()
        mass_list = mass_string.split(' ')
        
        if mass_list[-1] != 'OK':
            mass_datum = ''.join(mass_list[:-1])
        else:
            mass_datum = ''.join(mass_list[:-2])
        
        if now - then >= tdel(seconds=READ_INTERVAL):
            then = now
            data.append([str(now), mass_datum])
            print(now, mass_datum)
    except KeyboardInterrupt:
        break



Tk().withdraw()
try:
    filename = filedialog.asksaveasfilename(
        initialdir = ".",
        title = "Select where you want to save the data.",
        filetypes = (
            ("CSV","*.csv"),
            ("all files","*.*")
            )
        )
    assert filename, "WARNING: DATA NOT SAVED!"
except AssertionError as e:
    print(e)
    yes = messagebox.askyesno("WARNING!", "Are you sure you want to discard these data?")
    if not yes:
            filename = filedialog.asksaveasfilename(
        initialdir = ".",
        title = "Select where you want to save the data.",
        filetypes = (
            ("CSV","*.csv"),
            ("all files","*.*")
            )
        )
    else:
        sys.exit()

filename += '.csv'
with open(filename, 'w', newline="") as f:
    writer = csv.writer(f)
    for row in data:
        writer.writerow(row)

input("PRESS ENTER TO EXIT...")