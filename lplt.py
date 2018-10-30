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


def get_data(name):

    data = {}
    os.chdir(name)

    for folder in os.listdir():
        if not folder == '.gitignore':
            data.update({folder: []})

            for shot in os.listdir(folder):
                data[folder].append(np.ndfromtxt(
                    folder + '/' + shot, delimiter='\t'))
    return data


def butter_filter(data, order, cutoff):

    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')

    correct = 1  # 0.004 # Is this value necessary?

    for key in data.keys():
        buttered.update({key: []})

        for shot in data[key]:
            V = np.sqrt(shot[:][:, 1]**2)
            corrected = correct * signal.sosfiltfilt(sos, V)
            buttered[key].append(corrected)

    return buttered


def butter_avg(buttered):

    avg = {}

    for key in buttered.keys():
        avg.update({key: (np.sum(buttered[key], axis=0) / len(buttered[key]))})

    return avg


def density(avg):

    temp_estimate = 10  # eV
    temp_eV = temp_estimate * 1.16E4
    boltz = 1.38E-23
    area_of_probe = 1.749E-5
    electron_charge = 1.602E-19
    mass = 6.67E-26

    const = 0.6 * electron_charge * area_of_probe * \
        np.sqrt(boltz * temp_eV / mass)

    density = {}
    time_axis = np.linspace(1, 10000, num=10000) / 10

    for key in avg.keys():
        density.update({key: avg[key] / const})

    return time_axis, density


if __name__ == 'main':
    print('Running lplt')
