from src import tada_ui, data_src
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import traceback
import os

root = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    with ThreadPoolExecutor() as _exec:
        try:
            tada = data_src.TADADataSource(
                comport='/dev/ttyACM0', 
                baudrate=9600
            )
            baro = data_src.BaroDataSource(
                comport="/dev/ttyS0", 
                baudrate=19200
            )
            ui = tada_ui.TaDaUI(
                layout_path=root+"/src/tada_ui.json", 
                save_as_exec=_exec,
                data_src=[tada, baro],
                log_path = root + "/../../data/experimental_log.csv",
                datadir = root + "/../../data"
            )
            ui.mainloop()
        except:
            track = traceback.format_exc()
            now = datetime.now()
            dt_string = now.strftime("%Y%m%d%H%M%S")
            log_file = root + f"/crash_report_{dt_string}.log"
            print(track)
            with open(log_file, 'w') as f:
                f.write(dt_string + '\n' + track)
            print(f'Errors written to: {log_file}')
            input("Press Enter to exit...")
            

