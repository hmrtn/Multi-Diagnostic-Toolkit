import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import butter, lfilter
from scipy.stats import maxwell
from scipy.interpolate import CubicSpline, splev, splrep
from scipy import interpolate as inter

from PyQt5.QtWidgets import QCheckBox


def check_filename(filename):
    # Check if the filename is in the correct format
    #('Shot#XXXX_test - [num]V bias.txt'), where XXXX is the 4-digit shot
    # identifier and [num] is the value of the bias potential. If format
    # is correct, return bias potential value. Otherwise, raise a ValueError.
    if (filename[0:5] != 'Shot#' or
            filename[9:17] != '_test - ' or
            filename[-10:] != 'V bias.txt'):
        raise ValueError("Filename format is incorrect: %r" % filename)
    return None


def get_bias_potential(file):

    check_filename(file)

    # Pull out bias voltage from filename as a float.
    bias = file[16:-10].strip()
    bias = float(bias)

    return bias


def get_data(name):

    data = {}
    os.chdir(name)

    for shot in os.listdir():
        bias = get_bias_potential(shot)

        data[bias] = np.ndfromtxt(
            shot, delimiter='\t')

    return data


def butter_filter(data, order, cutoff):
    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for bias in data:
        corrected = np.array(signal.sosfiltfilt(sos, data[bias][:, 1]))
        buttered[bias] = corrected
    return buttered


def get_max_vals(buttered):

    max_vals = {}

    for bias in buttered.keys():
        max = np.absolute(np.amin(buttered[bias]))
        max_vals[bias] = max
    return max_vals




def Idensity(max_vals):

    area_of_probe = 1.2667686E-4 # m^2 = pi*[(12.7 mm)/2]^2
    shunt_resistance = 99.2    # Ohms

    const = area_of_probe * shunt_resistance

    Idensity = {}

    # Create a dictionary of bias voltages mapped to max current density values.
    for bias in max_vals.keys():
        Idensity[bias] = max_vals[bias] / const
    return Idensity


if __name__ == 'main':
    print('Running biasplt')
