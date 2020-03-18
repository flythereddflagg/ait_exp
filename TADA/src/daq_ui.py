from ui import UserInterface
from matplotlib import use
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from random import random, uniform
from time import sleep, time



class DataAquisitionUI(UserInterface):
    def __init__(self, layout_path):
        super().__init__(layout_path)
        self.running=True
        self.collect = False
        self.vis_data = 100
        self.time = time()
        # run the main loop program
        self.init_plot()
        self.clean_up()
        self.daq_loop()

    def clean_up(self):
        """ 
        Re-initializes the parameters for data collection and clears the 
        console screen.
        """
        self.xdata = []
        self.ydata = []
        self.data = []
    

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
        self.data_plot.configure(bg='black')

        self.data_plot.grid(row=4, column=0, columnspan=8, sticky="nsew")


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
            # data_point = self.ser.get_data()    # get data
            data_point = [(time() - self.time) * 1000,
                random()*1000,
                random(),
                random(),
                random(),
                uniform(0, 200)
            ]
            print(data_point)
            if type(data_point) == type('') and data_point[0] == '/':
                continue
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




if __name__ == "__main__":
    DataAquisitionUI("./tada_ui.json").mainloop()
