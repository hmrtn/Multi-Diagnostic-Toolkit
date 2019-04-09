"""DBD Langmuir Data Plotting Module

This module contains the functions used to plot the IV trace from a
langmuir probe given a sweeping set of bias potentials.
"""

__author__ = 'Kaito Durkee'
__contributors__ = ['Andrew Kullman']

import sys
import os
import numpy as np
import math as m
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.constants as const
import scipy.interpolate as interpolate
import pandas as pd
from scipy import stats as st
from scipy import signal
from scipy.signal import butter, lfilter, find_peaks
from scipy.stats import maxwell
from scipy.interpolate import CubicSpline, splev, splrep
from scipy import interpolate as inter
from decimal import Decimal

from PyQt5.QtWidgets import QCheckBox

from ErrorClasses import FileError

# System correction factor to convert voltages to currents
CORRECTION_FACTOR = 0.004 # A/V

def get_data(name):
    data = {}
    os.chdir(name)
    dir = os.listdir()
    for folder in dir:
        folder_name_length = len(folder)
        if folder != '.gitignore':
            if folder[-4:folder_name_length] != '.txt':
                try:
                    for file in os.listdir(folder):
                        filename_length = len(file)
                        if (file[-4:filename_length] == '.csv'
                                or  file[-4:filename_length] == '.CSV'):

                            all_data = pd.read_csv(
                                    folder + '/' + file, header=None)

                            # Why are we starting at index 290 and not index 0?
                            df = all_data.iloc[290:,4]
                            # Shouldn't the data in range(1, 291) be averaged
                            # and subtracted out, since the high voltage was off
                            # and the remaining signal is just system-level
                            # noise?

                            # convert to numpy array
                            current_data = df.values

                            try:
                                data[file] = current_data
                            except:
                                pass
                except:
                    pass
            elif folder[-4:folder_name_length] == '.txt':
                try:
                    df = pd.read_csv(folder, header=None)
                    bias_data = df.values
                except:
                    try:
                        bias_data = np.ndfromtxt(
                                folder,
                                delimiter=None,
                                encoding="utf8")
                    except:
                        try:
                            bias_data = np.ndfromtxt(
                                    folder,
                                    delimiter=',',
                                    encoding="utf8")
                        except:
                            pass
    try:
        # Remove all NaN values.
        bias_data_no_NaN = bias_data[~np.isnan(bias_data)]

        # Remove duplicate bias_data values, sorts
        # from closest to farthest from negative infinity, and
        # forms the result as a column vector.
        u = np.unique(bias_data_no_NaN)
        bias_data_out = np.vstack(u)
    except UnboundLocalError:
        message = ("Bias potentials text file could not be found:"
                + "CHECK DIRECTORY")
        raise FileError(message)

    return [data, bias_data_out]


def get_peak_vals(raw_current_data, bias_data):

    peak_current_data_dic = {}
    if (bias_data[:,0] == 0).any() == True:
        num_biases = len(bias_data) - 1
    else:
        num_biases = len(bias_data)

    for key in raw_current_data:
        # Make all values positive -- why are we doing this?
        abs_val_raw_current_data = np.absolute(raw_current_data[key])

        length_current_data = len(abs_val_raw_current_data)

        cutoff_index = (length_current_data-1)/num_biases
        peak_current_data = np.zeros((num_biases,1))
        for j in range(0,num_biases):
            temp = []
            starting_index = int(np.floor(j*cutoff_index))
            for i in range(starting_index, length_current_data):
                # For each bias category, collect current values in a temp list
                if (i >= j*cutoff_index) and (i < (j+1)*cutoff_index):
                    temp.append(abs_val_raw_current_data[i])
                if (i == length_current_data-1) and ((j+1) == num_biases):
                    # Categorize the very last data point in
                    # abs_val_raw_current_data
                    temp.append(abs_val_raw_current_data[-1])
                if i > (j+1)*cutoff_index:
                    break
            # Finds the peak current values in the temp list and
            # stores in the avg_peak_current_data list, in volts
            _, temp_peak_dic = find_peaks(temp,
                    height=np.mean(temp)*2)
            peaks = temp_peak_dic['peak_heights']
            peak_current_data[j] = np.max(peaks)

        peak_current_data_dic[key] = np.array(peak_current_data)

    return peak_current_data_dic


