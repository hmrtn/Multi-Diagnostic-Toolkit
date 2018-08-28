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

    if name in os.listdir():
        os.chdir(name)
    elif name not in os.listdir(): 
        os.chdir('..')
        os.chdir(name)
    else:
        print('FOLDER NOT FOUND')

    for folder in os.listdir():

        for shot in os.listdir(folder):
            data.update({shot:np.ndfromtxt(
                            folder+'/'+shot, delimiter = '\t')})
    return data


# This fucntion applies a Buttersworth Filter to the Raw data
def butter(data, order, cutoff):

    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for shot in sorted(data): # this sorts in decending order (i.e 0-10)
        corrected = np.array(signal.sosfiltfilt(sos, data[shot][:,1]))
        #corrected += np.mean(corrected[50:200])
        buttered.update({shot:[corrected]})
    return buttered


# means should only be used when finding mean of each plot in a given window
def means(buttered):

    butter_mean = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            butter_mean.update({key:[np.mean(shot[800:5000])]})
    return butter_mean

# this preforms a slice of time analysis to the buttered data
def time_slice(buttered, time):

    time *= 10
    slice = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            slice.update({key:[shot[time]]})
    return slice

# only call for debugging plots
def plot_dict(dict):

    plt.figure()
    for key in dict.keys():
        for value in dict[key]:
            plt.plot(value)
    plt.show()

# this function applies a median filter
def median_filter(dict, window):

    arr = []
    for key in dict.keys():
        for value in dict[key]:
            arr.append(value)
    med = signal.medfilt(arr, window)
    return med

# spline fits the data, best to leave as cubic (k=3)
def spline_fit(median, smooth, spline_num, rtrn=None):

    smooth = smooth * 1E-8
    x = np.linspace(0, len(median) - 1, len(median))
    splf = splrep(x, median, k = 3, s = smooth)
    xnew = np.linspace(0, len(median) - 1, spline_num)
    ynew = splev(xnew, splf)
    if rtrn is 'spline':
        return xnew, splf
    elif rtrn is 'xy':
        return xnew, ynew

# this takes the 1st derivative of of the spline
def ivdf(xnew, spl, window=9):

    yder = splev(xnew, spl, der=1)
    moving_avg = -np.convolve(yder,
                np.ones((window,))/window, mode = 'same')
    return xnew, moving_avg

if __name__ == '__main__':
    print("Running rplt")
