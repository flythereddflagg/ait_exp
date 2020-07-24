import os
import tkinter as tk
from sys import argv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_data(data_path):
    filename = data_path.split('/')[-1]
    with open(data_path, 'r') as f:
        f.readline()
        run_info = f.readline()

    with open(data_path, 'r') as f:
        try:
            data = pd.read_csv(f, header=4)
        except Exception as e:
            print(f"File: {data_path}: {type(e)}: {e}")
            return
    
    print(data.keys())
    ignition_status = run_info.split(',')[5]
    if "N/A" in ignition_status: ignition_status = "No"
    elif ignition_status == "": ignition_status = "Unknown"
    
    times = np.array(data['time'])
    time_pts = np.array((times - times[0]) / 60)
    internal_temp = np.array(data['t4'])
    pressure = np.array(data['pressure'])
    test_temp = find_test_temp(time_pts, internal_temp)
    data_title = filename[:-4] + \
        " (Temp: {0:.2f} \u00B0C - {1} ignition)".format(
        test_temp, ignition_status)
    
    plt.clf()
    plt.subplot(211)
    plt.title(data_title)
    plt.plot(time_pts, internal_temp)
    plt.ylabel('Temperature (\u00B0C)')
    plt.subplot(212)
    plt.plot(time_pts, pressure, 'r')
    plt.xlabel('time (min)')
    plt.ylabel('Pressure (torr)')


def find_test_temp(time_data, temp_data):
    
    # for i in range(len(time_data)):
    #     dT_dt_test =    (temp_data[i] - temp_data[i+3])/\
    #                     (time_data[i] - time_data[i+3]) * 1000
    #     if dT_dt_test < -0.5 and i > 10:
    #         return np.mean(temp_data[i-10:i])
    return np.mean(temp_data[:10])

 
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
            input_path = tk.filedialog.askopenfilename(master=root)
            if not input_path: return
            plt.figure()
            plot_data(input_path)
            plt.show()
            plt.close('all')
        else:
            input_path = tk.filedialog.askdirectory(master=root)
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
        try:
            plot_data(filename)
        except Exception as e:
            print(f"File: {data_path}: {type(e)}: {e}")
            return
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