def peak_avg(peak_current_data_dic, bias_data):

    avg_peak_vals =  np.zeros_like(bias_data)

    start_num = 0
    if (bias_data[:,0] == 0).any() == True:
        end_num = len(bias_data) - 1
    else:
        end_num = len(bias_data)

    for index in range(start_num, end_num):
        temp = []
        for key in peak_current_data_dic:
            temp.append(peak_current_data_dic[key][index])
        # Convert mean voltage value into current, in microamperes
        if (bias_data[:,0] == 0).any() == True:
            new_index = index + 1
        else:
            new_index = index

        avg_peak_vals[new_index] = (np.mean(temp)
                * CORRECTION_FACTOR * 1E6)

    return avg_peak_vals


def aggregate_data(bias_data, avg_peak_current_data):
    # combine the data in bias_data and avg_peak_current_data
    # into one numpy array
    data = np.concatenate((bias_data, avg_peak_current_data), axis=1)
    return data


def create_full_dataset(data):

    try:
        # Ensure current is 0 uA when bias is 0 V
        data[data[:,0]==0,1] = 0
    except:
        pass

    neg_and_flip_data = -np.flipud(data)
    biases_contain_zero = (data[:,0] == 0).any()
    bias_length = len(data[:,0])

    if ((data[:,0] < 0).any() == True):
        if ((data[:,0] > 0).any() == True):
            if biases_contain_zero == True:
                # Assume user has specified all bias potentials to be analyzed
                full_dataset = data
            else:
                # Assume user has specified all bias potentials to be analyzed,
                # except for the 0 V bias
                index = 0
                full_dataset = np.zeros(bias_length+1,2)
                for i in range(0, bias_length):
                    if i == 0 and data(i,0) > 0:
                        data = neg_and_flip_data

                    if data(i,0) < 0:
                        full_dataset[index,:] = data[i,:]
                        index += 1
                    elif data(i,0) > 0:
                        if data(i-1,0) < 0:
                            zero_array = np.array([[0, 0]])
                            full_dataset[index,:] = zero_array
                            index += 1

                        full_dataset[index,:] = data[i,:]
                        index += 1
        else:
            # User has only specified negative bias potentials,
            # and possibly 0 V
            if biases_contain_zero == True:
                neg_and_flip_data = neg_and_flip_data[1:bias_length,:]
            else:
                # User has only specified negative bias potentials
                zero_array = np.array([[0, 0]])
                data = np.concatenate((data, zero_array), axis=0)
            full_dataset = np.concatenate((data, neg_and_flip_data), axis=0)
    else:
        # User has only specified positive bias potentials,
        # and possibly 0 V
        if biases_contain_zero == True:
            neg_and_flip_data = neg_and_flip_data[0:-1,:]
        else:
            # User has only specified positive bias potentials
            zero_array = np.array([[0, 0]])
            data = np.concatenate((zero_array, data), axis=0)
        full_dataset = np.concatenate((neg_and_flip_data, data), axis=0)

    return full_dataset


def format_data(bias_data, avg_peak_current_data):

    data = aggregate_data(bias_data, avg_peak_current_data)
    full_dataset = create_full_dataset(data)

    return full_dataset


def split_data(data):

    num_biases = len(data[:,0])
    for index in range(0, num_biases):
        if data[index,0] == 0:
            zero_V_index = index

    # These cutoff values are from observation of 50+ data sets
    cutoff_point_1 = data[zero_V_index-1, 0] # V
    cutoff_point_2 = data[zero_V_index+1, 0] # V

    data_post_split = {}

    ion_sat_v = []
    ion_sat_i = []
    e_ret_v = []
    e_ret_i = []
    e_sat_v = []
    e_sat_i = []

    index = 0
    for val in data[:,0]:
      if val < cutoff_point_1:
        ion_sat_v.append(val)
        ion_sat_i.append(data[index,1])
      elif cutoff_point_1 <= val and val <= cutoff_point_2:
        e_ret_v.append(val)
        e_ret_i.append(data[index,1])
      else:
        e_sat_v.append(val)
        e_sat_i.append(data[index,1])
      index += 1

    ion_sat = {'V':ion_sat_v,'I':ion_sat_i}
    e_ret = {'V':e_ret_v,'I':e_ret_i}
    e_sat = {'V':e_sat_v,'I':e_sat_i}

    data_post_split['i_sat'] = ion_sat
    data_post_split['e_ret'] = e_ret
    data_post_split['e_sat'] = e_sat

    return data_post_split


