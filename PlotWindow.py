
import sys
import os

import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QLabel, QFileDialog, QWidget, QGroupBox,
QHBoxLayout, QPushButton, QRadioButton, QVBoxLayout, QCheckBox, QLineEdit,
QComboBox, QGridLayout, QApplication, QSpacerItem, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Navbar
from cycler import cycler

import rplt
import lplt     # Import dependent libs for plotting
import splt
import biasplt


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

def plotDLP(self, order=2, cutoff=0.05, tof=False):

    raw_dlp = lplt.get_data(self.fname)
    lowpass_dlp = lplt.butter_filter(raw_dlp, order, cutoff)
    average_dlp = lplt.butter_avg(lowpass_dlp)
    time, density = lplt.density(average_dlp)
    #plt.figure(figsize=(9, 5))

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


def plotNFP(self, order=2, cutoff=0.05):
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


def plotBiasVerification(self, order=2, cutoff=0.05):
    raw_nfp = biasplt.get_data(self.fname)
    lowpass_nfp = biasplt.butter_filter(raw_nfp, order, cutoff)
    max_vals_nfp = biasplt.get_max_vals(lowpass_nfp)
    Idensity = biasplt.Idensity(max_vals_nfp)
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
