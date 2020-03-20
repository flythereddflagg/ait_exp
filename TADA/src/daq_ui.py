from ui import UserInterface
from matplotlib import use, lines as mlplines
use('TkAgg')
from matplotlib.pyplot import subplots, ion, tight_layout
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from random import random, uniform
from time import sleep, time



class DummyDataSource():
    def __init__(self):
        self.time = time()


    def get_data(self):
        return [(time() - self.time) * 1000,
            random(),
            random(),
            random(),
            random(),
            uniform(0, 200)
        ]



class DataAquisitionUI(UserInterface):
    def __init__(
                self, 
                layout_path, 
                plt_path, 
                data_src=[DummyDataSource()],
                vis_data=100):
        super().__init__(layout_path)
        self.plt_config = self.dict_from_jsonfile(plt_path)
        self.running=True
        self.collect = False
        self.vis_data = vis_data
        self.data_src = data_src
        self.protocol("WM_DELETE_WINDOW", self.quit_app)


        self.init_plot()
        self.clean_up()
        self.daq_loop()


    def init_plot(self):
        """
        Sets up plot with colors and formats. Turns on
        interactive mode and places the plot in the 
        grid of the parent.
        """
        pltconf = self.plt_config["global config"]
        bg_color = pltconf['bg']
        fg_color = pltconf['fg']

        self.figure, self.ax1 = subplots(facecolor=bg_color)
        self.ax2 = self.ax1.twinx()
        self.ax1.set_xlabel(pltconf['x label'])
        self.ax1.set_ylabel(pltconf['y1 label'])
        self.ax2.set_ylabel(pltconf['y2 label'])

        self.lines = [
            self.ax1.add_line(
                mlplines.Line2D(
                    [], [], 
                    label=label,
                    **vals
                )
            ) for label, vals in self.plt_config['lines axis 1'].items()
        ]
        self.lines += [
            self.ax2.add_line(
                mlplines.Line2D(
                    [], [], 
                    label=label,
                    **vals
                )
            ) for label, vals in self.plt_config['lines axis 2'].items()
        ]
        for line in self.lines:
            line.xdata = []
            line.ydata = []
        self.ax1.legend(
                        self.lines, 
                        [l.get_label() for l in self.lines], 
                        loc='upper right'
                    )
        
        for axis in [self.ax1, self.ax2]:
            axis.set_facecolor(bg_color)
            for side in ['bottom', 'top', 'right', 'left']:
                axis.spines[side].set_color(fg_color)
            
            axis.tick_params(axis='x', colors=fg_color)
            axis.tick_params(axis='y', colors=fg_color)
            axis.yaxis.label.set_color(fg_color)
            axis.xaxis.label.set_color(fg_color)
            axis.grid(color=fg_color)
            axis.set_autoscaley_on(True)
            axis.set_autoscalex_on(True)

        tight_layout()
        ion()
        self.data_plot = FigureCanvasTkAgg(
                                        self.figure, 
                                        master=self
                                    ).get_tk_widget()
        self.data_plot.grid(**pltconf['grid'])


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
        all other temperatures and, if that AAD% is < the equilibrium 
        tolerance (self.eq_tol) then it marks the temperatures as 
        ready. Not ready otherwise
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
            if len(line.xdata) > self.vis_data and \
                    len(line.ydata) > self.vis_data:
                line.xdata.pop(0)
                line.ydata.pop(0)
                
            line.xdata.append(data1[0])
            line.ydata.append(data1[i+1])
            # Update data (with the new and the old points)
            line.set_xdata(line.xdata)
            line.set_ydata(line.ydata)
            
        # Need both of these in order to rescale
        self.ax1.relim()
        self.ax2.relim()
        self.ax1.autoscale_view()
        self.ax2.autoscale_view()
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
            data_point = []    # get data
            for src in self.data_src:
                data_point += src.get_data()

            print(data_point)
            if type(data_point) == type('') and\
                data_point[0] == '/': continue
            
            self.current_time = data_point[0]
            if self.collect == True:
                self.data.append(data_point)# save data to array
                print("Data collected.")
                
                display_time = float(data_point[0] - self.start_time)/1000
                self.msg1['text'] = "Collecting Data...\tTime"\
                                    " (sec): {:.1f}".format(display_time)

            self.graph_data(data_point)     # put the data on a graph


    def quit_app(self):
        self.running = False
        self.destroy()
        raise SystemExit





if __name__ == "__main__":
    DataAquisitionUI("./tada_ui.json", "./plot_config.json").mainloop()
