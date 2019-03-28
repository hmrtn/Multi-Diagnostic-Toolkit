"""Plot Window Module

This module contains the functions used to plot desired graphs for the electric
propulsion systems in the Advanced Propulsion Laboratory at the University of
Washington.
"""

__author__ = 'Hans Martin'
__contributors__ = ['Kaito Durkee']

import sys
import os

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splrep, BSpline

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QLabel, QFileDialog, QWidget, QGroupBox,
QHBoxLayout, QPushButton, QRadioButton, QVBoxLayout, QCheckBox, QLineEdit,
QComboBox, QGridLayout, QApplication, QSpacerItem, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Navbar
from cycler import cycler
from decimal import Decimal
import matplotlib.patches as mpatches
from matplotlib.offsetbox import TextArea, VPacker, AnnotationBbox
from pylab import *

import rplt
import lplt     # Import dependent libs for plotting
import splt
import bplt
import DBDlplt as dlplt

from ErrorClasses import NotImplementedError
import warnings


class PlotWindow(QDialog):

    def __init__(self):

        super(PlotWindow, self).__init__()

        self.figure = plt.figure()
        self.canvas = FigCanvas(self.figure)
        self.toolbar = Navbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)
        self.show()

# Each plot function will call for respective
# transformation and plot appearance.
# The plot data is parsed explicitly to avoid error.

def plotRPA(self, order=2, cutoff=0.04, tts=400, medWin=9,
            smooth=4, splinePts=100, stepV=2, subplt=False):

    raw_rpa = rplt.get_data(self.fname)
    lowpass_rpa = rplt.butter_filter(raw_rpa, order, cutoff)
    slice_rpa = rplt.time_slice(lowpass_rpa, tts)
    median_rpa = rplt.median_filter(slice_rpa, medWin)
    x, spl = rplt.spline_fit(median_rpa, smooth, splinePts, 'spline')
    x, y = rplt.ivdf(x, spl)

    if subplt:
        rplt.plot_dict(lowpass_rpa)

    plt.figure(figsize=(9, 5))
    plt.plot(x * stepV, y, '+-')
    plt.title('Ion Velocity Distribution')
    plt.xlabel('Energy (eV)')
    plt.ylabel('I.V.D.F (Arb. units)')
    plt.minorticks_on()
    plt.grid(which='major', alpha=0.5)
    plt.grid(which='minor', alpha=0.2)
    plt.show()

def plotDLP(self, order=2, cutoff=0.05, tof=False, DBDplot=False):
    if DBDplot == False:
        raw_dlp = lplt.get_data(self.fname)
        lowpass_dlp = lplt.butter_filter(raw_dlp, order, cutoff)
        average_dlp = lplt.butter_avg(lowpass_dlp)
        time, density = lplt.density(average_dlp)

        ax, fig = plt.subplots()


        for key in density.keys():
            fig.plot(time, density[key], label=key)
            fig.legend(prop={'size': 7})

            if tof:     # if time of flight is checked
                xmaxPos = np.argmax(density[key], axis=0) / 10
                yminPos = np.min(density[key])
                fig.axvline(x=xmaxPos, color='r', linestyle='--')
                textstr = (xmaxPos)
                props = dict(boxstyle='square', facecolor='white', alpha=0.0)
                fig.text(
                    xmaxPos,
                    yminPos,
                    textstr,
                    fontsize=9,
                    verticalalignment='center',
                    bbox=props)

        plt.xlabel(r'Time ($\mu$s)')
        plt.ylabel('$n_{e}$ ($m^{-3}$)')
        plt.title('Plasma Density')
        plt.minorticks_on()
        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.2)
        plt.show()
    else:

        [raw_I_vals, raw_bias_vals] = dlplt.get_data(self.fname)
        lowpass_I_vals = dlplt.butter_filter(raw_I_vals, order, cutoff)
        avg_I_vals = dlplt.butter_avg(lowpass_I_vals, raw_bias_vals)
        data = dlplt.format_data(raw_bias_vals, avg_I_vals)
        sectioned_data = dlplt.split_data(data)
        regression_data = dlplt.calculate_linear_regressions(sectioned_data)

        tol = 1E-8

        sat_vals, outside_tols =  dlplt.calculate_saturation_values(
                regression_data, tol, 2)

        V_sat = sat_vals['V sat']
        I_sat = sat_vals['I sat']

        electron_temp = dlplt.temperature(V_sat)
        electron_number_density = dlplt.density(V_sat, I_sat)

        # Warning handling
        if outside_tols['sat_V_diff'] == True:
            message = ('Average saturated voltage value '
                    + 'was used because the difference between left '
                    + 'and right saturated voltage values was outside the '
                    + 'tolerance of %.2E V.' % tol)
            warnings.warn(message, RuntimeWarning)
        if outside_tols['sat_I_diff'] == True:
            message = ('Average saturated current value '
                    + 'was used because the difference between left '
                    + 'and right saturated voltage values was outside the '
                    + 'tolerance of %.2E uA.' % tol)
            warnings.warn(message, RuntimeWarning)

        ax, fig = plt.subplots()
        # The section below still needs to be cleaned, but it will work for now
