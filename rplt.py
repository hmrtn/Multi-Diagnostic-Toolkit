import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import signal
from scipy.signal import butter, lfilter
from scipy.stats import maxwell
from scipy.interpolate import CubicSpline, splev, splrep
from scipy import interpolate as inter


def get_data(name):

    data = {}
    os.chdir(name)

    for folder in os.listdir():
        if not folder == '.gitignore':

            for shot in os.listdir(folder):
                data.update({shot: np.ndfromtxt(
                    folder + '/' + shot, delimiter='\t')})
    return data


# This fucntion applies a Buttersworth Filter to the Raw data
def butter_filter(data, order, cutoff):

    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for shot in sorted(data):  # this sorts in decending order (i.e 0-10)
        corrected = np.array(signal.sosfiltfilt(sos, data[shot][:, 1]))
        buttered.update({shot: [corrected]})
    return buttered


# Means should only be used when finding mean of each plot in a given window
def means(buttered):

    butter_mean = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            butter_mean.update({key: [np.mean(shot[800:5000])]})
    return butter_mean


# This preforms a slice of time analysis to the buttered data
def time_slice(buttered, time):

    time *= 10
    slice = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            slice.update({key: [shot[time]]})
    return slice


# Only call for debugging plots
def plot_dict(dict):

    plt.figure()
    for key in dict.keys():
        for value in dict[key]:
            plt.plot(value)
    plt.show()

# This function applies a median filter
def median_filter(dict, window):

    arr = []
    for key in dict.keys():
        for value in dict[key]:
            arr.append(value)
    med = signal.medfilt(arr, window)
    return med


# Spline fits the data, best to leave as cubic (k=3)
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

def normalize(x):
    x = np.asarray(x)
    return (x - x.min()) / (np.ptp(x))
# Takes the 1st derivative of of the spline
def ivdf(xnew, spl, window=9):

    yder = splev(xnew, spl, der=1)
    moving_avg = -np.convolve(yder,
                              np.ones((window,)) / window, mode='same')
    return xnew, moving_avg


if __name__ == 'main':
    print('Running rplt')