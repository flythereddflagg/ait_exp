from .ui import UserInterface
from tkinter.messagebox import askyesno
from matplotlib import use, lines as mlplines
from matplotlib.pyplot import subplots, ion, tight_layout
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as PltCanvas
use('TkAgg')

from random import random, uniform
from time import sleep, time



class DummyDataSource():
    def __init__(self):
        self.time = time()


    def get_data(self):
        return [(time() - self.time),
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
                data_src=[DummyDataSource()],
                vis_data=100
            ):
        super().__init__(layout_path)
        self.plt_config = self.ui_config['plot config']
        self.running=True
        self.collect = False
        self.vis_data = vis_data
        self.data_src = data_src
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.init_plot()
        self.cleanup()


    def init_plot(self):
        """
        Sets up plot with colors and formats. Turns on
        interactive mode and places the plot in the 
        grid of the parent.
        """
        pltconf = self.plt_config["global config"]
        bg_color, fg_color = pltconf['bg'], pltconf['fg']

        self.figure, self.ax1 = subplots(facecolor=bg_color)
        self.ax2 = self.ax1.twinx()
        self.ax1.set_xlabel(pltconf['x label'])
        self.ax1.set_ylabel(pltconf['y1 label'])
        self.ax2.set_ylabel(pltconf['y2 label'])

        self.lines = [self.ax1.add_line(
                mlplines.Line2D([], [], label=label, **vals)
            ) for label, vals in self.plt_config['lines axis 1'].items()
        ]
        self.lines += [self.ax2.add_line(
                mlplines.Line2D([], [], label=label, **vals)
            ) for label, vals in self.plt_config['lines axis 2'].items()
        ]

        for line in self.lines:
            line.xdata, line.ydata = [], []
        
        labels = [l.get_label() for l in self.lines]
        legend = self.ax2.legend(
                self.lines, labels, 
                loc='upper left',
                facecolor=bg_color,
                edgecolor=bg_color,
                framealpha=1.0
            )
        for text in legend.get_texts():
            text.set_color(fg_color)
        
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
        self.data_plot = PltCanvas(self.figure, master=self).get_tk_widget()
        self.data_plot.grid(**pltconf['grid'])


    def cleanup(self):
        """ 
        Re-initializes the parameters for data collection and clears the 
        console screen.
        """
        for line in self.lines:
            line.xdata = []
            line.ydata = []
        self.data = []
    
    
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
        data_point = []
        for src in self.data_src:
            data_point += src.get_data()

        if not self.valid_data(data_point): 
            self.after(0, self.daq_loop)
            return

        self.process_data(data_point)
        
        if self.collect: self.data_collect(data_point)

        self.graph_data(data_point)
        if self.running: self.after(0, self.daq_loop)


    def graph_data(self, data1):
        """ Update the data to be graphed and then update the graph """
        for i, line in enumerate(self.lines):
            assert len(line.xdata) == len(line.ydata)
            if len(line.xdata) > self.vis_data:
                line.xdata.pop(0)
                line.ydata.pop(0)
                
            line.xdata.append(data1[0])
            line.ydata.append(data1[i+1])
            line.set_xdata(line.xdata)
            line.set_ydata(line.ydata)
            
        self.ax1.relim()
        self.ax2.relim()
        self.ax1.autoscale_view()
        self.ax2.autoscale_view()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    def valid_data(self, data_point):
        """
        Check that data is valid and do any preprocessing on the data.
        Must return True or False.
        """
        print(data_point)
        return True 

    
    def process_data(self, data_point):
        """
        Do any processing needed before data collection and graphing.
        """
        pass


    def data_collect(data_point):
        """
        Processing for data collection.
        """
        pass


    def quit_app(self, event=None):
        """Safely exits the program."""
        if self.collect:
            if not askyesno(
                    "Quit Warning",
                    "DAQ is still running!\nAre you sure you want to quit?"
                ):
                return
        self.running = False
        self.destroy()
        raise SystemExit



if __name__ == "__main__":
    ui = DataAquisitionUI("./tada_ui.json")
    ui.after(0, ui.daq_loop)
    ui.mainloop()
