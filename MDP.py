import matplotlib.pyplot as plt
import sys
import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QMessageBox, QCheckBox, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

import rplt
import lplt

class MainWindow(QDialog):

    def __init__(self, parent = None):

        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Multi-Diagnostic Plotter 1.0')
        self.setMinimumSize(QSize(300, 220))

        self.launch_lplt = QPushButton('Plot Langmuir Data', self)
        self.launch_rplt = QPushButton('Plot RPA Data', self)
        self.launch_fplt = QPushButton('Plot Faraday Data', self)
        #self.enable_tof = QCheckBox('Enable Time of Flight (Langmuir)', self) # checkbox not yet implemented
        #self.export_data = QCheckBox('Export Data', self) # same



        layout = QVBoxLayout()
        layout.addWidget(self.launch_lplt)
        layout.addWidget(self.launch_rplt)
        layout.addWidget(self.launch_fplt)
        #layout.addWidget(self.enable_tof)
        #layout.addWidget(self.export_data)

        self.setLayout(layout)

        self.launch_rplt.clicked.connect(RPA)
        self.launch_lplt.clicked.connect(Langmuir)

class RPA(QDialog):

    def __init__(self):

        super(RPA, self).__init__()

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        self.setWindowTitle('RPA Plot')
        self.setLayout(layout)
        self.plot_rpa()

    def plot_rpa(self):

        BUTTER_ORDER = 2        # default = 2
        BUTTER_CUTOFF = 0.04    # default = 0.04
        TIME_2_SLICE = 400      # default = 400
        MEDIAN_WINDOW = 9       # default = 9
        SMOOTH_SPLINE = 4       # default = 4
        SPLINE_POINTS = 100     # defualt = 100
        VOLTAGE_STEP = 2 

        raw_rpa = rplt.get_data('RPA')
        lowpass_rpa = rplt.butter(raw_rpa, BUTTER_ORDER, BUTTER_CUTOFF)
        slice_rpa = rplt.time_slice(lowpass_rpa, TIME_2_SLICE)
        median_rpa = rplt.median_filter(slice_rpa, MEDIAN_WINDOW)
        x, spl = rplt.spline_fit(median_rpa, SMOOTH_SPLINE, SPLINE_POINTS, 'spline')
        x, y = rplt.ivdf(x, spl)
        
        plt.plot(x * VOLTAGE_STEP, y,'+-')
        plt.title('Ion Velocity Distribution')
        plt.xlabel('Energy (eV)'); plt.ylabel('I.V.D.F (Arb. units)')
        plt.minorticks_on()
        plt.grid(which = 'major', alpha = 0.5); plt.grid(which = 'minor', alpha = 0.2)
        plt.show()


class Langmuir(QDialog):
    
    def __init__(self):
        
        super(Langmuir, self).__init__()
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        self.setWindowTitle('Langmuir Plot')
        self.setLayout(layout)
        self.plot_dlp()

    def plot_dlp(self):

        BUTTER_ORDER = 2 # default = 2
        BUTTER_CUTOFF = 0.005 # default = 0.005

        raw_dlp = lplt.get_data('DLP')
        lowpass_dlp = lplt.butter(raw_dlp, BUTTER_ORDER, BUTTER_CUTOFF)
        average_dlp = lplt.butter_avg(lowpass_dlp)
        time, density = lplt.density(average_dlp)
        
        for key in density.keys():
            plt.plot(time, density[key],label=key)
            plt.legend(prop={'size': 7})
            
            #### UNCOMMENT THIS TO ENABLE TOF #####
            
            # xmaxPos = np.argmax(density[key], axis=0)/10
            # ymaxPos = np.max(density[key])
            # plt.axvline(x=xmaxPos, color ='r', linestyle='--')
            # print(xmaxPos)
            
            ######################
        
        plt.xlabel('Time ($\mu$s)'); plt.ylabel('$n_{e}$ ($m^{-3}$)')
        plt.title('Plasma Density')
        plt.minorticks_on()
        plt.grid(which = 'major', alpha = 0.5); plt.grid(which = 'minor', alpha = 0.2)
        
        plt.show()

def main():

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__=='__main__':

    main()
