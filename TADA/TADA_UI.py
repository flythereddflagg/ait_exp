#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
file: TADA_UI.py
name: Thermocouple Amplifier-Data Aquisition User Interface (TA-DA UI)
author: Mark Redd
email: redddogjr@gmail.com

Description:
A GUI for collecting time dependent data and storing the data in comma separated
values files (.csv). Originally designed to collect 4 temperature data vs. time 
and plot one of the temperatures in real time with matplotlib. Ideal for 
use with Arduino.
"""

## Tkinter imports
from tkinter import Tk, Label, Button, Entry, W, E, N, S, END
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import askyesno

## Matplotlib graphing imports
from matplotlib import use
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## Other misc. imports
from os import system, name as osname
from math import fabs, fsum
#from sys import exit
from time import localtime, strftime

testing = False

if testing:
    import test_mod as serial
else:
    import serial

if osname == 'nt':
    import winsound
else:
    import test_mod as winsound



class DAQGUI(Tk):
  
    def __init__(self):
        super().__init__()
        # constants
        self.plower         =   758.0
        self.pupper         =   762.0
        self.vis_data       =   100    # Number of visible data points
        self.tada_baudrate  =  9600 
        self.init_delay     =  1000    # Wait time before interface restart (ms)
        self.rs232_port     = 'COM1'
        self.rs232_baudrate = 19200
        self.pemergency     =   206
        self.eq_tol         =     0.0155 # maximum allowable AAD% in temperature
        self.delta_t_tol    =     0.51 # maximum allowable ΔT over 25 seconds
        self.log_path       = "./experimental_log.csv"
          
        # initial/default values
        self.target_data_path   = './dump.csv'
        self.collect            = False
        self.running            = True
        self.start_time         = 0
        self.current_time       = 0
        self.arduino_timestamp  = ""
        self.system_timestamp   = ""
        self.baro_press         = 640.0 # barometric pressure in torr 
        self.pvessel            = 640.0 # absolute pressure inside the vessel
        self.gpress             = 0     # gauge pressure inside the vessel

        # setup commands
        self.initUI()
        self.init_serial()
        self.clean_up()
        
        # run the main loop program
        self.daq_loop()
        

    
    
    def initUI(self):
        """ 
        Initializes and configures the UI with all widgets. 
        """
        # set window title
        self.title("TA-DA UI 0.6 - BETA")
        
        # Bind keys to common actions
        self.bind("<Escape>", self.quit_app)
        self.bind("<Return>", self.start_stop)
        self.bind("<Control-s>", self.file_save_as)
        self.config(bg='black')
        
        # Configure rows
        self.rowconfigure(0, pad=5)
        self.rowconfigure(1, pad=5)
        self.rowconfigure(4, weight=2)
        self.rowconfigure(5, pad=5)
        
        # Configure columns
        for i in range(10):
            self.columnconfigure(i, weight=1)
        
        # Set up all widgets in the UI
        self.init_plot()
        self.init_widgets()
        self.grid_widgets()
        
        # Setup window preferences
        #self.iconbitmap(r'flame.ico')
        self.geometry("1200x600+50+50")
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        
    
    
    def init_plot(self):
        """
        Sets up plot with colors and sizing formats.
        """
        # color the background black
        self.figure, self.ax = subplots(facecolor='black')
        self.ax.set_facecolor('black')
        # color the foreground white
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white') 
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.yaxis.label.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.grid(color='white')
        # color the plot line lime green
        self.lines, = self.ax.plot([],[],'lime')
        # label the axes
        xlabel('Time (ms)')
        ylabel('Temperature (deg C)')
        # set up the interactive plot
        tight_layout()
        self.ax.set_autoscaley_on(True)
        self.ax.set_autoscalex_on(True)
        # Turn on interactive mode
        ion() 
        # Embed plot in a canvas to be placed in the window
        self.data_plot = FigureCanvasTkAgg(self.figure, 
                                            master=self).get_tk_widget()
        # Color the canvas black
        self.data_plot.configure(   bg='black',
                                    highlightcolor='black', 
                                    highlightbackground='black')
        
    
    
    def init_widgets(self):
        """
        Sets up all widgets except the plot
        """
        
        button_options  = {'master':self, 'bg':'black', 'fg':'white', 'padx':5,
                            'pady':5}
        label_options   = {'master':self, 'bg':'black', 'fg':'white', 'padx':3}
        entry_options   = {'master':self, 'bg':'black', 'fg':'white',
                            'justify':'center', 'insertbackground':'white'}
        
        # Setup save button and path label                  
        self.button_save = Button(text='Choose Target File',
                                command=self.file_save_as, **button_options)
        self.path_text   = Label(**label_options, text=self.target_data_path)
        
        # Setup info labels
        self.lexp_time  = Label(**label_options, text="Time of Exp")
        self.lcompound  = Label(**label_options, text="Compound Name")
        self.lsamp_size = Label(**label_options, text="Samp Size")
        self.lset_pt    = Label(**label_options, text="Set Pt",)
        self.ltest_temp = Label(**label_options, text="Test Temp")
        self.lhot_cold  = Label(**label_options, text="Ignition\nHot/Cold/No")
        self.lsound     = Label(**label_options, text="Sound? (y/n)",)
        self.lrel_hum   = Label(**label_options, text="rh%/ext temp")
        self.lnotes     = Label(**label_options, text="Notes")
        
        
        # Setup info fields                            
        self.exp_time   = Entry(**entry_options)
        self.compound   = Entry(**entry_options)
        self.samp_size  = Entry(**entry_options)
        self.set_pt     = Entry(**entry_options)
        self.test_temp  = Entry(**entry_options)
        self.hot_cold   = Entry(**entry_options)
        self.sound      = Entry(**entry_options)
        self.rel_hum    = Entry(**entry_options)
        self.notes      = Entry(**entry_options)
        
        # Setup buttons and messages at bottom
        self.button_quit = Button(text='Quit', command=self.quit_app, 
                                    **button_options)
        self.press = Label(master=self, text="P(abs): 0 torr", 
            bg='black', fg='white', padx=5, pady=5, relief='groove')
        self.eq_msg = Label(master=self, text="Temp Ready",
            bg='#80ff00', fg='black', padx=5, pady=5, relief='groove')
        self.msg1 = Label(text="Data Collection Ready", **label_options)
        self.button_collect_data = Button(  master=self, 
                                            text='Collect Data',
                                            command=self.start_stop, 
                                            bg='green',
                                            padx=5,
                                            pady=5)
        
    
    
    def grid_widgets(self):
        """
        Places all widgets in the grid.
        """
        self.button_save.grid(          row=0, column=0, columnspan=10)
        self.path_text.grid(            row=1, column=0, columnspan=10)
                    
        self.lexp_time.grid(            row=2, column=0)
        self.lcompound.grid(            row=2, column=1)   
        self.lsamp_size.grid(           row=2, column=2)
        self.lset_pt.grid(              row=2, column=3)
        self.ltest_temp.grid(           row=2, column=4)
        self.lhot_cold.grid(            row=2, column=5) 
        self.lsound.grid(               row=2, column=6)   
        self.lrel_hum.grid(             row=2, column=7)
        self.lnotes.grid(               row=2, column=8, columnspan=2)
                                                
        self.exp_time.grid(             row=3, column=0, sticky=E+W)
        self.compound.grid(             row=3, column=1, sticky=E+W)
        self.samp_size.grid(            row=3, column=2, sticky=E+W)
        self.set_pt.grid(               row=3, column=3, sticky=E+W)
        self.test_temp.grid(            row=3, column=4, sticky=E+W)
        self.hot_cold.grid(             row=3, column=5, sticky=E+W) 
        self.sound.grid(                row=3, column=6, sticky=E+W)
        self.rel_hum.grid(              row=3, column=7, sticky=E+W)
        self.notes.grid(                row=3, column=8, columnspan=2,
                                        sticky=E+W)
        
        self.data_plot.grid(            row=4, column=0, columnspan=11, 
                                        sticky=W+E+N+S)
        
        self.button_quit.grid(          row=5, column=0, sticky=E+W)
        self.press.grid(                row=5, column=1, columnspan=2)
        self.eq_msg.grid(               row=5, column=3, sticky=E+W)
        self.msg1.grid(                 row=5, column=4, columnspan=5)
        self.button_collect_data.grid(  row=5, column=9, sticky=E+W)
        
    
    
    def init_serial(self):
        print("GUI Set up complete.\nAttempting to connect to TA-DA...")
        while not self.connect():
            x = input("Could not connect to TA-DA.\n Please fix the above"\
                " issues and press ENTER to continue \n OR\n Enter q and"\
                " press ENTER to quit ")
            if len(x) > 0 and x[0] == 'q': self.quit_app()

        print("Arduino is connected.")

        
    
    
    def connect(self):
        """
        Attempts to connect with Arduino using pyserial or equivalent object
        Returns True if successful False otherwise.
        """
        try:
            self.com_port = self.serial_port()
            self.ser = serial.Serial(
                self.com_port, 
                self.tada_baudrate,
                timeout=1.0)
            self.rs232 = serial.Serial(
                self.rs232_port,
                self.rs232_baudrate,
                timeout=0.1)
            assert(self.ser.isOpen() and self.rs232.isOpen())
            return True
        except AssertionError:
            print("\nAssertionError:\n TA-DA port '{}' and"\
                " Vaisala Barometer Port '{}' are not open.\n".format(
                self.com_port, self.rs232_port))
            return False
           
        
    
    
    def clean_up(self):
        """ 
        Re-initializes the parameters for data collection and clears the 
        console screen.
        """
        self.ser.close()

        self.xdata = []
        self.ydata = []
        # formatted as [['time','t1','t2','t3','t4','pressure']]
        self.data = []
       
        self.ser.open()
        self.after(self.init_delay, self.sync_time)
    
    
    
    
    def file_save_as(self, event=None):
        """ 
        Run save as dialog to choose target file. If an existing file is
        chosen the file is truncated and overwritten.
        """
        f = asksaveasfile(mode='w', defaultextension=".csv")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None: 
            return None
        self.target_data_path = f.name
        f.close()
        self.path_text['text'] = self.target_data_path
        self.clean_up()
        
        return self.target_data_path
    
    
    
    def format_data(self, data):
        """ 
        Returns the data from a lists of lists as a string with a newline 
        character between data points and a comma between each data point 
        element.
        """
        out_string = ""
        for point in data:
            out_string += ','.join([format(field, ".2f") for field in point])
            out_string += '\n'
        return out_string
    
    
    
    def get_data(self):
        """ 
        Get Data from the serial source and return it as a list.
        """
        try:
            data_string = self.ser.readline().decode()
        except Exception as e:
            print(e)
            print('Data could not be read')
            return None
        
        if len(data_string) == 0: # check for empty string
            return self.get_data()
        
        if   data_string[0] == '|' and data_string[-1] == '\n':
            # if the data_string is valid, process it
            data_string = data_string.strip()            
            data = data_string.split(',')
            data.pop(0) # get rid of leading symbol
            
            for i in range(len(data)): # convert strings to floats if possible
                try:
                    data[i] = float(data[i])
                except ValueError:  # replace non-number with -1000 - pi
                    data[i] = -1003.14159265359
                
            self.update_baro(data[-1])
            self.update_temp_equilbrium(data)
            print(data_string, '-', self.baro_press)
                
            data[-1] = self.pvessel
            return data
            
        elif data_string[0] == '+' and data_string[-1] == '\n':
            # if the data_string is a valid time stamp, process it
            print(data_string, end='')
            self.system_timestamp = "\nSystem start time is: "\
                "%s" % strftime("%Y/%m/%d %H:%M:%S", localtime())
            self.arduino_timestamp = data_string.strip()
            return self.get_data()
                
        else:
            # if the data_string is invalid, print it, and try again
            print(data_string, end='')
            return self.get_data()
    
    
    def update_baro(self, p_gauge):
        """
        Pulls barometric pressure data in and adds it to the gauge pressure
        Also updates the state of the pressure label to indicate if the 
        pressure is within acceptable parameters. Makes a warning sound if 
        pressure far exceeds acceptable parameters.
        """
        self.gpress = p_gauge
        try:
            baro_press = float(self.rs232.readline().decode())
            if baro_press < 1000 or baro_press > 600: 
                    self.baro_press = baro_press
            self.pvessel = self.gpress + self.baro_press
        except ValueError:
            self.pvessel = self.gpress + self.baro_press
        
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
        
        self.press['text'] = "P(abs): {:3.3f} torr{}".format(
                                                        self.pvessel, state)
        
        if self.gpress > self.pemergency:
            self.msg_str = self.msg1['text']
            self.msg1['text'] = "WARNING! Gauge Pressure > 4 psi! SHUTDOWN NOW!"
            self.msg1['bg'] = '#cc0000'
            self.msg1['fg'] = 'white'
            winsound.Beep(880, 125)

       
       
    def update_temp_equilbrium(self, data):
        """
        Calculates the absolute average deviation (AAD) fraction from t4 of 
        all other temperatures and, if that AAD% is < the equilibrium tolerance 
        (self.eq_tol) then it marks the temperatures as ready. Not ready
        otherwise
        """
        t4 = data[4]
        try:
            aad_pct = fsum([fabs(t4 - temp) for temp in data[1:-2]]) /4 /t4
        except ZeroDivisionError as detail:
            print(detail)
            aad_pct = self.eq_tol + 2
        
        try:
            delta_temp = fabs(self.ydata[0] - self.ydata[-1])
        except IndexError:
            delta_temp = 10
        
        # absolute average deviation < tolerance and t4 has
        # changed less than ΔT_tol over the last bit of time,
        # you are ready to run
        if aad_pct < self.eq_tol and delta_temp < self.delta_t_tol:
            self.eq_msg['bg']   = '#80ff00'
            self.eq_msg['text'] = 'Temp Ready'
        else:
            self.eq_msg['bg']   = '#FFFF00'
            self.eq_msg['text'] = 'Temp NOT Ready'
    
    
    def graph_data(self, data1):
        """ Reset the data to be graphed and then update the graph """
        if len(self.xdata) > self.vis_data and len(self.ydata) > self.vis_data:
            self.xdata.pop(0)
            self.ydata.pop(0)
            
        self.xdata.append(data1[0])
        self.ydata.append(data1[4])
        self.plt_update(self.xdata, self.ydata)
    
    
    
    def daq_loop(self):
        """ 
            Part of the mainloop. This function will run every 0.5 seconds. If
            the "collect" parameter is set to True it will append the data it 
            collects to an array to be saved to the output file.
            
            The loop functions with these instructions:
                - Get data as a list from some source
                - Save the data to an array if self.collect == True
                - Update the graph with the latest data point
                - Loop
            This will execute on startup and continue doing while mainloop is 
            still running.
        """
        while self.running:
            data_point = self.get_data()    # get data
            self.current_time = data_point[0]
            if self.collect == True:
                self.data.append(data_point)# save data to array
                print("Data collected.")
                
                display_time = float(data_point[0] - self.start_time)/1000
                self.msg1['text'] = "Collecting Data...\tTime"\
                                    " (sec): {:.1f}".format(display_time)

            self.graph_data(data_point)     # put the data on a graph

            

    
    
    def plt_update(self, xdata, ydata):
        """
        Updates the plot with @param xdata and @param ydata 
        """
        # Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        
        # Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        
        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    
    
    def quit_app(self, event=None):
        """ 
        Safely Exits Program 
        """
        if self.collect == True:
            if not askyesno("Quit Warning", \
                "DAQ is still running!\nAre you sure you want to quit?"):
                return
        self.ser.write(b'0')
        self.running = False
        self.destroy()
        raise SystemExit
    
    
    
    def start_stop(self, event=None):
        """ The Start/Stop procedure. Once stopped the program will ask you 
            to choose a file to save to if you haven't already. Then it saves
            the file and resets the DAQ. If you cancel the save all your data 
            will be lost."""
        if self.collect == False: # this is the start branch
            # tell the Arduino to start writing its data to the SD card
            self.start_time = self.current_time
            self.ser.write(b'1')
            self.collect = True
            self.msg1['text'] = "Collecting Data..."
            self.button_collect_data['bg']   = 'red'
            self.button_collect_data['fg']   = 'white'
            self.button_collect_data['text'] = "Stop Collection"

        else: # this is the stop branch
            try:
                f = open(self.target_data_path, 'r') # see if the file exists
                f.close()
            except FileNotFoundError:
                # if file not found, create it
                f = open(self.target_data_path, 'w')
                f.close()
            
            # check the experiment log
            try:
                f = open(self.log_path, 'r') # see if the file exists
                f.close()
            except FileNotFoundError:
                # if file not found, create it
                f = open(self.log_path, 'w')
                f.write("file,Time of Exp,Compound Name,Samp Size,Set Pt,Test "\
                "Temp,Ignition State,Sound?,Relative Humidity,"\
                "Notes")
                f.close()
            
            text_out = self.format_data(self.data)
            data_name_out = self.get_data_fields()
            
            with open(self.log_path, 'a') as f:
                f.write("\n")
                f.write(self.target_data_path.split('/')[-1])
                f.write(',')
                f.write(data_name_out)


            with open(self.target_data_path,'a') as f:
                f.write("Time of Exp,Compound Name,Phase,Samp Size,Set Pt,Test "\
                "Temp,Hot/Cold?,Sound?,Relative Humidity,"\
                "Notes\n")
                f.write(data_name_out)
                f.write('\n')
                f.write(self.arduino_timestamp)
                f.write(self.system_timestamp)
                f.write('\n')
                f.write('time,t1,t2,t3,t4,pressure\n')
                f.write(text_out)
            
            self.stop_reset()

    
    
    def stop_reset(self):
        """ Resets the buttons and indicates Data collection is ready"""
        # tell the Arduino to stop writing its data to the SD card
        self.ser.write(b'0')
        self.collect = False
        self.button_collect_data['bg'] = 'green'
        self.button_collect_data['fg'] = 'black'
        self.button_collect_data['text'] = 'Collect Data'
        self.msg1['text'] = "Data Collection Ready"
        print("\n\t--- Data Collection Stopped. Press ENTER to continue ---\n")
    
    
    
    def sync_time(self, event=None):
        if self.collect: return
        time_obj= localtime()
        serial_time = strftime("t%Y,%m,%d,%H,%M,%S", time_obj)
        print(serial_time)
        self.system_timestamp = "\nSystem start time is: {}".format(serial_time)
        print(serial_time.encode(encoding="ascii"))
        self.ser.write(serial_time.encode(encoding="ascii"))


        
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
            pass
            # unix
            #for port in list_ports.comports():
            #    return port[0]

    
    
    
    def get_data_fields(self):
        data_exp = [
            self.exp_time.get(),
            self.compound.get(),
            self.samp_size.get(),
            self.set_pt.get(),
            self.test_temp.get(),
            self.hot_cold.get(),
            self.sound.get(),
            self.rel_hum.get(),
            self.notes.get()]
        
        self.exp_time.delete(0, END)
        self.compound.delete(0, END)
        self.samp_size.delete(0, END)
        self.set_pt.delete(0, END)
        self.test_temp.delete(0, END)
        self.hot_cold.delete(0, END)
        self.sound.delete(0, END)
        self.rel_hum.delete(0, END)
        self.notes.delete(0, END)
        
        datastring = ','.join(data_exp)
        return datastring

   

if __name__ == '__main__':
    DAQGUI().mainloop()
