#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: Mark Redd
"""
## Tkinter imports
from Tkinter import Tk, Frame, BOTH, TOP, BOTTOM, Button, RIGHT, LEFT, Label
import tkFileDialog
import tkMessageBox

## Matplotlib graphing imports
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## Other misc. imports
import os
import time
from random import randint



class GUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.path1 = None
        self.collect = False
        self.start_time = 0
        self.width = 6
        self.initUI()

    def initUI(self):
        """ Initialize the User Interface with all widgets. """
        
        ## Start GUI and bind keys
        self.parent.title("Matplotlib Embeded Data Aquisition")
        self.parent.bind("<Escape>", self.quit_it)
        self.parent.bind("<\>", self.start_stop)
        self.parent.bind("<Control-s>", self.file_save_as)
        
        ## Set up interactive plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[])#, 'o')
        # Autoscale axis
        self.ax.set_autoscaley_on(True)
        self.ax.set_autoscalex_on(True)
        self.ax.grid() # give the plot a grid 
        plt.ion() # Turn on interactive mode
        
        ## Embed save and path
        self.sv_btn = Button(master=self.parent, text='Choose Target File', \
            command=self.file_save_as)
        self.sv_btn.pack(side=TOP)
        self.path_text = Label(master=self.parent, text="(No Path)")
        self.path_text.pack(side=TOP)  
        
        ## Embed plot in tk window
        graph1 = FigureCanvasTkAgg(self.figure, master=self.parent)
        graph1.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        graph1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        
        ## Embed buttons and messages in window
        self.button1 = Button(master=self.parent, text='Quit', \
            command=self.quit_it)
        self.button1.pack(side=LEFT)
        
        self.button2 = Button(master=self.parent, text='Collect Data', \
            command=self.start_stop, bg='green')
        self.button2.pack(side=RIGHT)
        
        self.msg1 = Label(master=self.parent, text="Data Collection Ready")
        self.msg1.pack(side=TOP)
        
        ## Start the DAQ
        self.clean_up()
        self.loop()
        
    def clean_up(self):
        """ Re-initializes the parameters for data collection and clears the 
            console screen."""
        os.system("cls")
        self.start_time = time.time()
        self.xdata = []
        self.ydata = []
        self.data = [[0,0,0,0,0]]

    
    def quit_it(self, event=None):
        """ Safely Exit Program """
        if self.collect == True:
            if not tkMessageBox.askyesno("Quit Warning", \
                "DAQ is still running!\nAre you sure you want to quit?"):
                return
        self.parent.quit()
        self.parent.destroy()
    
    def file_save_as(self, event=None):
        """ Run save as dialog to choose target file. If an existing file is
            chosen the file is truncated and overwritten."""
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None: 
            return None
        self.path1 = f.name
        f.close()
        self.path_text['text'] = self.path1
        return self.path1
        
    def loop(self):
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
        print "Getting data...",
        data1 = self.get_data()           # get data
        
        if self.collect == True:
            print data1,
            self.data.append(data1)       # save data to array
            print "Data collected."
        else:
            print data1
        
        self.graph_it(data1)              # put the data on a graph
        
        self.parent.after(500, self.loop) # loop
    
    def graph_it(self, data1):
        """ Reset the data to be graphed and then update the graph """
        if len(self.xdata) > self.width and len(self.xdata) > self.width:
            self.xdata.pop(0)
            self.ydata.pop(0)
            
        self.xdata.append(data1[0])
        self.ydata.append(data1[4])
        self.plt_update(self.xdata, self.ydata)
    
    def get_data(self):
        """ Get Data from some source and return it as a list """
        now = round(time.time() - self.start_time, 1)
        return [now, randint(1,5),randint(1,5),randint(1,5),randint(1,5)]

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

    def start_stop(self, event=None):
        """ The Start Stop proceedure. Once stopped the program will ask you 
            to choose a file to save to if you haven't already. Then it saves
            the file and resets the DAQ. If you cancel the save all your data 
            will be lost."""
        if self.collect == False:
            self.msg1['text'] = "Collecting Data..."
            self.button2['bg'] = 'red'
            self.button2['fg'] = 'white'
            self.button2['text'] = "Stop Collection"
            self.collect = True
            self.clean_up()
        else:
            try:
                f = open(self.path1,'r') # see if the file exists
                f.close()
            except:
                f1 = self.file_save_as() # if not open save as dialog
                if f1 == None:
                    if tkMessageBox.askyesno("Save Warning:\n", \
                        "Cancelling this save dialog will stop data "\
                        "collection and you will lose all data from this run."\
                        " Are you sure you want to cancel your save?"):
                            self.stop_reset()
                            return
            
            f = open(self.path1,'a')
            text_out = self.format_data(self.data)
            f.write(text_out)
            f.close()
            self.stop_reset()

    def format_data(self, data):
        """ Converts the data from a lists of lists to a string with a newline 
            character between data points and a space between data point 
            elements."""
        data_out = []
        for i in data:
            pt1 = []
            for j in i:
                pt1.append("%.2f" % j)
            pt2 = " ".join(pt1)
            data_out.append(pt2)
        data_out.insert(0,"")
        out = "\n".join(data_out)

        return out
    
    def stop_reset(self):
        """ Resets the buttons and indicates Data collection is ready"""
        self.collect = False
        self.button2['bg'] = 'green'
        self.button2['fg'] = 'black'
        self.button2['text'] = 'Collect Data'
        self.msg1['text'] = "Data Collection Ready"
        print "\n\t--- Data Collection Stopped. Press \\ to continue ---\n"
        
        
        
        
def main():
    root = Tk()
    root.geometry("600x600+200+200")
    app = GUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_it)
    root.mainloop()	


if __name__ == '__main__':
    main()