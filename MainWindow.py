"""Main Window GUI Module

This module contains the functions used to create the GUI and plot the desired
graphs for the electric propulsion systems in the Advanced Propulsion
Laboratory at the University of Washington.
"""

__version__ = '1.5.1'
__author__ = 'Hans Martin'
__contributors__ = ['Kaito Durkee']

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

import rplt
import lplt     # Import dependent libs for plotting
import pplt
import splt
import PlotWindow

class MainWindow(QDialog):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Multi-Diagnostic Toolkit ' + __version__)
        self.setWindowIcon(QIcon('assets/ic_aplotter.png'))
        self.setMinimumSize(QSize(400, 420))    # Set main window dimensions

        # Calls to create options grid below statusbar
        self.createGrid()

        # Choose plot type combobox in statusbar
        list1 = ['Choose Dataset...',
                 'Langmuir',
                 'REFA',
                 'Nude Faraday',
                 'Input Power',
                 'Single Dataset']

        self.choose = QComboBox(self)
        self.choose.addItems(list1)

        # Call to update layout on list index change
        self.choose.currentIndexChanged.connect(
            self.chooseLayout, self.choose.currentIndex())

        self.plot = QPushButton('Plot', self)
        self.browseButton = QPushButton('Browse', self)
        self.default_directory = 'C:\\'
        self.dirLoc = QLineEdit(self.default_directory)

        windowLayout = QVBoxLayout()    # Vertical layout, for main window
        statusLayout = QHBoxLayout()    # Horizontal Layout, for statusbar
        browseLayout = QHBoxLayout()    # Horizontal Layout, for browse bar

        windowLayout.addLayout(statusLayout)

        statusLayout.addWidget(self.choose)
        statusLayout.addWidget(self.plot)
        windowLayout.addWidget(self.optionsBox)
        browseLayout.addWidget(QLabel('Location:'))
        browseLayout.addWidget(self.dirLoc)
        browseLayout.addWidget(self.browseButton)

        self.setLayout(windowLayout)
        windowLayout.addLayout(browseLayout)

        self.show()


        # Create textboxes, checkboxes, buttons, etc
        # with filled in default values

        self.tof = QCheckBox('Time Of Flight')
        self.tts = QLineEdit('400')
        self.subplt = QCheckBox('Show Subplot')
        self.bplt = QCheckBox('Verify Bias')
        self.DBDlplt = QCheckBox('DBD Plot')
        self.energy = QCheckBox('Plot Energy Curve')
        self.orderflt = QLineEdit('2')
        self.cutflt = QLineEdit('0.005')
        self.window = QLineEdit('9')
        self.smooth_spline = QLineEdit('4')
        self.spline_pts = QLineEdit('100')
        self.volt_stp = QLineEdit('2')
        self.single_shot = QCheckBox('Show Single Shot')
        self.export = QCheckBox('Export Data')
        self.ds_rpa = QRadioButton('REFA')
        self.ds_dlp = QRadioButton('Langmuir')
        self.verticalSpacer = QSpacerItem(40, 40, QSizePolicy.Minimum,
                                            QSizePolicy.Expanding)

        self.ptype = QComboBox(self)
        self.ptypeList = ['Choose Plot Type...',
                          'Raw',
                          'Butterworth Filter',
                          'Median',
                          'Spline']
        self.ptype.addItems(self.ptypeList)
        self.errortxt = 'ERROR: CHECK DIRECTORY INFORMATION'


    # Checks index of plot type in status bar and updates
    # respective layout based on index value

    def chooseLayout(self, ind):

        self.clearLayout(self.layout)

        try:
            self.plot.clicked.disconnect() or self.browseButton.disconnect()
        except Exception:
            pass

        if ind is 1:

            self.layoutDLP()

        elif ind is 2:

            self.layoutRPA()

        elif ind is 3:
            self.layoutNFP()

        elif ind is 4:
            self.layoutPower()

        elif ind is 5:

            self.layoutSingle()

    def createGrid(self):

        self.optionsBox = QGroupBox('Options')
        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 0)
        self.optionsBox.setLayout(self.layout)


    # Clear layout at every index update to avoid
    # extra objects being created/duplicated

    def clearLayout(self, layout):

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)


    # On each layout update:
    # gui objects are added according to row and column
    # changes state of plot button and type of parsing

    def layoutRPA(self):
        default_dir = os.getcwd()+'/RPA'

        self.layout.addWidget(self.subplt, 0, 0)
        self.layout.addWidget(self.export, 2, 0)
        self.layout.addWidget(QLabel('Filter Order:'), 0, 1)
        self.layout.addWidget(self.orderflt, 0, 2)
        self.layout.addWidget(QLabel('Cutoff Freq.:'), 1, 1)
        self.layout.addWidget(self.cutflt, 1, 2)
        self.layout.addWidget(QLabel('Filter Window:'), 2, 1)
        self.layout.addWidget(self.window, 2, 2)
        self.layout.addWidget(QLabel('Slice Time:'), 3, 1)
        self.layout.addWidget(self.tts, 3, 2)
        self.layout.addWidget(QLabel('Smooth Factor:'), 4, 1)
        self.layout.addWidget(self.smooth_spline, 4, 2)
        self.layout.addWidget(QLabel('Spline Points:'), 5, 1)
        self.layout.addWidget(self.spline_pts, 5, 2)
        self.layout.addWidget(QLabel('Step Voltage:'), 6, 1)
        self.layout.addWidget(self.volt_stp, 6, 2)
        self.layout.addItem(self.verticalSpacer)

        self.plot.clicked.connect(self.pushRPA)
        self.browseButton.clicked.connect(lambda: self.getFiles('folder'))

    def layoutDLP(self):

        default_dir = os.getcwd()+'/DLP'

        self.layout.addWidget(self.tof, 0, 0)
        self.layout.addWidget(self.DBDlplt, 1, 0)
        self.layout.addWidget(self.export, 2, 0)
        self.layout.addWidget(QLabel('Filter Order:'), 0, 1)
        self.layout.addWidget(self.orderflt, 0, 2)
        self.layout.addWidget(QLabel('Cutoff Freq.:'), 1, 1)
        self.layout.addWidget(self.cutflt, 1, 2)
        self.dirLoc.setText(default_dir)
        self.layout.addItem(self.verticalSpacer)

        self.plot.clicked.connect(self.pushDLP)
        self.browseButton.clicked.connect(lambda: self.getFiles('folder'))

    def layoutNFP(self):

        default_dir = os.getcwd()+'/NFP'

        self.layout.addWidget(self.bplt, 0, 0)
        self.layout.addWidget(self.export, 2, 0)
        self.layout.addWidget(QLabel('Filter Order:'), 0, 1)
        self.layout.addWidget(self.orderflt, 0, 2)
        self.layout.addWidget(QLabel('Cutoff Freq.:'), 1, 1)
        self.layout.addWidget(self.cutflt, 1, 2)
        self.dirLoc.setText(default_dir)
        self.layout.addItem(self.verticalSpacer)

        self.plot.clicked.connect(self.pushNFP)
        self.browseButton.clicked.connect(lambda: self.getFiles('folder'))

    def layoutPower(self):

        default_dir = os.getcwd()+'/DLP'

        self.layout.addWidget(self.energy, 0, 0)
        self.dirLoc.setText(default_dir)
        self.layout.addItem(self.verticalSpacer)

        self.plot.clicked.connect(self.pushPower)
        self.browseButton.clicked.connect(lambda: self.getFiles('folder'))


    def layoutSingle(self):

        self.layout.addWidget(self.ptype, 1, 0)
        self.layout.addWidget(self.export, 2, 0)
        self.layout.addWidget(QLabel('Filter Order:'), 0, 1)
        self.layout.addWidget(self.orderflt, 0, 2)
        self.layout.addWidget(QLabel('Cutoff Freq.:'), 1, 1)
        self.layout.addWidget(self.cutflt, 1, 2)
        self.layout.addWidget(QLabel('Filter Window:'), 2, 1)
        self.layout.addWidget(self.window, 2, 2)
        self.layout.addWidget(QLabel('Smooth Factor:'), 3, 1)
        self.layout.addWidget(self.smooth_spline, 3, 2)
        self.layout.addWidget(QLabel('Spline Points:'), 4, 1)
        self.layout.addWidget(self.spline_pts, 4, 2)
        self.layout.addItem(self.verticalSpacer)

        self.plot.clicked.connect(self.pushSingle)
        self.browseButton.clicked.connect(lambda: self.getFiles('file'))


    # Each push function is called via respective plotbutton layout
    # on push call -> read state of each gui object ->
    # create new plot window object filled with plotted data


    def pushRPA(self):

        order = int(self.orderflt.text())
        cutoff = float(self.cutflt.text())
        tts = int(self.tts.text())
        medWin = int(self.window.text())
        smooth = int(self.smooth_spline.text())
        splinePts = int(self.spline_pts.text())
        stepV = int(self.volt_stp.text())
        subplt = int(self.subplt.isChecked())
        try:
            PlotWindow.plotRPA(self, order,
                            cutoff, tts,
                            medWin, smooth,
                            splinePts, stepV, subplt)
        except (AttributeError, NotADirectoryError):
            print(self.errortxt)

    def pushDLP(self):

        order = int(self.orderflt.text())
        cutoff = float(self.cutflt.text())
        tof = self.tof.isChecked()
        DBDlplt = self.DBDlplt.isChecked()

        try:
            PlotWindow.plotDLP(self, order, cutoff, tof, DBDlplt)
        except(AttributeError, NotADirectoryError):
            print(self.errortxt)

    def pushNFP(self):

        order = int(self.orderflt.text())
        cutoff = float(self.cutflt.text())
        biasplt = int(self.bplt.isChecked())

        try:
            PlotWindow.plotNFP(self, order, cutoff, biasplt)
        except(AttributeError, NotADirectoryError):
            print(self.errortxt)

    def pushPower(self):

        energy = bool(self.energy.isChecked())

        try:
            PlotWindow.plotPower(self, energy)
        except(AttributeError, NotADirectoryError):
            print(self.errortxt)

    def pushSingle(self):

        order = int(self.orderflt.text())
        cutoff = float(self.cutflt.text())
        medWin = int(self.window.text())
        smooth = int(self.smooth_spline.text())
        splinePts = int(self.spline_pts.text())
        index = int(self.ptype.currentIndex())

        try:
            PlotWindow.plotSingle(
            self,
            order,
            cutoff,
            medWin,
            smooth,
            splinePts,
            index)
        except(AttributeError, NotADirectoryError):
            print(self.errortxt)

    # Used to determine file explorer file type expectation
    def getFiles(self, dirType='folder'):
        if dirType is 'folder':
            self.fname = QFileDialog.getExistingDirectory()
        elif dirType is 'file':
            # Returns a tuple, index first for location
            self.fname = str(QFileDialog.getOpenFileName()[0])

        self.dirLoc.setText(self.fname)

def main():

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':

    main()
