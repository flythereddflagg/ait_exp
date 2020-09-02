import os
import tkinter as tk
import tkinter.filedialog as fd
from sys import argv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_dataframe(data_path):

    
    with open(data_path, 'r') as f:
        f.readline()
        run_info = f.readline()
        headertxt = "time,t1,t2,t3,t4"

    header_row = 0
    with open(data_path, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if "time,t1,t2,t3,t4,pressure" in line:
                header_row = i
                break

    try:
        data = pd.read_csv(
            data_path, 
            header=header_row,
            index_col=False, 
            usecols=["time","t1","t2","t3","t4","pressure"]
        )
        return data, run_info
    except Exception as e:
        print(f"File: {data_path}: {type(e)}: {e}")
        return None, None

def plot_data(data_path):
    filename = data_path.split('/')[-1] 
    data, run_info = get_dataframe(data_path)
    
    assert data is not None and run_info is not None, "Data retrival failed."

    ignition_status = run_info.split(',')[5]
    if "N/A" in ignition_status: ignition_status = "No"
    elif ignition_status == "": ignition_status = "Unknown"

    times = np.array(data['time'])
    time_pts = (times - times[0]) / 60
    pressure = np.array(data['pressure'])
    test_temp, min_ = find_test_temp(time_pts, data)
    pm = test_temp - min_
    data_title = filename[:-4] + \
        f" (Temp: {test_temp:.2f} +/- {pm:.2f} \u00B0C - {ignition_status} ignition)"

    plt.clf()
    plt.subplot(211)
    plt.title(data_title)

    for label in data.keys():
        if "Unnamed" in label or\
            "time" in label or\
            "pressure" in label:
            continue
        
        temps = np.array(data[label])
        plt.plot(time_pts, temps, label=label)

    plt.ylabel('Temperature (\u00B0C)')
    plt.legend()
    plt.subplot(212)
    plt.plot(time_pts, pressure, 'r')
    plt.xlabel('time (min)')
    plt.ylabel('Pressure (torr)')


def find_test_temp(time_data, data):
    return np.mean(data['t4'][:10]), min([np.mean(data[f't{i+1}'][:10]) for i in range(4)])


def recurse_plot(path):
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if not filename.endswith(".csv"): continue
            print("Processing {}...".format(root + '/' + filename))
            try:
                plot_data(root + '/' + filename)
                plt.savefig(root + '/' + filename[:-4] + '.png')
            except Exception as e:
                print("Plot failed because:")
                print(e)
    plt.close('all')


def run_plot(file_, root, event=None):
    try:
        if file_:
            input_path = fd.askopenfilename(master=root)
            if not input_path: return
            plt.figure()
            plot_data(input_path)
            plt.show()
            plt.close('all')
        else:
            input_path = fd.askdirectory(master=root)
            if not input_path: return
            plt.figure()
            recurse_plot(input_path)
        print("DONE PROCESSING.")
    except Exception as e:
        print(type(e), e)
        print("Plot Generation Failed. Please try again.")


def main():
    root = tk.Tk()
    root.withdraw()
    if len(argv) < 2:
        filename = tk.filedialog.askopenfilename(parent=root)
        if not filename: return
        root.destroy()
        plot_data(filename)
        # try:
        #     plot_data(filename)
        # except Exception as e:
        #     print(f"File: {filename}: {type(e)}: {e}")
        #     return
        plt.show()
    elif argv[1] == '-r':
        dirname = tk.filedialog.askdirectory(parent=root)
        root.destroy()
        if not dirname: return
        for root, dirs, files in os.walk(dirname):
            for file_ in files:
                if file_.endswith(".csv"):
                    # try:
                    plot_data(root + "/" + file_)
                    # except Exception as e:
                    #     print(f"File: {root + '/' + file_}: {type(e)}: {e}")
                    #     continue
                    plt.savefig(root + "/" + file_[:-5] + '.png')
            break
    else:
        print("Error: Invalid argument.")
        root.destroy()


if __name__ == "__main__":
    main()