def calculate_linear_regressions(data_post_split):

    linear_regression_data = {}

    i_sat = data_post_split['i_sat']
    e_ret = data_post_split['e_ret']
    e_sat = data_post_split['e_sat']

    # ion saturation region linear regression
    i_reg = st.linregress(i_sat['V'], i_sat['I'])
    slope = i_reg[0]
    intercept = i_reg[1]
    rvalue = i_reg[2]
    pvalue = i_reg[3]
    stderr = i_reg[4]

    ion_sat = {}
    ion_sat['slope'] = slope
    ion_sat['intercept'] = intercept
    ion_sat['rvalue'] = rvalue
    ion_sat['pvalue'] = pvalue
    ion_sat['stderr'] = stderr

    # electron retarding region linear regression
    e_reg = st.linregress(e_ret['V'], e_ret['I'])
    slope = e_reg[0]
    intercept = e_reg[1]
    rvalue = e_reg[2]
    pvalue = e_reg[3]
    stderr = e_reg[4]

    e_ret = {}
    e_ret['slope'] = slope
    e_ret['intercept'] = intercept
    e_ret['rvalue'] = rvalue
    e_ret['pvalue'] = pvalue
    e_ret['stderr'] = stderr

    # electron saturation region linear regression
    e_reg = st.linregress(e_sat['V'], e_sat['I'])
    slope = e_reg[0]
    intercept = e_reg[1]
    rvalue = e_reg[2]
    pvalue = e_reg[3]
    stderr = e_reg[4]

    e_sat = {}
    e_sat['slope'] = slope
    e_sat['intercept'] = intercept
    e_sat['rvalue'] = rvalue
    e_sat['pvalue'] = pvalue
    e_sat['stderr'] = stderr

    linear_regression_data['i_sat'] = ion_sat
    linear_regression_data['e_ret'] = e_ret
    linear_regression_data['e_sat'] = e_sat

    return linear_regression_data


def calculate_saturation_values(
        linear_regression_data, tol=10**(-8), nargout=1):

    # in case nargout is not equal to 1 (saturation_values)
    # or 2 (saturation_values, outside_tolerances)
    if (nargout != 1) and (nargout != 2):
        nargout = 1

    ion_sat = linear_regression_data['i_sat']
    e_ret = linear_regression_data['e_ret']
    e_sat = linear_regression_data['e_sat']
    slopes = [ion_sat['slope'], e_ret['slope'], e_sat['slope']]
    intercepts = [
            ion_sat['intercept'],e_ret['intercept'], e_sat['intercept']]

    v_sat_left = (intercepts[0] - intercepts[1]) / (slopes[1] - slopes[0])
    i_sat_left = slopes[1] * v_sat_left + intercepts[1]

    v_sat_right = (intercepts[2] - intercepts[1]) / (slopes[1] - slopes[2])
    i_sat_right = slopes[1] * v_sat_right + intercepts[1]

    v_diff = abs(abs(v_sat_left) - abs(v_sat_right))
    i_diff = abs(abs(i_sat_left) - abs(i_sat_right))

    v_sat = (abs(v_sat_left) + abs(v_sat_right)) / 2
    i_sat = (abs(i_sat_left) + abs(i_sat_right)) / 2

    saturation_values = {}
    saturation_values['I sat'] = i_sat
    saturation_values['V sat'] = v_sat

    if nargout == 1:
        return saturation_values
    else:
        # Warning handling
        outside_tolerances = {}
        v_diff_outside_tol = False
        i_diff_outside_tol = False

        if v_diff > tol:
            v_diff_outside_tol = True
        if i_diff > tol:
            i_diff_outside_tol = True

        outside_tolerances['sat_V_diff'] = v_diff_outside_tol
        outside_tolerances['sat_I_diff'] = i_diff_outside_tol

        return saturation_values, outside_tolerances


def temperature(v_sat):

    k_B = const.Boltzmann # J/K
    q_e = const.e # C

    electron_temp_K = (q_e*v_sat) / (2*k_B) # K
    electron_temp = electron_temp_K / (1.1604522167E4) # eV

    return electron_temp


def density(v_sat, i_sat):
    # Cross-sectional area of the Langmuir probe used
    probe_cs_area = 1.749E-5 # m^2

    # assuming argon propellant
    ion_mass = 6.6335209E-26 # kg (per ion)

    k_B = const.Boltzmann # J/K
    q_e = const.e # C

    i_sat_Amps = i_sat * 1E-6

    electron_temp_K = (q_e*v_sat) / (2*k_B) # K

    electron_number_density = (i_sat_Amps
            / (q_e*probe_cs_area*m.exp(-0.5))
            * m.sqrt(ion_mass / (k_B*electron_temp_K))
            )

    return electron_number_density


if __name__ == 'main':
    print('Running DBDlplt')
