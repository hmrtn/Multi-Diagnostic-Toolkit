"""Power Plotting Module

This module contains the functions used to plot input current, voltage, 
and power for a single data trial for the electric propulsion systems in the 
Advanced Propulsion Laboratory at the University of Washington.
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, integrate
from scipy.signal import butter, lfilter
from scipy.stats import maxwell
from scipy.interpolate import CubicSpline, splev, splrep
from scipy import interpolate as inter
import re

from PyQt5.QtWidgets import QCheckBox

def get_channel_name(filename):

    # Pull out channel name identifier from filename.
    channel_name_match = re.search('CH[1-4]',filename)

    if channel_name_match == None:
        raise ValueError("Filename format is incorrect: %r" % filename)

    channel_name = channel_name_match.group()

    return channel_name



def get_data(name, energy_bool):
    data = {}
    os.chdir(name)
    dir = os.listdir()
    try:
        for file in dir:
            filename_length = len(file)
            file_extension = file[-4:filename_length]
            if (file_extension == '.csv'
                    or  file_extension == '.CSV'):

                channel_name = get_channel_name(file)
                all_data = pd.read_csv(file, header=None)

                df1 = all_data.iloc[:,3]
                df2 = all_data.iloc[:,4]

                # convert to numpy array
                if channel_name == 'CH1':
                    time_data = df1.values
                    voltage_data = df2.values
                elif channel_name == 'CH3':
                    current_data = df2.values
                else:
                    pass
                try:
                    data['time'] = time_data
                    data['voltage'] = voltage_data * 100 # V/V scaling factor
                    data['current'] = current_data * 2 # A/V scaling factor
                    data['power'] = data['voltage'] * data['current'] # W

                    if energy_bool:
                        data['energy'] = integrate.cumtrapz(data['power'], data['time'], initial=0) # J
                except:
                    pass
    except:
        pass
    return data



if __name__ == 'main':
    print('Running pplt')
