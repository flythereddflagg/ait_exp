from src import tada_ui, data_src
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import traceback
import os

DEMO = False
ROOT = os.path.dirname(os.path.abspath(__file__))
LAYOUT = ROOT + "/data/tada_ui.json"
LOG_PATH = ROOT + "/../../data/experimental_log.csv"
DATADIR = ROOT + "/../../data"
ARDUINO_COMPORT, ARDUINO_BAUDRATE = '/dev/ttyACM0', 9600
RS232_COMPORT, RS232_BAUDRATE = "/dev/ttyS0", 19200


if __name__ == '__main__':
    with ThreadPoolExecutor() as _exec:
        try:
            if not DEMO:
                tada = data_src.TADADataSource(
                    comport = ARDUINO_COMPORT, 
                    baudrate = ARDUINO_BAUDRATE
                )
                baro = data_src.BaroDataSource(
                    comport = RS232_COMPORT, 
                    baudrate = RS232_BAUDRATE
                )
                ui = tada_ui.TaDaUI(
                    layout_path=LAYOUT, 
                    save_as_exec = _exec,
                    data_src = [tada, baro],
                    log_path = LOG_PATH,
                    datadir = DATADIR
                )
            else:
                ui = tada_ui.TaDaUI(
                    layout_path = LAYOUT,
                    save_as_exec=_exec,
                    log_path = LOG_PATH,
                    datadir = DATADIR
                )

            ui.mainloop()
        except:
            track = traceback.format_exc()
            now = datetime.now()
            dt_string = now.strftime("%Y%m%d%H%M%S")
            log_file = ROOT + f"/logs/crash_report_{dt_string}.log"
            print(track)
            with open(log_file, 'w') as f:
                f.write(dt_string + '\n' + track)
            print(f'Errors written to: {log_file}')
            input("Press Enter to exit...")
            

