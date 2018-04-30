#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
name: TA-DA UI - ALPHA
version: 0.4.0
author: Mark Redd
email: redddogjr@gmail.com
Source Forge: https://sourceforge.net/u/flythereddflagg/profile/

last modified: 13 June 2017
python version: 2.7.13

Description:
A GUI for collecting time dependent data and storing the data in comma separated
values files (.csv). Originally designed to collect 4 temperature data vs. time 
and plot one of the temperatures in real time with matplotlib. Ideal for 
use with Arduino.

Changes to this version:
 - Add arduino functionality with the arduino keeping track of time
"""

## Tkinter imports
from Tkinter import Tk, Frame, BOTH, TOP, RIGHT, LEFT, Label, Button, Entry
from tkFileDialog import asksaveasfile
from tkMessageBox import askyesno

## Matplotlib graphing imports
from matplotlib import use
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## Other misc. imports
from os import system, name as osname
import serial
from time import localtime, strftime


class DAQGUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.path1 = 'C:\\Users\\Public\\Documents\\AIT\\data\\dump.csv'
        self.collect = False
        self.vis_data = 100
        self.recurse_counter = 0
        self.start_time = 0
        self.time = 0
        self.arduino_timestamp = ""
        self.system_timestamp = ""
        self.initUI()

    def initUI(self):
        """ Initialize the UI Interface with all widgets. """
        
        ## Start GUI and bind keys
        self.parent.title("TA-DA UI 0.4 - ALPHA")
        self.parent.bind("<Escape>", self.quit_it)
        self.parent.bind("<backslash>", self.start_stop)
        self.parent.bind("<Control-s>", self.file_save_as)
        self.parent.config(bg='black')
        
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
            command=self.file_save_as, bg='black', fg='white')
        self.path_text = Label(master=self.parent, text=self.path1,bg='black',
            fg='white')
        self.sv_btn.pack(side=TOP)
        self.path_text.pack(side=TOP)

        
        ## Embed plot in tk window
        graph1 = FigureCanvasTkAgg(self.figure, master=self.parent)
        graph1.get_tk_widget().configure(bg='black',
            highlightcolor='black', highlightbackground='black')
        graph1.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        graph1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        
        ## Embed buttons and messages in window
        self.button1 = Button(master=self.parent, text='Quit',
            command=self.quit_it, bg='black', fg='white')
        self.button1.pack(side=LEFT)
        
        self.button_sync = Button(master=self.parent, text='Sync Time',
            command=self.sync_time, bg='black', fg='white')
        self.button_sync.pack(side=LEFT)
        
        self.button2 = Button(master=self.parent, text='Collect Data',
            command=self.start_stop, bg='green')
        self.button2.pack(side=RIGHT)
        
        self.msg1 = Label(master=self.parent, text="Data Collection Ready", 
            bg='black', fg='white')
        self.msg1.pack(side=TOP)
        
        
        

        ## Start the DAQ
        self.ser = serial.Serial('COM3', 9600, timeout=1.0)
        self.clean_up()
        self.daq_loop()
        
    def clean_up(self):
        """ Re-initializes the parameters for data collection and clears the 
            console screen."""
        system('cls' if osname == 'nt' else 'clear')

        self.xdata = []
        self.ydata = []
        self.data = [
            #['0.0'                    ],
            ['time','t1','t2','t3','t4']]
    
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
        self.parent.after(1000, self.ser.open())
        return self.path1
    
    def format_data(self, data):
        """ Converts the data from a lists of lists to a string with a newline 
            character between data points and a space between data point 
            elements."""
        data_out = []
        for i in data:
            pt1 = []
            if i == ['time','t1','t2','t3','t4']:# or list(str(i[0]))[0] == '+':
                pt2 = ",".join(i)
                data_out.append(pt2)
                continue
            for j in i:

                pt1.append("%.2f" % j)
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
            data_string = self.ser.readline()
            data_chars = list(data_string)
        except self.ser.self.serialTimeoutException:
            print('Data could not be read')
            return None
        
        if len(data_chars) > 0: # check for empty string
            print data_string,
            if data_chars[0] != '|': # it's not data
                if data_chars[0] == '+': # it's the arduino timestamp
                    self.system_timestamp = "\nSystem start time is: "\
                        "%s" % strftime("%Y/%m/%d %H:%M:%S", localtime())
                    self.arduino_timestamp = data_string
                    self.arduino_timestamp = self.arduino_timestamp.strip(
                        "\r\n")
                self.parent.after(0, self.get_data)
                return
        else:
            return None
        
        if data_chars[0] == '|' and data_chars[-1] == '\n':
            # Check for complete data string
            data_string = data_string.strip("\r\n")
            data = data_string.split(',')
            data.pop(0)
            for i in range(len(data)):
                try:
                    data[i] = float(data[i])
                except ValueError:
                    data[i] = 0.0
        else:
            # skip if else
            return None
        return data
    
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
            print "Data collected."
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
    
    #def passit(self):
    #    pass
    
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
        print "\n\t--- Data Collection Stopped. Press \\ to continue ---\n"
    
    def sync_time(self, event=None):
        if self.collect: return
        t1 = localtime()
        tser = strftime(b"t%Y,%m,%d,%H,%M,%S", t1)
        self.system_timestamp = "\nSystem start time is: "\
            "%s" % strftime("%Y/%m/%d %H:%M:%S", t1)
        
        #print tser
        self.ser.write(tser)
        
        #self.parent.after(1000, self.ser.close())
        self.clean_up()
        #self.parent.after(1000, self.ser.open())
    
    def trigger_check(self, trigger):
        if trigger:
            self.start_stop()
            
        
        
        
def main():
    root = Tk()
    root.geometry("600x600+200+200")
    root.iconbitmap(r'flame.ico')
    app = DAQGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_it)
    root.mainloop()    


if __name__ == '__main__':
    main()
