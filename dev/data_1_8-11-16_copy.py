#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: Mark Redd
"""
from random import randint
from Tkinter import Tk, Frame, BOTH, TOP

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

import time


class GUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.data = [[0,0,0,0,0]]
        self.running = False
        self.start_time = 0
        self.min_x = 0
        self.max_x = 10
        self.xdata = []
        self.ydata = []
        self.initUI()

        
    def initUI(self):
        #os.system("cls")
        self.parent.title("A NEW THING!")
        self.parent.bind("<Escape>", lambda self: self.widget.quit())
        self.parent.bind("<\>", self.start)
        self.parent.bind("<=>", self.stop)
        
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
       
        
    def loop(self):
        if self.running == False:
            return
        print "Getting data...",
            
        data1 = self.get_data()           # get data
        print data1
        self.data.append(data1)         # save data to array
        self.xdata.append(data1[0])
        self.ydata.append(data1[4])
        self.on_running(self.xdata, self.ydata)
        
        self.parent.after(500, self.loop) # loop
    
    def get_data(self):
        now = round(time.time() - self.start_time, 1)
        return [now, randint(1,5),randint(1,5),randint(1,5),randint(1,5)]
        
    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
        #...

    def on_running(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def run(self):
        self.on_launch()
        xdata = []
        ydata = []
        for x in np.arange(0,10,0.5):
            xdata.append(x)
            ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))
            self.on_running(xdata, ydata)
        return xdata, ydata

    def start(self, event): 
        if self.running == False:
            self.running = True
            #os.system("cls")
            self.start_time = time.time()
            self.loop()
        else:
            self.running = False
            print "\n\t--- Paused. Press \\ to continue ---\n"
            
    def stop(self, event): 
        self.running = False
        print "\n\t--- Stopped. Press \\ to continue ---\n"


def main():
    root = Tk()
    root.geometry("500x400+400+200")
    app = GUI(root)
    root.mainloop()	


if __name__ == '__main__':
    main()