###############################################################################
        x_ion = np.linspace(data[0,0], data[-1,0], num=50)
        x_e_ret = np.linspace(data[0,0], data[-1,0], num=50)
        x_e_sat = np.linspace(data[0,0], data[-1,0], num=50)
        y_ion = np.zeros_like(x_ion)
        y_e_ret = np.zeros_like(x_e_ret)
        y_e_sat = np.zeros_like(x_e_sat)

        i_sat = regression_data['i_sat']
        e_ret = regression_data['e_ret']
        e_sat = regression_data['e_sat']

        index = 0
        for val in x_ion:
            y_ion[index] = i_sat['slope']*val + i_sat['intercept']
            index += 1
        index = 0
        for val in x_e_ret:
            y_e_ret[index] = e_ret['slope']*val + e_ret['intercept']
            index += 1
        index = 0
        for val in x_e_sat:
            y_e_sat[index] = e_sat['slope']*val + e_sat['intercept']
            index += 1

        y_ion = np.array(y_ion)
        y_e_ret = np.array(y_e_ret)
        y_e_sat = np.array(y_e_sat)

        v_fine = np.linspace(data[0,0], data[-1,0], 300)
        t, c, k = splrep(
                data[:,0], data[:,1], s=0, k=3)
        I_func = BSpline(t, c, k, extrapolate=False)
        fig.plot(v_fine, I_func(v_fine), color='black',
                linestyle='dashed', linewidth=2)
        fig.scatter(
                data[:,0], data[:,1], color='black', s=10*(2**2))
        fig.plot(x_ion, y_ion, color='red', linewidth=2.0)
        fig.plot(x_e_ret, y_e_ret, color='magenta', linewidth=2.0)
        fig.plot(x_e_sat, y_e_sat, color='green', linewidth=2.0)

        # Construct linear regression equations

        if i_sat['intercept'] < 0:
            i_sat_intercept_negative = True
            i_sat_intercept_zero = False
            i_sat['intercept'] = np.absolute(i_sat['intercept'])
        else:
            i_sat_intercept_negative = False
            if round(i_sat['intercept'], 4) == 0.0000:
                i_sat_intercept_zero = True
            else:
                i_sat_intercept_zero = False


        if e_ret['intercept'] < 0:
            e_ret_intercept_negative = True
            e_ret['intercept'] = np.absolute(e_ret['intercept'])
        else:
             e_ret_intercept_negative = False
             if round(e_ret['intercept'], 4) == 0.0000:
                 e_ret_intercept_zero = True
             else:
                 e_ret_intercept_zero = False

        if e_sat['intercept'] < 0:
            e_sat_intercept_negative = True
            e_sat['intercept'] = np.absolute(e_sat['intercept'])
        else:
             e_sat_intercept_negative = False
             if round(e_sat['intercept'], 4) == 0.0000:
                 e_sat_intercept_zero = True
             else:
                 e_sat_intercept_zero = False


        s_ion_str = str("%.4f" % round(i_sat['slope'], 4))
        inter_ion_str = str("%.4f" % round(i_sat['intercept'], 4))

        s_e_ret_str = str("%.4f" % round(e_ret['slope'], 4))
        inter_e_ret_str = str("%.4f" % round(e_ret['intercept'], 4))

        s_e_sat_str = str("%.4f" % round(e_sat['slope'], 4))
        inter_e_sat_str = str("%.4f" % round(e_sat['intercept'], 4))


        str_ion = r'$I_{ion \,\,\, sat} = $' + s_ion_str
        if i_sat_intercept_negative == False:
            if i_sat_intercept_zero == False:
                str_ion += r'$\cdot V +$' + inter_ion_str
            else:
                str_ion += r'$\cdot V$'
        else:
            str_ion += r'$\cdot V -$' + inter_ion_str

        str_e_ret = r'$I_{e \,\,\, ret} = $' + s_e_ret_str
        if e_ret_intercept_negative == False:
            if e_ret_intercept_zero == False:
                str_e_ret += r'$\cdot V +$' + inter_e_ret_str
            else:
                str_e_ret += r'$\cdot V$'
        else:
            str_e_ret += r'$\cdot V -$' + inter_e_ret_str

        str_e_sat = r'$I_{e \,\,\, sat} = $' + s_e_sat_str
        if e_sat_intercept_negative == False:
            if e_sat_intercept_zero == False:
                str_e_sat += r'$\cdot V +$' + inter_e_sat_str
            else:
                str_e_sat += r'$\cdot V$'
        else:
            str_e_sat += r'$\cdot V -$' + inter_e_sat_str

        # Construct electron temp and number density output

        T_str = r'$T_e$ ~ ' + str('%.2f' % round(electron_temp, 2)) + ' eV'
        n_e_str =  (r'$n_e$ ~ '
                + '%.2E' % Decimal(str(electron_number_density))
                + r' $\mathrm{m}^{-3}$')

        # Construct legend
        h = []

        plot_labels = ['Measured Data',
                'Ion Saturation Regression',
                'Electron Retarding Regression',
                'Electron Saturation Regression']

        h.append(mpatches.Patch(color='black', label=plot_labels[0]))
        h.append(mpatches.Patch(color='red', label=plot_labels[1]))
        h.append(mpatches.Patch(color='magenta', label=plot_labels[2]))
        h.append(mpatches.Patch(color='green', label=plot_labels[3]))

        fig.legend(loc=2, borderaxespad=0, handles=h, prop={'size': 18})

  #############################################################################
        ax = plt.gca()

        # fig.text(0.55, 0.30, str_ion, transform=ax.transAxes)
        # fig.text(0.55, 0.25, str_e_ret, transform=ax.transAxes)
        # fig.text(0.55, 0.20, str_e_sat, transform=ax.transAxes)
        # fig.text(0.55, 0.10, T_str, transform=ax.transAxes)
        # fig.text(0.55, 0.5, n_e_str, transform=ax.transAxes)

        txt = (str_ion + "\n" + str_e_ret + "\n" + str_e_sat
            + "\n" + T_str + "\n" + n_e_str)

        props = dict(boxstyle='round', facecolor='white', alpha=0.5)

        fig.text(0.55, 0.25, txt, size=18,
            verticalalignment="top", horizontalalignment="left",
            multialignment="left", bbox=props,  transform=ax.transAxes)

        plt.rcParams.update({'font.size': 22})

        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                ax.get_xticklabels() + ax.get_yticklabels()):
             item.set_fontsize(20)

        plt.xlabel('Voltage (V)')
        plt.ylabel(r'Current ($\mu$A)')
        plt.title('Bias Voltage vs Current')
        plt.minorticks_on()
        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.2)
        plt.show()



