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

    # if name in os.listdir():
    #     os.chdir(name)
    # elif name not in os.listdir(): 
    #     os.chdir('..')
    #     os.chdir(name)
    # else:
    #     print('FOLDER NOT FOUND')
    #os.chdir(name)

    data.update({name:np.ndfromtxt(
                            name, delimiter = '\t')})
    
    # for folder in os.listdir():

    #     for shot in os.listdir(folder):
    #         data.update({shot:np.ndfromtxt(
    #                         folder+'/'+shot, delimiter = '\t')})
    return data

def butter(data, order, cutoff):
    buttered = {}
    sos = signal.butter(order, cutoff, btype='low', analog=False, output='sos')
    for shot in sorted(data): # this sorts in decending order (i.e 0-10)
        corrected = np.array(signal.sosfiltfilt(sos, data[shot][:,1]))
        #corrected += np.mean(corrected[50:200])
        buttered.update({shot:[corrected]})
    return buttered

def means(buttered):

    butter_mean = {}
    for key in buttered.keys():
        for shot in buttered[key]:
            butter_mean.update({key:[np.mean(shot[800:5000])]})
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
    splf = splrep(x, median, k = 3, s = smooth)
    xnew = np.linspace(0, len(median) - 1, spline_num)
    ynew = splev(xnew, splf)
    if rtrn is 'spline':
        return xnew, splf
    elif rtrn is 'xy':
        return xnew, ynew

def plot_dict(dict):

    #plt.figure()
    for key in dict.keys():
        for value in dict[key]:
            plt.plot(value)
    #plt.show()