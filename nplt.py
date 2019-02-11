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


def get_radial_position(file):

    # Pull out radial position from filename as a float.
    position_match = re.search('[0-9]?[0-9][.]?[0-9]?[0-9]?[ -]?[ ]?cm',file)

    if position_match == None:
        raise ValueError("\n\nFilename format is incorrect: %r" % file)

    position_string = bias_match.group()
    position_string = "".join(position_string.split())
    position_string = position_string[:-2]
    if position_string[-1] == '-':
        position_string = position_string[:-1]

    position = float(position_string)

    return position


def check_folders_in_directory(id_list):
    flag = False
    for folder in os.listdir():
        if folder[0] in id_list:
            flag = True
    if flag == False:
        raise ValueError("No folders in directory are named correctly: " +
                         "CHECK DIRECTORY")


def get_data(name):

    data = {}
    os.chdir(name)

    # id is L, R, D, or T (Left, Right, Double, or Triple)
    id_list = ['L','R','D','T']
    check_folders_in_directory(id_list)

    for id in id_list:
        for folder in os.listdir():
            if folder[0] == id:
                data[id] = {}
                for position_file in os.listdir(folder):
                    for shot_file in os.listdir(position_file):
                        position = get_radial_position(shot_file)
                        data[id][position] = {shot_file: np.ndfromtxt(
                                folder + '/' + position_file +'/' +
                                shot_file, delimiter='\t')}
    if data == {}:

    return data


def butter_filter(data, order, cutoff):
    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for id in data:
        buttered[id] = {}
        for position in data[id]:
            buttered[id][position] = {}
            for shot_file in data[id][position]:
                corrected = np.array(
                    signal.sosfiltfilt(sos, data[positon][shot_file][:, 1]))

                buttered[id][position][shot_file] = corrected
    return buttered


def butter_avg(buttered):

    avg = {}

    for id in buttered.keys():
        avg[id] = {}
        for position in buttered[id]:
            avg[id][position] = {}
            for shot_file in buttered[id][position]:
                length = len(buttered[id][position][shot_file])
                average_vals = (np.sum(
                        buttered[id][position][shot_file], axis=0) / length)

                avg[id][position] = average_vals

    return avg

def get_max_vals(avg):

    max_vals = {}

    for id in avg.keys():
        max_vals[id] = {}
        for position in avd[id]:
            max = np.absolute(np.amin(avg[id][position]))
            max_vals.[id][position] = max
    return max_vals

def Idensity(max_vals):

    area_of_probe = 1.2667686E-4 # m^2 = pi*[(12.7 mm)/2]^2
    shunt_resistance = 99.2    # Ohms

    const = area_of_probe * shunt_resistance

    Idensity = {}

    # Create a dictionary of radial position mapped to
    # max current density values.
    for id in max_vals.keys():
        Idensity[id] = {}
        for position in max_vals[id]:
            Idensity[id][position] = max_vals[position] / const
    return Idensity


if __name__ == 'main':
    print('Running nplt')