def plotNFP(self, order=2, cutoff=0.05, biasplt=False):

    # Until working, throw NotImplemented error if biasplt == False
    if biasplt == False:
        raise NotImplementedError("NFP plotting not yet implemented")

    if biasplt == False:
        raw_nfp = nplt.get_data(self.fname)
        lowpass_nfp = nplt.butter_filter(raw_nfp, order, cutoff)
        max_vals_nfp = biasplt.get_max_vals(lowpass_nfp)
        Idensity = nplt.Idensity(max_vals_nfp)
        #plt.figure(figsize=(9, 5))

        # Setting prop cycle on default rc parameter
        plt.rc('lines', linewidth=4)
        plt.rc('axes', prop_cycle=(cycler('color', ['k', 'b', 'r', 'm'])))

        ax, fig = plt.subplots()

        for id in Idensity.keys():
            if id == 'L':
                id_label = 'Left'
            elif id == 'R':
                id_label = 'Right'
            elif id == 'D':
                id_label = 'Double'
            elif id == 'T':
                id_label = 'Triple'
            else:
                id_label = 'Other'
            fig.plot(*zip(*sorted(Idensity[id].items())), 'o', label=id_label)
            fig.legend(prop={'size': 7})

        plt.xlabel(r'Radial Position (cm)')
        plt.ylabel(r'$J$ $\left(\mathrm{A} \, \mathrm{m}^{-2}\right)$')
        plt.title(r'Plasma Current Density at $V_{bias} = -30 \, V$')
        plt.minorticks_on()
        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.2)
        plt.show()

    else:
        raw_nfp = bplt.get_data(self.fname)
        lowpass_nfp = bplt.butter_filter(raw_nfp, order, cutoff)
        max_vals_nfp = bplt.get_max_vals(lowpass_nfp)
        Idensity = bplt.Idensity(max_vals_nfp)
        #plt.figure(figsize=(9, 5))

        ax, fig = plt.subplots()

        for key in Idensity.keys():
            fig.plot(*zip(*sorted(Idensity.items())), 'ko')

        plt.xlabel(r'Bias Potential (V)')
        plt.ylabel(r'$J$ $\left(\mathrm{A} \, \mathrm{m}^{-2} \right)$')
        plt.title(r'Plasma Current Density at $r = 0$')
        plt.minorticks_on()
        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.2)
        plt.show()


def plotSingle(self, order=2, cutoff=0.05, medWin=9,
                smooth=4, splinePts=100, index=0):


    if index is 1:

        raw = splt.get_data(self.fname)

        splt.plot_dict(raw)

    elif index is 2:
        raw = splt.get_data(self.fname)
        buttered = splt.butter_filter(raw, order, cutoff)
        print(buttered)
        splt.plot_dict(buttered)
        # plt.figure()
        # plt.minorticks_on()
        # plt.grid(which='major', alpha=0.5)
        # plt.grid(which='minor', alpha=0.2)
    elif index is 3:
        raw = splt.get_data(self.fname)
        buttered = splt.butter_filter(raw, order, cutoff)
        median = splt.median_filter(buttered, 9)

        splt.plot_dict(median)
    elif index is 0:
        print('NOT READY')
