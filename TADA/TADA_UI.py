#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
file: TADA_UI.py
name: Thermocouple Amplifier-Data Aquisition User Interface (TA-DA UI)
author: Mark Redd
email: redddogjr@gmail.com

python version: 3.6.3

Description:
A GUI for collecting time dependent data and storing the data in comma separated
values files (.csv). Originally designed to collect 4 temperature data vs. time 
and plot one of the temperatures in real time with matplotlib. Ideal for 
use with Arduino.
"""

## Tkinter imports
from tkinter import Tk, Frame, BOTH, TOP, RIGHT, LEFT, Label, Button, Entry,\
    W, E, N, S, END
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import askyesno

## Matplotlib graphing imports
from matplotlib import use
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## Other misc. imports
from os import system, name as osname
from sys import exit
import serial
from time import localtime, strftime
import winsound


class DAQGUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.path1 = 'C:\\Users\\Public\\Documents\\AIT\\data\\dump.csv'
        self.collect = False
        self.vis_data = 100     #Number of visible data points
        self.com_port = ''
        self.baud_rate = 9600   #Serial rate (/s)
        self.init_delay = 1000  #Time to wait before restarting interface (ms)
        self.recurse_counter = 0
        self.start_time = 0
        self.time = 0
        self.arduino_timestamp = ""
        self.system_timestamp = ""
        self.rs232_port = 'COM1'
        self.rs232_baudrate = 19200
        self.pemergency = 1000.0
        self.atm1 = 760.0
        self.plower = 758.0
        self.pupper = 762.0
        self.baro_press = 640.0 # barometric pressure in torr (nominal expected value
        self.pvessel = 640.0 # absolute pressure inside the vessel
        self.initUI()

    def initUI(self):
        """ Initialize the UI Interface with all widgets. """
        
        ## Start GUI and bind keys
        self.parent.title("TA-DA UI 0.4 - ALPHA")
        self.parent.bind("<Escape>", self.quit_it)
        self.parent.bind("<Return>", self.start_stop)
        self.parent.bind("<Control-s>", self.file_save_as)
        self.parent.bind("<Control-t>", self.sync_time)
        self.parent.config(bg='black')
        
        self.parent.rowconfigure(0, pad=5)
        self.parent.rowconfigure(1, pad=5)
        self.parent.rowconfigure(4, weight=2)
        self.parent.rowconfigure(5, pad=5)
        
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)
        self.parent.columnconfigure(2, weight=1)
        self.parent.columnconfigure(3, weight=1)
        self.parent.columnconfigure(4, weight=1)
        self.parent.columnconfigure(5, weight=1)
        self.parent.columnconfigure(6, weight=1)
        self.parent.columnconfigure(7, weight=1)
        self.parent.columnconfigure(8, weight=1)
        self.parent.columnconfigure(9, weight=1)
        self.parent.columnconfigure(10, weight=1)
        self.parent.columnconfigure(11, weight=1)
        
        
        ## Set up interactive plot
        self.figure, self.ax = subplots(facecolor='black')
        self.ax.set_facecolor('black')
        self.lines, = self.ax.plot([],[],'lime')
        xlabel('Time (ms)')
        ylabel('Temperature (deg C)')
        
        ## Format graph
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white') 
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')

        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        self.ax.yaxis.label.set_color('white')
        self.ax.xaxis.label.set_color('white')
        
        # Autoscale axis
        self.ax.set_autoscaley_on(True)
        self.ax.set_autoscalex_on(True)
        self.ax.grid(color='white') # give the plot a grid 
        tight_layout()
        ion() # Turn on interactive mode
        
        ## Embed save and path
        self.sv_btn = Button(master=self.parent, text='Choose Target File',
            command=self.file_save_as, bg='black', fg='white',padx=5,pady=5)
        self.path_text = Label(master=self.parent, text=self.path1,bg='black',
            fg='white',pady=5)
        ## Embed plot in tk window
        graph1 = FigureCanvasTkAgg(self.figure, master=self.parent)
        graph1.get_tk_widget().configure(bg='black',
            highlightcolor='black', highlightbackground='black')
        
        # info labels
        self.lexp_time   = Label(master=self.parent,text="Time of Exp",
            bg='black', fg='white',padx=3)
        self.lcompound   = Label(master=self.parent,text="Compound Name",
            bg='black', fg='white',padx=3)
        self.lphase      = Label(master=self.parent,text="Phase",bg='black', 
            fg='white',padx=3)
        self.lsamp_size  = Label(master=self.parent,text="Samp Size",bg='black',
            fg='white',padx=3)
        self.lset_pt     = Label(master=self.parent,text="Set Pt",bg='black', 
            fg='white',padx=3)
        self.ltest_temp  = Label(master=self.parent,text="Test Temp",bg='black',
            fg='white',padx=3)
        self.lignition   = Label(master=self.parent,text="Ignition?",bg='black',
            fg='white',padx=3)
        self.lhot_cold   = Label(master=self.parent,text="Hot/Cold?",bg='black', 
            fg='white',padx=3)
        self.lsound      = Label(master=self.parent,text="Sound?",bg='black', 
            fg='white',padx=3)
        self.lrel_hum = Label(master=self.parent,text="rh%/ext temp",
            bg='black', fg='white',padx=3)
        self.lnotes = Label(master=self.parent,text="Notes",
            bg='black', fg='white',padx=3)
        
        # info fields
        self.exp_time   = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.compound   = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.phase      = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.samp_size  = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.set_pt     = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.test_temp  = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.ignition   = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.hot_cold   = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.sound      = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.rel_hum = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        self.notes = Entry(master=self.parent,bg='black', fg='white',
            justify='center',insertbackground='white')
        
        ## Embed buttons and messages in window
        self.button1 = Button(master=self.parent, text='Quit',
            command=self.quit_it, bg='black', fg='white',padx=5,pady=5)
        self.button_sync = Button(master=self.parent, text='Sync Time',
            command=self.sync_time, bg='black', fg='white',padx=5,pady=5)
        self.button2 = Button(master=self.parent, text='Collect Data',
            command=self.start_stop, bg='green',padx=5,pady=5)
        self.msg1 = Label(master=self.parent, text="Data Collection Ready", 
            bg='black', fg='white',padx=5,pady=5)
        self.press = Label(master=self.parent, text="P(abs): 0 torr", 
            bg='black', fg='white',padx=5,pady=5,relief='groove')
        
        # grid set
        self.sv_btn.grid(row=0,column=0,columnspan=13)
        self.path_text.grid(row=1,column=0,columnspan=13)
        
        self.lexp_time.grid(row=2,column=0,columnspan=2)
        self.lcompound.grid(row=2,column=2)
        self.lphase.grid(row=2,column=3)    
        self.lsamp_size.grid(row=2,column=4)
        self.lset_pt.grid(row=2,column=5)
        self.ltest_temp.grid(row=2,column=6)
        self.lignition.grid(row=2,column=7)
        self.lhot_cold.grid(row=2,column=8) 
        self.lsound.grid(row=2,column=9)   
        self.lrel_hum.grid(row=2,column=11)
        self.lnotes.grid(row=2,column=12)
        
        self.exp_time.grid(row=3,column=0,columnspan=2)
        self.compound.grid(row=3,column=2)
        self.phase.grid(row=3,column=3)    
        self.samp_size.grid(row=3,column=4)
        self.set_pt.grid(row=3,column=5)
        self.test_temp.grid(row=3,column=6)
        self.ignition.grid(row=3,column=7)
        self.hot_cold.grid(row=3,column=8) 
        self.sound.grid(row=3,column=9)
        self.rel_hum.grid(row=3,column=11)
        self.notes.grid(row=3,column=12)
        
        graph1.get_tk_widget().grid(row=4,column=0,columnspan=13,sticky=W+E+N+S)
        graph1._tkcanvas.grid(row=4,column=0,columnspan=13,sticky=W+E+N+S)
        
        self.button1.grid(row=5,column=0)
        self.button_sync.grid(row=5,column=1,sticky=W)
        self.msg1.grid(row=5,column=6,columnspan=5)
        self.button2.grid(row=5,column=12)
        self.press.grid(row=5,column=2,columnspan=5)
        
        print("GUI Set up complete.\nAttempting to connect to TA-DA...")
        ## Start the DAQ
        while not self.connect():
            x = input("Could not connect to TA-DA.\n Please fix the above issues and press "\
                "ENTER to continue \n OR\n Enter q and press ENTER to quit ")
            if len(x) > 0 and x[0] == 'q': self.quit_it()

        print("Arduino is connected.")
        self.clean_up()
        self.daq_loop()
        
    def connect(self):
        try:
            self.com_port = self.serial_port()
            self.ser = serial.Serial(
                self.serial_port(), 
                self.baud_rate,
                timeout=1.0)
            self.rs232 = serial.Serial(
                self.rs232_port,
                self.rs232_baudrate,
				timeout=1.0)
            assert(self.ser.isOpen() and self.rs232.isOpen())
            return True
        except serial.serialutil.SerialException as detail:
            print("\nSerialException: \n{}\n".format(detail))
            return False
        except AssertionError:
            print("\nAssertionError:\n TA-DA port '{}' and"\
                " Vaisala Barometer Port '{}' are not open.\n".format(
                self.com_port, self.rs232_port))
            return False
            
        
    def clean_up(self):
        """ Re-initializes the parameters for data collection and clears the 
            console screen."""
        system('cls' if osname == 'nt' else 'clear')

        self.xdata = []
        self.ydata = []
        self.data = [
            ['time','t1','t2','t3','t4','pressure']]
    
    def file_save_as(self, event=None):
        """ Run save as dialog to choose target file. If an existing file is
            chosen the file is truncated and overwritten."""
        f = asksaveasfile(mode='w', defaultextension=".csv")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None: 
            return None
        self.path1 = f.name
        f.close()
        self.path_text['text'] = self.path1
        self.ser.close()
        self.clean_up()
        self.parent.after(self.init_delay, self.ser.open())
        return self.path1
    
    def format_data(self, data):
        """ Converts the data from a lists of lists to a string with a newline 
            character between data points and a space between data point 
            elements."""
        data_out = []
        for i in data:
            pt1 = []
            if i == ['time','t1','t2','t3','t4','pressure']:# or list(str(i[0]))[0] == '+':
                pt2 = ",".join(i)
                data_out.append(pt2)
                continue
            for j in i:
                pt1.append("{.2f}".format(j))
            pt2 = ",".join(pt1)
            data_out.append(pt2)
        data_out.insert(0,"")
        out = "\n".join(data_out)
        return out
    
    def get_data(self):
        """ 
        Get Data from some source and return it as a list.
        Return None if it doesn't work
        """
        
        try:
            data_string = self.ser.readline().decode()
            data_chars = list(data_string)
        except Exception as e:
            print(e)
            print('Data could not be read')
            return None
        
        if len(data_chars) == 0: # check for empty string
            return None
            
        print("%s" %data_string, end=' ')
        
        if data_chars[0] != '|': # it's not data
            if data_chars[0] == '+': # it's the arduino timestamp
                self.system_timestamp = "\nSystem start time is: "\
                    "%s" % strftime("%Y/%m/%d %H:%M:%S", localtime())
                self.arduino_timestamp = data_string
                self.arduino_timestamp = self.arduino_timestamp.strip(
                    "\r\n")
            self.parent.after(0, self.get_data)
            return
        elif data_chars[-1] != '\n':
            #Check if incomplete data string
            return None
            
        # It is a complete data string
        data_string = data_string.strip("\r\n")
        data = data_string.split(',')
        data.pop(0) # get rid of leading symbol
        for i in range(len(data)):
            try:
                data[i] = float(data[i])
            except ValueError:  #replace non-number data with zeros
                data[i] = 0.0
        self.update_baro(data)
        return data
    
    def update_baro(self,data):
        """
        Pulls barometric pressure data in and adds it to the gauge pressure
        Also updates the state of the pressure label to indicate if the 
        pressure is within acceptable parameters. Makes a warning sound if 
        pressure far exceeds acceptable parameters.
        """
        try:
            self.baro_press = float(self.rs232.readline().decode())
            data[-1] += self.baro_press
            self.pvessel = data[-1]
        except ValueError:
             self.pvessel = data[-1] + self.baro_press
        
        if self.pvessel < self.plower:
            self.press['bg'] = 'blue'
            self.press['fg'] = 'white'
            state = " (low)"
        elif self.pvessel > self.pupper:
            self.press['bg'] = '#cc0000'
            self.press['fg'] = 'white'
            state = " (high)"
        else:
            self.press['bg'] = '#80ff00'
            self.press['fg'] = 'black'
            state = ""
        
        self.press['text'] = "P(abs): {:3.3f} torr{}".format(data[-1], state)
        
        if self.pvessel > self.pemergency:
            self.msg1['text'] = "WARNING! P > 1000 TORR! SHUTDOWN NOW!"
            self.msg['bg'] = '#cc0000'
            self.msg['fg'] = 'white'
            winsound.Beep(880, 125)
            
    
    def graph_it(self, data1):
        """ Reset the data to be graphed and then update the graph """
        if len(self.xdata) > self.vis_data and len(self.xdata) > self.vis_data:
            self.xdata.pop(0)
            self.ydata.pop(0)
            
        self.xdata.append(data1[0])
        self.ydata.append(data1[4])
        self.plt_update(self.xdata, self.ydata)
    
    def daq_loop(self):
        """ Part of the mainloop. This funtion will run every 0.5 seconds. If
            the "collect" parameter is set to True it will append the data it 
            collects to an array to be saved to the output file.
            
            The loop functions with these instructions:
                - Get data as a list from some source
                - Save the data to an array if self.collect == True
                - Update the graph with the latest data point
                - Loop
            This will execute on startup and continue doing while mainloop is 
            still running."""
        
        self.recurse_counter += 1         # count recursions
        data1 = self.get_data()           # get data
        if data1 == None:
            return self.parent.after(0, self.daq_loop)
        self.time = data1[0]
        if self.collect == True:
            #print data1,
            self.data.append(data1)       # save data to array
            print("Data collected.")
            t1 = float(data1[0] - self.start_time)/1000
            self.msg1['text'] = "Collecting Data...\t"\
                "Time (sec): %.1f" % (t1)

        self.graph_it(data1)              # put the data on a graph
        
        self.parent.after(0, self.daq_loop) # loop
            

    def plt_update(self, xdata, ydata):
        """ Update the plot with xdata and ydata """
        #Update data (with the new _and_ the old points)

        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def quit_it(self, event=None):
        """ Safely Exit Program """
        if self.collect == True:
            if not askyesno("Quit Warning", \
                "DAQ is still running!\nAre you sure you want to quit?"):
                return
        self.parent.quit()
        self.parent.destroy()
        exit()

    
    def start_stop(self, event=None):
        """ The Start Stop proceedure. Once stopped the program will ask you 
            to choose a file to save to if you haven't already. Then it saves
            the file and resets the DAQ. If you cancel the save all your data 
            will be lost."""
        if self.collect == False:
            # tell the Arduino to start writing its data to the SD card
            self.start_time = self.time
            self.ser.write(b'1')
            self.clean_up()
            self.collect = True
            self.msg1['text'] = "Collecting Data..."
            self.button2['bg'] = 'red'
            self.button2['fg'] = 'white'
            self.button2['text'] = "Stop Collection"

        else:
            try:
                f = open(self.path1,'r') # see if the file exists
                f.close()
            except:
                f1 = self.file_save_as() # if not open save as dialog
                if f1 == None:
                    if askyesno("Save Warning:\n", \
                        "Cancelling will stop data collection delete all data"\
                        "from this run."\
                        " Are you sure you want to cancel your save?"):
                            self.stop_reset()
                            return
                    else:
                        return
            
            f = open(self.path1,'a')
            text_out = self.format_data(self.data)
            data_name_out = self.get_data_name()
            f.write("Time of Exp,Compound Name,Phase,Samp Size,Set Pt,Test "\
            "Temp,Ignition?,Hot/Cold?,Sound?,Relative Humidity,"\
            "Notes\n")
            f.write(data_name_out)
            f.write('\n')
            f.write(self.arduino_timestamp)
            f.write(self.system_timestamp)
            f.write(text_out)
            f.close()
            self.stop_reset()

    def stop_reset(self):
        """ Resets the buttons and indicates Data collection is ready"""
        # tell the Arduino to stop writing its data to the SD card
        self.ser.write(b'0')
        self.collect = False
        self.button2['bg'] = 'green'
        self.button2['fg'] = 'black'
        self.button2['text'] = 'Collect Data'
        self.msg1['text'] = "Data Collection Ready"
        print("\n\t--- Data Collection Stopped. Press ENTER to continue ---\n")
    
    def sync_time(self, event=None):
        if self.collect: return
        t1 = localtime()
        tser = strftime("t%Y,%m,%d,%H,%M,%S", t1).encode()
        self.system_timestamp = "\nSystem start time is: "\
            "%s" % strftime("%Y/%m/%d %H:%M:%S", t1)
        
        #print tser
        self.ser.write(tser)
        
        #self.parent.after(self.init_delay, self.ser.close())
        self.clean_up()
        #self.parent.after(self.init_delay, self.ser.open())
    
    def serial_port(self):
        """
        returns a string of the first available port that is not COM 1
        excludes 'COM 1' because that is generally reserved for the 
        RS 232 interface from the barometer
        """
        if osname == 'nt':
            # windows
            for i in range(1,256):
                try:
                    s = serial.Serial('COM'+ str(i + 1))
                    s.close()
                    return 'COM' + str(i + 1)
                except serial.SerialException:
                    pass
        else:
            # unix
            for port in list_ports.comports():
                return port[0]
    
    def trigger_check(self, trigger):
        if trigger:
            self.start_stop()
    
    def get_data_name(self):
        data_exp = [
            self.exp_time.get(),
            self.compound.get(),
            self.phase.get(),
            self.samp_size.get(),
            self.set_pt.get(),
            self.test_temp.get(),
            self.ignition.get(),
            self.hot_cold.get(),
            self.sound.get(),
            self.rel_hum.get(),
            self.notes.get()]
        
        self.exp_time.delete(0, END)
        self.compound.delete(0, END)
        self.phase.delete(0, END)
        self.samp_size.delete(0, END)
        self.set_pt.delete(0, END)
        self.test_temp.delete(0, END)
        self.ignition.delete(0, END)
        self.hot_cold.delete(0, END)
        self.sound.delete(0, END)
        self.rel_hum.delete(0, END)
        self.notes.delete(0, END)
        
        datastring = ','.join(data_exp)
        return datastring

        
def main():
    root = Tk()
    root.geometry("1200x600+50+50")
    root.iconbitmap(r'flame.ico')
    app = DAQGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_it)
    root.mainloop()    


if __name__ == '__main__':
    main()
