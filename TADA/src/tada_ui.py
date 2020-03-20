from daq_ui import DataAquisitionUI, DummyDataSource


class TaDaUI(DataAquisitionUI):
    def __init__(
                self, 
                layout_path, 
                data_src=[DummyDataSource()],
                vis_data=100
            ):
        super().__init__(layout_path, data_src, vis_data)
        self.data = []
        self.current_time = 0
        self.start_time = 0

        self.setup_commands()
        


    def setup_commands(self):
    
        self.bind("<Escape>", self.quit_app)
        self.bind("<Return>", self.start_stop)
        self.bind("<Control-s>", self.file_save_as)
        self.widgets["target file button"]['command'] = self.file_save_as


    def valid_data(self, data_point):
        """
        Check that data is valid and do any preprocessing on the data.
        Must return True or False.
        """
        if type(data_point) == type('') and data_point[0] == '/': 
            print(data_point)
            return False
        else:
            print_out = ""
            for datum in data_point:
                print_out += f"{datum:6.2f}, "
            print(print_out[:-2])
            return True

    
    def process_data(data_point):
        """
        Do any processing needed before data collection and graphing.
        """
        self.current_time = data_point[0]


    def data_collect(data_point):
        self.data.append(data_point)
        print("Data collected.")

        display_time = float(data_point[0] - self.start_time)
        self.widgets['message']['text'] = \
            f"Collecting Data...\tTime (sec): {display_time:.1f}"


    def update_temp_equilbrium(self):
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
        
        # if AAD < tol and Δt4 < ΔT_tol over the last Δtime you are ready to run
        if aad_pct < self.eq_tol and delta_temp < self.delta_t_tol:
            self.eq_msg['bg']   = '#80ff00'
            self.eq_msg['text'] = 'Temp Ready'
        else:
            self.eq_msg['bg']   = '#FFFF00'
            self.eq_msg['text'] = 'Temp NOT Ready'


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
            state = " (low) "
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

       
    
    def start_stop(self, event=None):
        """ 
        The Start/Stop procedure. Once stopped the program will ask you 
        to choose a file to save to if you haven't already. Then it saves
        the file and resets the DAQ. If you cancel the save all your data 
        will be lost.
        """
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
            self.save_data()
            self.stop_reset()

        
    def save_data(self):
        """ 
        The save data part of Start/Stop procedure. Once stopped the program 
        will ask you  to choose a file to save to if you haven't already. 
        Then it saves the file and resets the DAQ. If you cancel the save 
        all your data will be lost.
        """
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
            f.write("file," + ','.join(self.data_labels) + '\n')
            f.close()
        
        text_out = self.format_data(self.data)
        data_name_out = self.get_data_fields()
        
        with open(self.log_path, 'a') as f:
            f.write("\n")
            f.write(self.target_data_path.split('/')[-1])
            f.write(',')
            f.write(data_name_out)

        with open(self.target_data_path,'a') as f:
            f.write(','.join(self.data_labels) + '\n')
            f.write(data_name_out)
            f.write('\n')
            f.write(self.arduino_timestamp)
            f.write(self.system_timestamp)
            f.write('\n')
            f.write('time,t1,t2,t3,t4,pressure\n')
            f.write(text_out)    
    
    
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

    
    def get_data_fields(self):
        """
        Returns the data from all data fields
        """
        data_exp = [
            self.data_fields[label][1].get() for label in self.data_labels
        ]
        
        for label in self.data_labels:
            self.data_fields[label][1].delete(0, END)
        
        datastring = ','.join(data_exp)
        return datastring



if __name__ == '__main__':
    TaDaUI("./tada_ui.json").mainloop()