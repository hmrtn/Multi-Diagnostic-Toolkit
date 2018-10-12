import sys
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy import signal
from scipy.signal import butter, lfilter
from scipy.stats import maxwell
from scipy.interpolate import CubicSpline, splev, splrep
from scipy import interpolate as inter


def get_data(name):

    data = {}
    data.update({name: np.ndfromtxt(name, delimiter='\t')})
    return data


def butter_filter(data, order, cutoff):
    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for shot in data:  # this sorts in decending order (i.e 0-10)
        corrected = np.array(signal.sosfiltfilt(sos, data[shot][:, 1]))
        buttered.update({shot: [corrected]})
    return buttered


def means(buttered):

    butter_mean = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            butter_mean.update({key: [np.mean(shot[800:5000])]})
    return butter_mean


def median_filter(dict, window):

    arr = []
    for key in dict.keys():
        for value in dict[key]:
            arr.append(value)
    med = signal.medfilt(arr, window)
    return med


def spline_fit(median, smooth, spline_num, rtrn=None):

    smooth = smooth * 1E-8
    x = np.linspace(0, len(median) - 1, len(median))
    splf = splrep(x, median, k=3, s=smooth)
    xnew = np.linspace(0, len(median) - 1, spline_num)
    ynew = splev(xnew, splf)
    if rtrn is 'spline':
        return xnew, splf
    elif rtrn is 'xy':
        return xnew, ynew


def plot_dict(dic):

    plt.figure()
    plt.minorticks_on()
    plt.grid(which='major', alpha=0.5)
    plt.grid(which='minor', alpha=0.2)
    for k,v in dic.items():
        plt.plot(v)
    plt.show()


if __name__ == 'main':
    print('Running splt')
