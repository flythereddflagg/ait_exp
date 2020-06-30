from .daq_ui import DataAquisitionUI, DummyDataSource
import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from random import uniform
from concurrent.futures import ThreadPoolExecutor
import traceback


class DummyBarometer(DummyDataSource):

    def get_data(self):
        return [uniform(630, 760)]



class TaDaUI(DataAquisitionUI):
    def __init__(
                self, 
                layout_path,
                save_as_exec,
                data_src = [DummyDataSource(), DummyBarometer()],
                vis_data = 100,
                log_path = "../experimental_log.csv",
                datadir  = "../"
            ):
        super().__init__(layout_path, data_src, vis_data)
        self.data = []
        self.current_time = 0
        self.start_time = 0
        self.pemergency = 206.86 # torr
        self.delta_t_tol = 1.0
        self.eq_tol = 0.2
        self.p_lower_limit = 758 # torr
        self.p_upper_limit = 762 # torr
        self.target_data_path = ""
        self.log_path = log_path
        self.arduino_timestamp = ""
        self.system_timestamp = ""
        self.data_labels = [
            key for key in self.ui_config['widgets'] \
            if 'label' in key
        ]
        self.data_fields = [
            self.widgets[key] for key in self.ui_config['widgets'] \
            if 'entry' in key
        ]
        self.setup_commands()
        self.widgets["message"]['text'] = "Data Collection Ready"
        self.save_as = False
        self.save_as_exec = save_as_exec
        self.save_as_task = None
        self.datadir = datadir


    def setup_commands(self):
        """Binds commands to keyboard and buttons."""
        self.bind("<Escape>", self.quit_app)
        self.bind("<Return>", self.start_stop)
        self.bind("<Control-s>", self.set_save_as)
        
        self.widgets["quit button"]['command'] = self.quit_app
        self.widgets["collect button"]['command'] = self.start_stop
        self.widgets["target file button"]['command'] = self.set_save_as
    
    
    def mainloop(self):
        """
        OVERRIDDEN FROM Tk
        Runs the mainloop for Tk with some modifications to allow
        concurrent running of the daq_loop and file_save_as methods.
        """
        while self.running:
            if self.save_as: self.run_save_as()
            self.update()
            self.daq_loop()


    def run_save_as(self):
        if not self.save_as_task:
            self.save_as_task = self.save_as_exec.submit(self.file_save_as)
        if self.save_as_task.done():
            self.target_data_path = self.save_as_task.result()
            self.widgets["file path"]['text'] = self.target_data_path
            self.save_as_task = None
            self.save_as = False
                    


    def daq_loop(self):
        data_point = []
        for src in self.data_src:
            data_point += src.get_data()

        if not self.valid_data(data_point): 
            self.after(0, self.daq_loop)
            return

        self.process_data(data_point)
        
        if self.collect: self.data_collect(data_point)

        self.graph_data(data_point)


    def set_save_as(self, event=None):
        self.save_as = True


    def valid_data(self, data_point):
        """
        OVERRIDDEN FROM PARENT
        Check that data is valid and do any preprocessing on the data.
        Must return True or False.
        """
        if type(data_point) == type('') and data_point[0] == '/': 
            print(data_point)
            return False
        else:
            print_out = ""
            for datum in data_point:
                print_out += f"{datum:7.2f}  "
            print(print_out[:-2])
            return True

    
    def process_data(self, data_point):
        """
        OVERRIDDEN FROM PARENT
        Do any processing needed before data collection and graphing.
        """
        self.current_time = data_point[0]
        self.temps = data_point[1:5]
        self.p_gauge, self.p_baro = data_point[5:]
        self.p_abs = self.p_gauge + self.p_baro
        self.update_temp_equilbrium()
        self.update_pressure()


    def data_collect(self, data_point):
        """
        OVERRIDDEN FROM PARENT
        Processing for data collection.
        """
        self.data.append(data_point)
        print("Data collected.")

        display_time = float(self.current_time - self.start_time)
        self.widgets['message']['text'] = \
            f"Collecting Data...\tTime (sec): {display_time:.1f}"


    def graph_data(self, data_point):
        new_data_point = [data for data in data_point[:-1]]
        new_data_point[-1] += data_point[-1]
        super().graph_data(new_data_point)


    def update_temp_equilbrium(self):
        """
        Calculates the absolute average deviation (AAD) fraction from t4 of 
        all other temperatures and, if that AAD% is < the equilibrium 
        tolerance (self.eq_tol) then it marks the temperatures as 
        ready. Not ready otherwise
        """
        t4 = self.temps[-1]
        ydata = self.lines[3].ydata
        try:
            aad_pct = sum(
                [abs(t4 - temp) for temp in self.temps]
                ) /len(self.temps) /t4
        except ZeroDivisionError as detail:
            print(detail)
            aad_pct = self.eq_tol + 2
        
        try:
            delta_temp = abs(ydata[0] - ydata[-1])
        except IndexError:
            delta_temp = 10 * self.delta_t_tol
        
        # if AAD < tol and Δt4 < ΔT_tol in last Δtime: ready to run
        if aad_pct < self.eq_tol and delta_temp < self.delta_t_tol:
            self.widgets["temp indicator"]['bg']   = '#80ff00'
            self.widgets["temp indicator"]['text'] = 'Temp Ready'
        else:
            self.widgets["temp indicator"]['bg']   = '#FFFF00'
            self.widgets["temp indicator"]['text'] = 'Temp NOT Ready'


    def update_pressure(self):
        """
        Updates the state of the pressure label to indicate if the 
        pressure is within acceptable parameters. Makes a warning sound if 
        pressure far exceeds acceptable parameters.
        """
        if self.p_abs < self.p_lower_limit:
            self.widgets["pressure indicator"]['bg'] = 'blue'
            self.widgets["pressure indicator"]['fg'] = 'white'
            state = " (low) "
        elif self.p_abs > self.p_upper_limit:
            self.widgets["pressure indicator"]['bg'] = '#cc0000'
            self.widgets["pressure indicator"]['fg'] = 'white'
            state = " (high)"
        else:
            self.widgets["pressure indicator"]['bg'] = '#80ff00'
            self.widgets["pressure indicator"]['fg'] = 'black'
            state = ""
        
        self.widgets["pressure indicator"]['text'] = \
                    f"P(abs): {self.p_abs:3.3f} torr{state}"
        
        if self.p_gauge > self.pemergency:
            self.msg_str = self.widgets["message"]['text']
            self.widgets["message"]['text'] = \
                "WARNING! SHUTDOWN NOW! Gauge Pressure > 4 psi!"
            self.widgets["message"]['bg'] = '#cc0000'
            self.widgets["message"]['fg'] = 'white'
            print("\a") # makes a noise to indicate a problem

    
    def start_stop(self, event=None):
        """ 
        The Start/Stop procedure. Once stopped the program will ask you 
        to choose a file to save to if you haven't already. Then it saves
        the file and resets the DAQ. If you cancel the save all your data 
        will be lost.
        """
        if self.collect == False: # this is the start branch
            self.start_time = self.current_time
            self.data_src[0].collect_data()
            self.collect = True
            self.widgets["message"]['text'] = "Collecting Data..."
            self.widgets["collect button"]['bg']   = 'red'
            self.widgets["collect button"]['fg']   = 'white'
            self.widgets["collect button"]['text'] = "Stop Collection"

        else: # this is the stop branch
            self.save_data()
            self.stop_reset()
            self.cleanup()

        
    def save_data(self):
        """ 
        The save data part of Start/Stop procedure. Once stopped the program 
        will ask you  to choose a file to save to if you haven't already. 
        Then it saves the file and resets the DAQ. If you cancel the save 
        all your data will be lost.
        """
        header_str = ','.join([
            self.ui_config['widgets'][key]['init']['text'] \
            for key in self.data_labels
        ])
        if not self.target_data_path:
            self.target_data_path = self.file_save_as()
            self.widgets["file path"]['text'] = self.target_data_path
            
        try:
            # see if the file exists
            open(self.target_data_path, 'r').close()
        except FileNotFoundError:
            # if file not found, create it
            open(self.target_data_path, 'w').close()
        
        # check the experiment log
        try:
            # see if the file exists
            open(self.log_path, 'r').close()
        except FileNotFoundError:
            # if file not found, create it
            with open(self.log_path, 'w') as f:
                f.write(f"file,{header_str}\n")
        
        text_out = self.format_data(self.data)
        data_name_out = self.get_data_fields()
        
        with open(self.log_path, 'a') as f:
            f.write(self.target_data_path.split('/')[-1])
            f.write(',')
            f.write(data_name_out)
            f.write("\n")

        with open(self.target_data_path, 'a') as f:
            f.write(header_str + '\n')
            f.write(data_name_out)
            f.write('\n')
            f.write(self.arduino_timestamp)
            f.write(self.system_timestamp)
            f.write('\n')
            f.write('time,t1,t2,t3,t4,pressure\n')
            f.write(text_out)
        
        self.cleanup()  
    
    
    def stop_reset(self):
        """ Resets the buttons and indicates Data collection is ready"""
        # tell the Arduino to stop writing its data to the SD card
        self.data_src[0].stop_collecting_data()
        for src in self.data_src:
            src.reset()
        self.collect = False
        self.widgets["collect button"]['bg'] = 'green'
        self.widgets["collect button"]['fg'] = 'black'
        self.widgets["collect button"]['text'] = 'Collect Data'
        self.widgets["message"]['text'] = "Data Collection Ready"
        print("\n\tData Collection Stopped. Resetting system...\n")

    
    def get_data_fields(self):
        """Returns the data from all data fields."""
        data_exp = [
            entry.get() for entry in self.data_fields
        ]
        
        for entry in self.data_fields:
            entry.delete(0, tk.END)
        
        datastring = ','.join(data_exp)
        return datastring

    
    def file_save_as(self, event=None):
        """ 
        Run save as dialog to choose target file. If an existing file is
        chosen the file is truncated and overwritten.
        """
        temp_root = tk.Tk()
        temp_root.withdraw()
        f = asksaveasfilename(
                parent = temp_root,
                initialdir = self.datadir,
                title = "Select Target File",
                filetypes = (
                    ("csv files","*.csv"),
                    ("all files","*.*")
                )
            )
        if not f: return
        if not f.endswith('.csv'): f += ".csv"
        return f

    
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



if __name__ == '__main__':
    with ThreadPoolExecutor() as _exec:
        try:
            TaDaUI("./tada_ui.json", _exec).mainloop()
        except:
            track = traceback.format_exc()
            print(track)
