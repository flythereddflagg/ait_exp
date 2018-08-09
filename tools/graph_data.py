import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_data(data_path):
    filename = data_path.split('\\')[-1]
    with open(data_path, 'r', newline='') as f:
        f.readline()
        run_info = f.readline()

    with open(data_path, 'r') as f:
        data = pd.read_csv(f, header=4)
    
    ignition_status = run_info.split(',')[7]
    if "N/A" in ignition_status: ignition_status = "No"
    elif ignition_status == "": ignition_status = "Unknown"
    
    time = np.array((data['time'] - data['time'][0]) / 1000 / 60)
    internal_temp = np.array(data['t4'])
    pressure = np.array(data['pressure'])
    test_temp = np.mean(internal_temp[:10])
    data_title = filename[:-4] + \
        " (Temp: {0:.2f} \u00B0C - {1} ignition)".format(
        test_temp, ignition_status)
    
    plt.clf()
    plt.subplot(211)
    plt.title(data_title)
    plt.plot(time, internal_temp)
    plt.ylabel('Temperature (\u00B0C)')
    plt.subplot(212)
    plt.plot(time, pressure, 'r')
    plt.xlabel('time (min)')
    plt.ylabel('Pressure (torr)')

    
def recurse_plot(path):
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename[-4:] != ".csv": continue
            print("Processing {}...".format(root + '\\' + filename))
            plot_data(root + '\\' + filename)
            plt.savefig(root + '\\' + filename[:-4] + '.png')

            
prompt = "\nEnter a '.csv' data path, r with a directory or q to quit\n ---> "
input_path = input(prompt)
while input_path != 'q':
    try:
        if input_path.split()[0] == 'r':
            recurse_plot(' '.join(input_path.split()[1:]))
        else:
            plot_data(input_path)
            plt.show()
    except Exception as e:
        print(e)
        print("Plot Generation Failed. Please try again.")
    input_path = input(prompt)
