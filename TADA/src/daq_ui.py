from ui import UserInterface
from matplotlib import use, lines as mlplines
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from random import random, uniform
from time import sleep, time



class DataAquisitionUI(UserInterface):
    def __init__(self, layout_path, plt_path):
        super().__init__(layout_path)
        # setup constants
        self.running=True
        self.collect = False
        self.vis_data = 100
        self.plt_config = self.dict_from_jsonfile(plt_path)
        self.time = time()


        self.init_plot()
        self.clean_up()
        self.daq_loop()


    def init_plot(self):
        """
        Sets up plot with colors and sizing formats.
        """
        # color the background black
        self.figure, self.ax = subplots(facecolor='black')
        self.lines = [
            self.ax.add_line(
                mlplines.Line2D(
                    [], [], 
                    label=label,
                    **vals
                )
            ) for label, vals in self.plt_config['lines'].items() \
                if label != "Pressure"
        ]
        self.pax = self.ax.twinx()        
        self.lines.append(
            self.pax.add_line(
                mlplines.Line2D(
                    [], [], 
                    label="Pressure",
                    **self.plt_config['lines']["Pressure"]
                )
            )
        )
        for line in self.lines:
            line.xdata = []
            line.ydata = []
        self.ax.legend(self.lines, [l.get_label() for l in self.lines], loc='upper right')
        self.ax.set_ylabel("Temperature (°C)")
        self.pax.set_ylabel('Pressure (torr)')
        self.ax.set_xlabel("Time (ms)")

        for ax in [self.ax, self.pax]:
            ax.set_facecolor('black')
            # color the foreground white
            for side in ['bottom', 'top', 'right', 'left']:
                ax.spines[side].set_color('white')
            
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.grid(color='white')
            
            
            # set up the interactive plot
            ax.set_autoscaley_on(True)
            ax.set_autoscalex_on(True)
        # Get rid of extra space and turn on interactive mode
        tight_layout()
        ion()
        # Embed plot in a canvas to be placed in the window
        self.data_plot = FigureCanvasTkAgg(
                            self.figure, 
                            master=self
                        ).get_tk_widget()
        # Color the canvas black
        self.data_plot.configure(bg='black')
        # place plot on grid
        self.data_plot.grid(row=4, column=0, columnspan=8, sticky="nsew")

        



    def clean_up(self):
        """ 
        Re-initializes the parameters for data collection and clears the 
        console screen.
        """
        for line in self.lines:
            line.xdata = []
            line.ydata = []
        self.data = []


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
        for i, line in enumerate(self.lines):
            if len(line.xdata) > self.vis_data and len(line.ydata) > self.vis_data:
                line.xdata.pop(0)
                line.ydata.pop(0)
                
            line.xdata.append(data1[0])
            line.ydata.append(data1[i+1])
            # Update data (with the new and the old points)
            line.set_xdata(line.xdata)
            line.set_ydata(line.ydata)
            
        # Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        self.pax.relim()
        self.pax.autoscale_view()
        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    
    
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
                random(),
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
        




if __name__ == "__main__":
    DataAquisitionUI("./tada_ui.json", "./plot_config.json").mainloop()
