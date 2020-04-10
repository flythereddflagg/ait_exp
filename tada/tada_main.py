from src import tada_ui, data_src
from concurrent.futures import ThreadPoolExecutor
import traceback

if __name__ == '__main__':
    with ThreadPoolExecutor() as _exec:
        try:
            tada = data_src.TADADataSource(
                comport='/dev/ttyACM0', 
                baudrate=9600
            )
            baro = data_src.SerialDataSource(
                comport="/dev/ttyS0", 
                baudrate=19200
            )
            ui = tada_ui.TaDaUI(
                layout_path="./src/tada_ui.json", 
                save_as_exec=_exec,
                data_src=[tada, baro]
            )
            ui.mainloop()
        except:
            track = traceback.format_exc()
            print(track)
