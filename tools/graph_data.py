import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from sys import argv

def plot_data(data_path):
    #data_path = argv[1]
    with open(data_path, 'r') as f:
        data = pd.read_csv(f, header=4)

        
    time = np.array((data['time'] - data['time'][0]) / 1000 / 60)
    internal_temp = np.array(data['t4'])
    pressure = np.array(data['pressure'])
    plt.subplot(211)
    plt.plot(time, internal_temp)
    plt.xlabel('time (min)')
    plt.ylabel('Temperature (\u00B0C)')
    plt.subplot(212)
    plt.plot(time, pressure, 'r')
    plt.xlabel('time (min)')
    plt.ylabel('Gauge Pressure (torr)')

    plt.show()

input_path = input("Data path or q to quit\n ---> ")
while input_path != 'q':
    plot_data(input_path)
    input_path = input("Data path or q to quit\n ---> ")
