import os
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets

import time
import collections
import math

from matplotlib import *
import pyqtgraph as pg


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class DisplaySavedData(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.setGeometry(100, 100, 1060, 680)
        self.setMinimumSize(1060, 680)
        self.setWindowTitle("Saved Data Plotter")
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptPath + os.path.sep + 'Icon.ico'))

        # Empty widget to shrink areas
        self.empty = QWidget()

        # Other
        self.Switch_index = 0
        self.filters_data = [0, 0]

        # Checkboxes for variables
        self.checkers = []
        for i in range(15):
            self.checkers.append(QCheckBox())
            self.checkers[i].setEnabled(False)

        self.imu1 = QCheckBox()
        self.imu2 = QCheckBox()
        self.imu3 = QCheckBox()
        self.imu4 = QCheckBox()
        self.imu5 = QCheckBox()
        self.imu6 = QCheckBox()

        # Locks until file is loaded
        self.imu1.setEnabled(False)
        self.imu2.setEnabled(False)
        self.imu3.setEnabled(False)
        self.imu4.setEnabled(False)
        self.imu5.setEnabled(False)
        self.imu6.setEnabled(False)

        # Checkbox labels
        self.x_gyro_label = QLabel("X")
        self.y_gyro_label = QLabel("Y")
        self.z_gyro_label = QLabel("Z")
        self.x_acc_label = QLabel("X")
        self.y_acc_label = QLabel("Y")
        self.z_acc_label = QLabel("Z")
        self.x_mag_label = QLabel("X")
        self.y_mag_label = QLabel("Y")
        self.z_mag_label = QLabel("Z")
        self.imu_counter_label = QLabel("Counter")
        self.rssi_data_label = QLabel("RSSi [dBm]")
        self.imu_temp_label = QLabel("IMU Temperature")
        self.imu_pressure_label = QLabel("Pressure")
        self.glob_temp_label = QLabel("Temperature")
        self.battery_label = QLabel("Battery")
        self.imu1_label = QLabel("Imu 1")
        self.imu2_label = QLabel("Imu 2")
        self.imu3_label = QLabel("Imu 3")
        self.imu4_label = QLabel("Imu 4")
        self.imu5_label = QLabel("Imu 5")
        self.imu6_label = QLabel("Imu 6")

        # Group labels
        self.glabel = QLabel("Gyroscope")
        self.glabel.setFont(QFont("Calibri", 14))
        self.alabel = QLabel("Accelerometer")
        self.alabel.setFont(QFont("Calibri", 14))
        self.mlabel = QLabel("Magnetometer")
        self.mlabel.setFont(QFont("Calibri", 14))
        self.others = QLabel("Other data to display")
        self.others.setFont(QFont("Calibri", 14))
        self.imuselection = QLabel("Select IMU")
        self.imuselection.setFont(QFont("Calibri", 14))

        # Graph initialization
        self.display_graph = pg.PlotWidget()
        self.display_graph.setBackground("#f2f2f2")
        self.display_graph.showGrid(x=True, y=True)
        font = QtGui.QFont()
        font.setPixelSize(8)
        self.display_graph.getAxis("bottom").tickFont = font
        self.display_graph.getAxis("bottom").setStyle(tickTextOffset=5)
        self.display_graph.getAxis("left").tickFont = font
        self.display_graph.getAxis("left").setStyle(tickTextOffset=20)
        labelStyle = {'font-size': '8pt'}
        self.display_graph.setLabel('left', 'RAW ADC DATA', color='k', **labelStyle)
        self.display_graph.setLabel('bottom', 'Sample', 'n', color='k', **labelStyle)

        # Plotter definition
        self.plotter = []
        self.plotter.append(self.display_graph.plot(pen=(255, 0, 0)))  # GX
        self.plotter.append(self.display_graph.plot(pen=(50, 255, 50)))  # GY
        self.plotter.append(self.display_graph.plot(pen=(0, 0, 255)))  # GZ
        self.plotter.append(self.display_graph.plot(pen=(200, 200, 20)))  # AX
        self.plotter.append(self.display_graph.plot(pen=(0, 200, 255)))  # AY
        self.plotter.append(self.display_graph.plot(pen=(255, 0, 255)))  # AZ
        self.plotter.append(self.display_graph.plot(pen=(80, 120, 200)))  # MX
        self.plotter.append(self.display_graph.plot(pen=(230, 90, 45)))  # MY
        self.plotter.append(self.display_graph.plot(pen=(87, 14, 99)))  # MZ
        self.plotter.append(self.display_graph.plot(pen=(255, 67, 123)))  # Counter
        self.plotter.append(self.display_graph.plot(pen=(255, 141, 45)))  # RSSi 1
        self.plotter.append(self.display_graph.plot(pen=(180, 10, 88)))  # RSSi 2
        self.plotter.append(self.display_graph.plot(pen=(88, 45, 171)))  # IMU Temp
        self.plotter.append(self.display_graph.plot(pen=(88, 191, 75)))  # Pressure
        self.plotter.append(self.display_graph.plot(pen=(120, 90, 180)))  # Temp P
        self.plotter.append(self.display_graph.plot(pen=(155, 120, 155)))  # Battery

        # Add layouts to main_layout inside QGroupBox "Display selector"
        self.main_layout.addWidget(self.Load_data(), 0, 0, 1, 1, Qt.AlignTop)  # BOX 1
        self.main_layout.addWidget(self.LostIMUS(), 0, 1, 1, 1, Qt.AlignTop)  # BOX 5
        self.main_layout.addWidget(self.select_window_fun(), 0, 2, 1, 1, Qt.AlignTop)  # BOX 2
        self.main_layout.addWidget(self.StandardsBox(), 0, 3, 1, 1, Qt.AlignTop)  # BOX 3
        self.main_layout.addWidget(self.urlwindow(), 1, 0, 1, 4)  # BOX 4
        self.main_layout.addWidget(self.display_graph, 2, 0, 1, 4)  # GRAPH
        self.setLayout(self.main_layout)

        # Status change of checkboxes, calling a function
        # Indexes follow displayed check boxes starting with Gyroscope and ending with Other data to display
        self.checkers[0].stateChanged.connect(self.display_data_fun)  # Gx
        self.checkers[1].stateChanged.connect(self.display_data_fun)  # Gy
        self.checkers[2].stateChanged.connect(self.display_data_fun)  # Gz
        self.checkers[3].stateChanged.connect(self.display_data_fun)  # Ax
        self.checkers[4].stateChanged.connect(self.display_data_fun)  # Ay
        self.checkers[5].stateChanged.connect(self.display_data_fun)  # Az
        self.checkers[6].stateChanged.connect(self.display_data_fun)  # Mx
        self.checkers[7].stateChanged.connect(self.display_data_fun)  # My
        self.checkers[8].stateChanged.connect(self.display_data_fun)  # Mz
        self.checkers[9].stateChanged.connect(self.display_data_fun)  # Counter
        self.checkers[10].stateChanged.connect(self.display_data_fun)  # Rssi
        self.checkers[11].stateChanged.connect(self.display_data_fun)  # IMU Temperature
        self.checkers[12].stateChanged.connect(self.display_data_fun)  # Pressure
        self.checkers[13].stateChanged.connect(self.display_data_fun)  # Temperature
        self.checkers[14].stateChanged.connect(self.display_data_fun)  # Battery

        # Checkbox triggers for imus
        self.imu1.stateChanged.connect(self.display_data_fun)
        self.imu2.stateChanged.connect(self.display_data_fun)
        self.imu3.stateChanged.connect(self.display_data_fun)
        self.imu4.stateChanged.connect(self.display_data_fun)
        self.imu5.stateChanged.connect(self.display_data_fun)
        self.imu6.stateChanged.connect(self.display_data_fun)

        # RAW and SI button click calls
        self.RAWButton.clicked.connect(self.change_format_raw)
        self.SIButton.clicked.connect(self.change_format_si)

    ########################### BOX 1 ########################################
    # Load data Group box window with Button which will make a pop up file selection
    def Load_data(self):
        self.Load_data_window = QGroupBox()
        self.Load_data_window.setFixedHeight(170)
        self.Load_data_window.setFixedWidth(100)
        self.Load_data_window.setTitle("File selector")
        self.Load_data_window.setStyleSheet("QGroupBox { background-color: rgb(250, 250, 250);"
                                            " border: 1px solid rgb(150, 150, 150);"
                                            "border-radius: 2px;"
                                            "margin-top: 6px; }"
                                            "QGroupBox::title {subcontrol-origin: margin;"
                                            "left: 7px;"
                                            "padding: -4px 5px 0px 5px }")
        self.Load_data_window.setFont(QFont("Calibri", 10))
           
        self.Load_data_window.layout = QGridLayout()
        self.Load_data_window.layout.addWidget(self.Load_button_fun(), 1, 1, 1, 1, Qt.AlignCenter)
        self.Load_data_window.setLayout(self.Load_data_window.layout)
        return self.Load_data_window

    def Load_button_fun(self):
        # File to load button
        self.Load_button = QPushButton("Select file")
        self.Load_button.setFixedSize(80, 40)
        self.Load_button.setFont(QFont("Calibri", 12))
        self.Load_button.setStyleSheet("background: #f0f5f5")
        self.Load_button.clicked.connect(self.LoadFile)
        return self.Load_button

    ##########################################################################

    ######################### Data selection box ############################
    # BOX 2
    def select_window_fun(self):
        self.select_window = QGroupBox()
        self.select_window.setFixedHeight(170)
        self.select_window.setMinimumWidth(690)
        self.select_window.setTitle("Display selector")
        self.select_window.setStyleSheet("QGroupBox { background-color: rgb(250, 250, 250);"
                                         " border: 1px solid rgb(150, 150, 150);"
                                         "border-radius: 2px;"
                                         "margin-top: 6px; }"
                                         "QGroupBox::title {subcontrol-origin: margin;"
                                         "left: 7px;"
                                         "padding: -4px 5px 0px 5px }")

        self.select_window.layout = QGridLayout()  # Layout in select_window Groupbox
        self.select_window.layout.setAlignment(Qt.AlignCenter)
        # Imu selection
        self.select_window.layout.addWidget(self.imuselection, 0, 0, 1, 2, Qt.AlignCenter)

        self.select_window.layout.addWidget(self.imu1, 1, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu1_label, 1, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.imu2, 2, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu2_label, 2, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.imu3, 3, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu3_label, 3, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.imu4, 4, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu4_label, 4, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.imu5, 5, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu5_label, 5, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.imu6, 6, 0, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.imu6_label, 6, 1, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.empty, 0, 2, 5, 2)

        # Gyroscope
        self.select_window.layout.addWidget(self.glabel, 0, 4, 1, 2, Qt.AlignCenter)

        self.select_window.layout.addWidget(self.checkers[0], 1, 4, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.x_gyro_label, 1, 5, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[1], 2, 4, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.y_gyro_label, 2, 5, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[2], 3, 4, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.z_gyro_label, 3, 5, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.empty, 0, 5, 5, 2)

        # Accelerometer
        self.select_window.layout.addWidget(self.alabel, 0, 8, 1, 2, Qt.AlignCenter)

        self.select_window.layout.addWidget(self.checkers[3], 1, 8, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.x_acc_label, 1, 9, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[4], 2, 8, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.y_acc_label, 2, 9, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[5], 3, 8, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.z_acc_label, 3, 9, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.empty, 0, 10, 5, 2)

        # Magnetometer
        self.select_window.layout.addWidget(self.mlabel, 0, 12, 1, 2, Qt.AlignCenter)

        self.select_window.layout.addWidget(self.checkers[6], 1, 12, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.x_mag_label, 1, 13, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[7], 2, 12, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.y_mag_label, 2, 13, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[8], 3, 12, 1, 1, Qt.AlignCenter)
        self.select_window.layout.addWidget(self.z_mag_label, 3, 13, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.empty, 0, 14, 5, 2)

        # Other
        self.select_window.layout.addWidget(self.others, 0, 16, 1, 2, Qt.AlignCenter)

        self.select_window.layout.addWidget(self.checkers[9], 1, 16, 1, 1, Qt.AlignCenter)  # imu_counter
        self.select_window.layout.addWidget(self.imu_counter_label, 1, 17, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[10], 2, 16, 1, 1, Qt.AlignCenter)  # rssi_data
        self.select_window.layout.addWidget(self.rssi_data_label, 2, 17, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[11], 3, 16, 1, 1, Qt.AlignCenter)  # imu_temp
        self.select_window.layout.addWidget(self.imu_temp_label, 3, 17, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[12], 4, 16, 1, 1, Qt.AlignCenter)  # imu_pressure
        self.select_window.layout.addWidget(self.imu_pressure_label, 4, 17, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[13], 5, 16, 1, 1, Qt.AlignCenter)  # glob_temp
        self.select_window.layout.addWidget(self.glob_temp_label, 5, 17, 1, 1, Qt.AlignLeft)

        self.select_window.layout.addWidget(self.checkers[14], 6, 16, 1, 1, Qt.AlignCenter)  # battery
        self.select_window.layout.addWidget(self.battery_label, 6, 17, 1, 1, Qt.AlignLeft)

        self.select_window.setLayout(self.select_window.layout)
        return self.select_window     

    # #############   BOX 3   ############ #
    # Box covers RAW/SI Group box with buttons (RAW and SI)
    def StandardsBox(self):
        self.Standards_box = QGroupBox()
        self.Standards_box.setFixedHeight(170)
        self.Standards_box.setFixedWidth(100)
        self.Standards_box.setTitle("Units")
        self.Standards_box.setStyleSheet("QGroupBox { background-color: rgb(250, 250, 250);"
                                         "border: 1px solid rgb(150, 150, 150);"
                                         "border-radius: 2px;"
                                         "margin-top: 6px; }"
                                         "QGroupBox::title {subcontrol-origin: margin;"
                                         "left: 7px;"
                                         "padding: -4px 5px 0px 5px }")

        self.Standards_box.layout = QGridLayout()
        self.Standards_box.layout.addWidget(self.RButton(), 0, 0, 1, 1, Qt.AlignCenter)
        self.Standards_box.layout.addWidget(self.SButton(), 1, 0, 1, 1, Qt.AlignCenter)
        self.Standards_box.setLayout(self.Standards_box.layout)
        return self.Standards_box

    # Button RAW
    def RButton(self):
        self.RAWButton = QPushButton("RAW")
        self.RAWButton.setFont(QFont("Calibri", 12))
        self.RAWButton.setStyleSheet("background: #f0f5f5")
        self.RAWButton.setCheckable(True)
        self.RAWButton.setEnabled(False)
        self.RAWButton.setChecked(True)
        return self.RAWButton
        
    # Button SI
    def SButton(self):
        self.SIButton = QPushButton("SI")
        self.SIButton.setFont(QFont("Calibri", 12))
        self.SIButton.setStyleSheet("background: #f0f5f5")
        self.SIButton.setCheckable(True)
        self.SIButton.setEnabled(False)
        return self.SIButton

    ############ BOX 4 ############
    # A QLabel in QGroupbox displaying loaded file
    def urlwindow(self):
        self.url_window = QGroupBox()
        self.url_window.setFixedHeight(40)
        self.url_window.setTitle("File path")
        self.url_window.setStyleSheet("QGroupBox { background-color: rgb(250, 250, 250);"
                                      "border: 1px solid rgb(150, 150, 150);"
                                      "border-radius: 2px;"
                                      "margin-top: 6px; }"
                                      "QGroupBox::title {subcontrol-origin: margin;"
                                      "left: 7px;"
                                      "padding: -4px 5px 0px 5px }")

        self.url_window.layout = QGridLayout()
        self.url_label = QLabel("No file selected!")
        self.url_window.layout.addWidget(self.url_label)
        self.url_window.setLayout(self.url_window.layout)
        return self.url_window
        
    ########################### BOX 5 ########################################
    # Imu lost data label window
    def LostIMUS(self):        
        self.Lost_IMU = QGroupBox()
        self.Lost_IMU.setContentsMargins(0, 0, 0, 0)
        self.Lost_IMU.setFixedHeight(170)
        self.Lost_IMU.setFixedWidth(135)
        self.Lost_IMU.setTitle("IMU data")
        self.Lost_IMU.setStyleSheet("QGroupBox { background-color: rgb(250, 250, 250);"
                                    " border: 1px solid rgb(150, 150, 150);"
                                    "border-radius: 2px;"
                                    "margin-top: 6px; }"
                                    "QGroupBox::title {subcontrol-origin: margin;"
                                    "left: 7px;"
                                    "padding: -4px 5px 0px 5px }")
        self.Lost_IMU.setFont(QFont("Calibri", 10))

        # Label to display
        self.Lost_label = QLabel()
        self.Lost_label.setText("Lost data:\nIMU 1: 0/0\nIMU 2: 0/0\nIMU 3: 0/0\nIMU 4: 0/0\nIMU 5: 0/0\nIMU 6: 0/0"
                                "\nFilter settings:\nGyroscope: None\nAccelerometer: None")
        self.Lost_label.setAlignment(Qt.AlignCenter)

        # Merge Button to Load_data_window groupbox
        self.Lost_IMU.layout = QGridLayout()
        self.Lost_IMU.setContentsMargins(0, 0, 0, 0)
        self.Lost_IMU.layout.addWidget(self.Lost_label, 1, 1, 1, 1, Qt.AlignCenter)
        self.Lost_IMU.setLayout(self.Lost_IMU.layout)
        return self.Lost_IMU

    @pyqtSlot()
    def change_format_raw(self):
        labelStyle = {'font-size': '8pt'}
        self.display_graph.setLabel('left', 'RAW ADC DATA', color='k', **labelStyle)
        self.RAWButton.setChecked(True)
        self.RAWButton.setEnabled(False)
        self.SIButton.setChecked(False)
        self.SIButton.setEnabled(True)
        self.Switch_index = 0

        self.x_gyro_label.setText("X")
        self.y_gyro_label.setText("Y")
        self.z_gyro_label.setText("Z")
        self.x_acc_label.setText("X")
        self.y_acc_label.setText("Y")
        self.z_acc_label.setText("Z")
        self.x_mag_label.setText("X")
        self.y_mag_label.setText("Y")
        self.z_mag_label.setText("Z")
        self.imu_counter_label.setText("Counter")
        self.rssi_data_label.setText("RSSi [dBm]")
        self.imu_temp_label.setText("IMU Temperature")
        self.imu_pressure_label.setText("Pressure")
        self.glob_temp_label.setText("Temperature")
        self.battery_label.setText("Battery")

        try:
            for i in range(len(self.plotter)):
                self.plotter[i].clear()
            self.display_data_fun()

        except:
            print("Something wrong in change_format_raw")

    def change_format_si(self):
        labelStyle = {'font-size': '8pt'}
        self.display_graph.setLabel('left', 'SI', color='k', **labelStyle)
        self.SIButton.setChecked(True)
        self.RAWButton.setChecked(False)
        self.RAWButton.setEnabled(True)
        self.SIButton.setEnabled(False)
        self.Switch_index = 1

        self.x_gyro_label.setText("X [°/s]")
        self.y_gyro_label.setText("Y [°/s]")
        self.z_gyro_label.setText("Z [°/s]")
        self.x_acc_label.setText("X [m/s\u00b2]")
        self.y_acc_label.setText("Y [m/s\u00b2]")
        self.z_acc_label.setText("Z [m/s\u00b2]")
        self.x_mag_label.setText("X [\u03BCT]")
        self.y_mag_label.setText("Y [\u03BCT]")
        self.z_mag_label.setText("Z [\u03BCT]")
        self.imu_counter_label.setText("Counter")
        self.rssi_data_label.setText("RSSi [dBm]")
        self.imu_temp_label.setText("IMU Temperature [°C]")
        self.imu_pressure_label.setText("Pressure [mBar]")
        self.glob_temp_label.setText("Temperature [°C]")
        self.battery_label.setText("Battery [V]")

        try:
            for i in range(len(self.plotter)):
                self.plotter[i].clear()
            self.display_data_fun()
        except:
            print("Something wrong in change_format_si")

    def LoadFile(self):
        path = QFileDialog.getOpenFileName(self, "Select txt file", "", "Text files (*.txt)")[0]
        try:
            if path:
                self.url_label.setText("Loading... Please wait")
                QApplication.processEvents()
                new_time = time.perf_counter()
                self.splited_data = []
                self.axis = []

                with open(path, 'r') as f:
                    loaded = f.readlines()
                    f.close()

                # Find start of sample data and put them to variable
                count = 0
                cga = 0
                for i in range(100):
                    a = loaded[i].split(',')
                    count += 1
                    if a[0] == '1809' or a[0] == '1810' or a[0] == '1811' or a[0] == '1812' or a[0] == '1813':
                        print(count)
                        break

                for i in range(count - 1, len(loaded)):
                    self.splited_data.append(loaded[i].split(','))

                # Creating list for x axis
                for i in range(len(self.splited_data)):
                    self.axis.append(self.splited_data[i][150])

                # Get filter data
                for i in range(10):
                    b = loaded[i].split(',')
                    cga += 1
                    if "Gyroscrope" in b[0]:
                        temp = b[0].split(' ')
                        self.filters_data[0] = int(temp[1])
                        self.filters_data[1] = int(temp[4])
                        temp.clear()
                        break

                self.axis = list(map(int, self.axis))

                self.gxes(), self.gyes(), self.gzes()
                self.axes(), self.ayes(), self.azes()
                self.mxes(), self.myes(), self.mzes()
                self.Temp1(), self.counter(), self.rssi(), self.rssi_first(), self.Pressure(), self.MT(), self.Battery()

                self.url_label.setText("Selected file: {}".format(path))  # File path loaded to "File path" Groupbox

                for i in range(15):
                    self.checkers[i].setEnabled(False)

                self.imu1.setChecked(False)
                self.imu2.setChecked(False)
                self.imu3.setChecked(False)
                self.imu4.setChecked(False)
                self.imu5.setChecked(False)
                self.imu6.setChecked(False)

                self.imu1.setEnabled(True)
                self.imu2.setEnabled(True)
                self.imu3.setEnabled(True)
                self.imu4.setEnabled(True)
                self.imu5.setEnabled(True)
                self.imu6.setEnabled(True)
                self.txt = []

                for i in range(6):
                    self.txt.append(hex(int(self.splited_data[0][25 * i])))

                self.imu1_label.setText("IMU " + str(self.txt[0]))
                self.imu2_label.setText("IMU " + str(self.txt[1]))
                self.imu3_label.setText("IMU " + str(self.txt[2]))
                self.imu4_label.setText("IMU " + str(self.txt[3]))
                self.imu5_label.setText("IMU " + str(self.txt[4]))
                self.imu6_label.setText("IMU " + str(self.txt[5]))

                # lost data function call
                self.IMU_lost_data()
                self.SIButton.setEnabled(True)
                print(str(round(time.perf_counter()-new_time, 3)) + " secs")

            else:
                pass
                print("No file selected!")

        except:
            self.url_label.setText("WRONG DATA OR FILE IS NOT SUPPORTED!")

    def IMU_lost_data(self):
        lost = [0, 0, 0, 0, 0, 0]

        for i in range(len(self.Count[0])):
            if self.Count[0][i] == 0:
                lost[0] += 1

            if self.Count[1][i] == 0:
                lost[1] += 1

            if self.Count[2][i] == 0:
                lost[2] += 1

            if self.Count[3][i] == 0:
                lost[3] += 1

            if self.Count[4][i] == 0:
                lost[4] += 1

            if self.Count[5][i] == 0:
                lost[5] += 1

        lengthof = len(self.Count[0])
        varis = []
        for i in range(6):
            varis.append("{}: {}/{}".format(self.txt[i], lost[i], lengthof))

        self.Lost_label.setText("Lost data:\n" +
                                varis[0] + '\n' +
                                varis[1] + '\n' +
                                varis[2] + '\n' +
                                varis[3] + '\n' +
                                varis[4] + '\n' +
                                varis[5] + '\n' +
                                "Filter settings:" + '\n' +
                                "Gyroscope: \u00B1{}".format(self.filters_data[0]) + '\n' +
                                "Accelerometer: \u00B1{}".format(self.filters_data[1]))

    # Estimating the receive signal power
    def RSSI_RX_Level(self, C, N):
        a64 = 121.74
        try:
            if C != 0 and N != 0:
                self.rx_l = 10 * math.log10((C * 2 ** 17) / N ** 2) - a64
            else:
                self.rx_l = 0
        except:
            self.rx_l = self.rx_l

        return round(self.rx_l, 2)

    def RSSI_First_path(self, f1, f2, f3, n):
        A = 121.74
        try:
            if n != 0:
                self.FPPL_l = 10 * math.log10((f1 ** 2 + f2 ** 2 + f3 ** 2) / (n ** 2)) - A
            else:
                self.FPPL_l = 0
        except:
            self.FPPL_l = self.FPPL_l

        return round(self.FPPL_l, 2)

    #####################################

    def gxes(self):
        x1, x2, x3, x4, x5, x6 = [], [], [], [], [], []
        self.GyroX = []
        self.GyroXX = []
        for i in range(len(self.splited_data)):
            x1.append(self.splited_data[i][1])
            x2.append(self.splited_data[i][26])
            x3.append(self.splited_data[i][51])
            x4.append(self.splited_data[i][76])
            x5.append(self.splited_data[i][101])
            x6.append(self.splited_data[i][126])

    #if self.Switch_index == 0:
        self.GyroX.append([np.int16(i) for i in x1])
        self.GyroX.append([np.int16(i) for i in x2])
        self.GyroX.append([np.int16(i) for i in x3])
        self.GyroX.append([np.int16(i) for i in x4])
        self.GyroX.append([np.int16(i) for i in x5])
        self.GyroX.append([np.int16(i) for i in x6])

    #elif self.Switch_index == 1:
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x1])
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x2])
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x3])
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x4])
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x5])
        self.GyroXX.append([(np.int16(i) / 32768) * self.filters_data[0] for i in x6])

    def gyes(self):
        y1, y2, y3, y4, y5, y6 = [], [], [], [], [], []
        self.GyroY = []
        self.GyroYY = []
        for i in range(len(self.splited_data)):
            y1.append(self.splited_data[i][2])
            y2.append(self.splited_data[i][27])
            y3.append(self.splited_data[i][52])
            y4.append(self.splited_data[i][77])
            y5.append(self.splited_data[i][102])
            y6.append(self.splited_data[i][127])

    #if self.Switch_index == 0:
        self.GyroY.append([np.int16(i) for i in y1])
        self.GyroY.append([np.int16(i) for i in y2])
        self.GyroY.append([np.int16(i) for i in y3])
        self.GyroY.append([np.int16(i) for i in y4])
        self.GyroY.append([np.int16(i) for i in y5])
        self.GyroY.append([np.int16(i) for i in y6])

    #elif self.Switch_index == 1:
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y1])
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y2])
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y3])
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y4])
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y5])
        self.GyroYY.append([(np.int16(i) / 32768) * self.filters_data[0] for i in y6])

    def gzes(self):
        z1, z2, z3, z4, z5, z6 = [], [], [], [], [], []
        self.GyroZ = []
        self.GyroZZ = []
        for i in range(len(self.splited_data)):
            z1.append(self.splited_data[i][3])
            z2.append(self.splited_data[i][28])
            z3.append(self.splited_data[i][53])
            z4.append(self.splited_data[i][78])
            z5.append(self.splited_data[i][103])
            z6.append(self.splited_data[i][128])

    #if self.Switch_index == 0:
        self.GyroZ.append([np.int16(i) for i in z1])
        self.GyroZ.append([np.int16(i) for i in z2])
        self.GyroZ.append([np.int16(i) for i in z3])
        self.GyroZ.append([np.int16(i) for i in z4])
        self.GyroZ.append([np.int16(i) for i in z5])
        self.GyroZ.append([np.int16(i) for i in z6])

    #elif self.Switch_index == 1:
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z1])
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z2])
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z3])
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z4])
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z5])
        self.GyroZZ.append([(np.int16(i) / 32768) * self.filters_data[0] for i in z6])

    def axes(self):
        x1, x2, x3, x4, x5, x6 = [], [], [], [], [], []
        self.AccX = []
        self.AccXX = []
        for i in range(len(self.splited_data)):
            x1.append(self.splited_data[i][4])
            x2.append(self.splited_data[i][29])
            x3.append(self.splited_data[i][54])
            x4.append(self.splited_data[i][79])
            x5.append(self.splited_data[i][104])
            x6.append(self.splited_data[i][129])

    #if self.Switch_index == 0:
        self.AccX.append([np.int16(i) for i in x1])
        self.AccX.append([np.int16(i) for i in x2])
        self.AccX.append([np.int16(i) for i in x3])
        self.AccX.append([np.int16(i) for i in x4])
        self.AccX.append([np.int16(i) for i in x5])
        self.AccX.append([np.int16(i) for i in x6])

    #elif self.Switch_index == 1:
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x1])
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x2])
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x3])
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x4])
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x5])
        self.AccXX.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in x6])

    def ayes(self):
        y1, y2, y3, y4, y5, y6 = [], [], [], [], [], []
        self.AccY = []
        self.AccYY = []
        for i in range(len(self.splited_data)):
            y1.append(self.splited_data[i][5])
            y2.append(self.splited_data[i][30])
            y3.append(self.splited_data[i][55])
            y4.append(self.splited_data[i][80])
            y5.append(self.splited_data[i][105])
            y6.append(self.splited_data[i][130])

    #if self.Switch_index == 0:
        self.AccY.append([np.int16(i) for i in y1])
        self.AccY.append([np.int16(i) for i in y2])
        self.AccY.append([np.int16(i) for i in y3])
        self.AccY.append([np.int16(i) for i in y4])
        self.AccY.append([np.int16(i) for i in y5])
        self.AccY.append([np.int16(i) for i in y6])

    #elif self.Switch_index == 1:
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y1])
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y2])
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y3])
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y4])
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y5])
        self.AccYY.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in y6])

    def azes(self):
        z1, z2, z3, z4, z5, z6 = [], [], [], [], [], []
        self.AccZ = []
        self.AccZZ = []
        for i in range(len(self.splited_data)):
            z1.append(self.splited_data[i][6])
            z2.append(self.splited_data[i][31])
            z3.append(self.splited_data[i][56])
            z4.append(self.splited_data[i][81])
            z5.append(self.splited_data[i][106])
            z6.append(self.splited_data[i][131])

    #if self.Switch_index == 0:
        self.AccZ.append([np.int16(i) for i in z1])
        self.AccZ.append([np.int16(i) for i in z2])
        self.AccZ.append([np.int16(i) for i in z3])
        self.AccZ.append([np.int16(i) for i in z4])
        self.AccZ.append([np.int16(i) for i in z5])
        self.AccZ.append([np.int16(i) for i in z6])

    #elif self.Switch_index == 1:
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z1])
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z2])
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z3])
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z4])
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z5])
        self.AccZZ.append([(np.int16(i) / 32768) * self.filters_data[1] * 9.8 for i in z6])

    def mxes(self):
        x1, x2, x3, x4, x5, x6 = [], [], [], [], [], []
        self.MagX = []
        self.MagXX = []
        for i in range(len(self.splited_data)):
            x1.append(self.splited_data[i][7])
            x2.append(self.splited_data[i][32])
            x3.append(self.splited_data[i][57])
            x4.append(self.splited_data[i][82])
            x5.append(self.splited_data[i][107])
            x6.append(self.splited_data[i][132])

    #if self.Switch_index == 0:
        self.MagX.append([np.int16(i) for i in x1])
        self.MagX.append([np.int16(i) for i in x2])
        self.MagX.append([np.int16(i) for i in x3])
        self.MagX.append([np.int16(i) for i in x4])
        self.MagX.append([np.int16(i) for i in x5])
        self.MagX.append([np.int16(i) for i in x6])

    #elif self.Switch_index == 1:
        self.MagXX.append([np.int16(i) * 0.15 for i in x1])
        self.MagXX.append([np.int16(i) * 0.15 for i in x2])
        self.MagXX.append([np.int16(i) * 0.15 for i in x3])
        self.MagXX.append([np.int16(i) * 0.15 for i in x4])
        self.MagXX.append([np.int16(i) * 0.15 for i in x5])
        self.MagXX.append([np.int16(i) * 0.15 for i in x6])

    def myes(self):
        y1, y2, y3, y4, y5, y6 = [], [], [], [], [], []
        self.MagY = []
        self.MagYY = []
        for i in range(len(self.splited_data)):
            y1.append(self.splited_data[i][8])
            y2.append(self.splited_data[i][33])
            y3.append(self.splited_data[i][58])
            y4.append(self.splited_data[i][83])
            y5.append(self.splited_data[i][108])
            y6.append(self.splited_data[i][133])

    #if self.Switch_index == 0:
        self.MagY.append([np.int16(i) for i in y1])
        self.MagY.append([np.int16(i) for i in y2])
        self.MagY.append([np.int16(i) for i in y3])
        self.MagY.append([np.int16(i) for i in y4])
        self.MagY.append([np.int16(i) for i in y5])
        self.MagY.append([np.int16(i) for i in y6])

    #elif self.Switch_index == 1:
        self.MagYY.append([np.int16(i) * 0.15 for i in y1])
        self.MagYY.append([np.int16(i) * 0.15 for i in y2])
        self.MagYY.append([np.int16(i) * 0.15 for i in y3])
        self.MagYY.append([np.int16(i) * 0.15 for i in y4])
        self.MagYY.append([np.int16(i) * 0.15 for i in y5])
        self.MagYY.append([np.int16(i) * 0.15 for i in y6])

    def mzes(self):
        z1, z2, z3, z4, z5, z6 = [], [], [], [], [], []
        self.MagZ = []
        self.MagZZ = []
        for i in range(len(self.splited_data)):
            z1.append(self.splited_data[i][9])
            z2.append(self.splited_data[i][34])
            z3.append(self.splited_data[i][59])
            z4.append(self.splited_data[i][84])
            z5.append(self.splited_data[i][109])
            z6.append(self.splited_data[i][134])

    #if self.Switch_index == 0:
        self.MagZ.append([np.int16(i) for i in z1])
        self.MagZ.append([np.int16(i) for i in z2])
        self.MagZ.append([np.int16(i) for i in z3])
        self.MagZ.append([np.int16(i) for i in z4])
        self.MagZ.append([np.int16(i) for i in z5])
        self.MagZ.append([np.int16(i) for i in z6])

    #elif self.Switch_index == 1:
        self.MagZZ.append([np.int16(i) * 0.15 for i in z1])
        self.MagZZ.append([np.int16(i) * 0.15 for i in z2])
        self.MagZZ.append([np.int16(i) * 0.15 for i in z3])
        self.MagZZ.append([np.int16(i) * 0.15 for i in z4])
        self.MagZZ.append([np.int16(i) * 0.15 for i in z5])
        self.MagZZ.append([np.int16(i) * 0.15 for i in z6])

    def Temp1(self):
        t1, t2, t3, t4, t5, t6 = [], [], [], [], [], []
        self.temp_1 = []
        self.temp_1E = []
        for i in range(len(self.splited_data)):
            t1.append(self.splited_data[i][10])
            t2.append(self.splited_data[i][35])
            t3.append(self.splited_data[i][60])
            t4.append(self.splited_data[i][85])
            t5.append(self.splited_data[i][110])
            t6.append(self.splited_data[i][135])

        self.temp_1.append([int(i) for i in t1])
        self.temp_1.append([int(i) for i in t2])
        self.temp_1.append([int(i) for i in t3])
        self.temp_1.append([int(i) for i in t4])
        self.temp_1.append([int(i) for i in t5])
        self.temp_1.append([int(i) for i in t6])

        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t1])
        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t2])
        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t3])
        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t4])
        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t5])
        self.temp_1E.append([np.int16(i) / 333.87 + 21 for i in t6])

    def counter(self):
        c1, c2, c3, c4, c5, c6 = [], [], [], [], [], []
        self.Count = []
        for i in range(len(self.splited_data)):
            c1.append(self.splited_data[i][24])
            c2.append(self.splited_data[i][49])
            c3.append(self.splited_data[i][74])
            c4.append(self.splited_data[i][99])
            c5.append(self.splited_data[i][124])
            c6.append(self.splited_data[i][149])

        self.Count.append(list(map(int, c1)))
        self.Count.append(list(map(int, c2)))
        self.Count.append(list(map(int, c3)))
        self.Count.append(list(map(int, c4)))
        self.Count.append(list(map(int, c5)))
        self.Count.append(list(map(int, c6)))

    def rssi(self):
        r1, r2, r3, r4, r5, r6 = [], [], [], [], [], []
        self.rs_si = []
        for i in range(len(self.splited_data)):
            r1.append(self.RSSI_RX_Level(int(self.splited_data[i][11]), int(self.splited_data[i][12])))
            r2.append(self.RSSI_RX_Level(int(self.splited_data[i][36]), int(self.splited_data[i][37])))
            r3.append(self.RSSI_RX_Level(int(self.splited_data[i][61]), int(self.splited_data[i][62])))
            r4.append(self.RSSI_RX_Level(int(self.splited_data[i][86]), int(self.splited_data[i][87])))
            r5.append(self.RSSI_RX_Level(int(self.splited_data[i][111]), int(self.splited_data[i][112])))
            r6.append(self.RSSI_RX_Level(int(self.splited_data[i][136]), int(self.splited_data[i][137])))

        self.rs_si.append(list(map(int, r1)))
        self.rs_si.append(list(map(int, r2)))
        self.rs_si.append(list(map(int, r3)))
        self.rs_si.append(list(map(int, r4)))
        self.rs_si.append(list(map(int, r5)))
        self.rs_si.append(list(map(int, r6)))

    def rssi_first(self):
        rs1, rs2, rs3, rs4, rs5, rs6 = [], [], [], [], [], []
        self.rs_first = []
        for i in range(len(self.splited_data)):
            rs1.append(self.RSSI_First_path(int(self.splited_data[i][16]), int(self.splited_data[i][17]),
                                            int(self.splited_data[i][18]), int(self.splited_data[i][12])))
            rs2.append(self.RSSI_First_path(int(self.splited_data[i][41]), int(self.splited_data[i][42]),
                                            int(self.splited_data[i][43]), int(self.splited_data[i][37])))
            rs3.append(self.RSSI_First_path(int(self.splited_data[i][66]), int(self.splited_data[i][67]),
                                            int(self.splited_data[i][68]), int(self.splited_data[i][62])))
            rs4.append(self.RSSI_First_path(int(self.splited_data[i][91]), int(self.splited_data[i][92]),
                                            int(self.splited_data[i][93]), int(self.splited_data[i][87])))
            rs5.append(self.RSSI_First_path(int(self.splited_data[i][116]), int(self.splited_data[i][117]),
                                            int(self.splited_data[i][118]), int(self.splited_data[i][112])))
            rs6.append(self.RSSI_First_path(int(self.splited_data[i][141]), int(self.splited_data[i][142]),
                                            int(self.splited_data[i][143]), int(self.splited_data[i][137])))

        self.rs_first.append(list(map(int, rs1)))
        self.rs_first.append(list(map(int, rs2)))
        self.rs_first.append(list(map(int, rs3)))
        self.rs_first.append(list(map(int, rs4)))
        self.rs_first.append(list(map(int, rs5)))
        self.rs_first.append(list(map(int, rs6)))

    def Pressure(self):
        p1, p2, p3, p4, p5, p6 = [], [], [], [], [], []
        self.press = []
        self.pressE = []
        for i in range(len(self.splited_data)):
            p1.append(self.splited_data[i][22])
            p2.append(self.splited_data[i][47])
            p3.append(self.splited_data[i][72])
            p4.append(self.splited_data[i][97])
            p5.append(self.splited_data[i][122])
            p6.append(self.splited_data[i][147])

    #if self.Switch_index == 0:
        self.press.append([np.int16(i) for i in p1])
        self.press.append([np.int16(i) for i in p2])
        self.press.append([np.int16(i) for i in p3])
        self.press.append([np.int16(i) for i in p4])
        self.press.append([np.int16(i) for i in p5])
        self.press.append([np.int16(i) for i in p6])

    #elif self.Switch_index == 1:
        self.pressE.append([np.int16(i) / 10 for i in p1])
        self.pressE.append([np.int16(i) / 10 for i in p2])
        self.pressE.append([np.int16(i) / 10 for i in p3])
        self.pressE.append([np.int16(i) / 10 for i in p4])
        self.pressE.append([np.int16(i) / 10 for i in p5])
        self.pressE.append([np.int16(i) / 10 for i in p6])

    def MT(self):
        m1, m2, m3, m4, m5, m6 = [], [], [], [], [], []
        self.MTemp = []
        self.MTempE = []
        for i in range(len(self.splited_data)):
            m1.append(self.splited_data[i][21])
            m2.append(self.splited_data[i][46])
            m3.append(self.splited_data[i][71])
            m4.append(self.splited_data[i][96])
            m5.append(self.splited_data[i][121])
            m6.append(self.splited_data[i][146])

    #if self.Switch_index == 0:
        self.MTemp.append([np.int16(i) for i in m1])
        self.MTemp.append([np.int16(i) for i in m2])
        self.MTemp.append([np.int16(i) for i in m3])
        self.MTemp.append([np.int16(i) for i in m4])
        self.MTemp.append([np.int16(i) for i in m5])
        self.MTemp.append([np.int16(i) for i in m6])

    #elif self.Switch_index == 1:
        self.MTempE.append([np.int16(i) / 100 for i in m1])
        self.MTempE.append([np.int16(i) / 100 for i in m2])
        self.MTempE.append([np.int16(i) / 100 for i in m3])
        self.MTempE.append([np.int16(i) / 100 for i in m4])
        self.MTempE.append([np.int16(i) / 100 for i in m5])
        self.MTempE.append([np.int16(i) / 100 for i in m6])

    def Battery(self):
        b1, b2, b3, b4, b5, b6 = [], [], [], [], [], []
        self.Bat = []
        self.BatE = []
        for i in range(len(self.splited_data)):
            b1.append(self.splited_data[i][23])
            b2.append(self.splited_data[i][48])
            b3.append(self.splited_data[i][73])
            b4.append(self.splited_data[i][98])
            b5.append(self.splited_data[i][123])
            b6.append(self.splited_data[i][148])

    #if self.Switch_index == 0:
        self.Bat.append([np.int16(i) for i in b1])
        self.Bat.append([np.int16(i) for i in b2])
        self.Bat.append([np.int16(i) for i in b3])
        self.Bat.append([np.int16(i) for i in b4])
        self.Bat.append([np.int16(i) for i in b5])
        self.Bat.append([np.int16(i) for i in b6])

    #elif self.Switch_index == 1:
        self.BatE.append([np.int16(i) / 1000 for i in b1])
        self.BatE.append([np.int16(i) / 1000 for i in b2])
        self.BatE.append([np.int16(i) / 1000 for i in b3])
        self.BatE.append([np.int16(i) / 1000 for i in b4])
        self.BatE.append([np.int16(i) / 1000 for i in b5])
        self.BatE.append([np.int16(i) / 1000 for i in b6])

    @pyqtSlot()
    def display_data_fun(self):
        if self.imu1.isChecked():
            self.ims(0)
            self.imu1.setEnabled(True)
            self.imu2.setEnabled(False)
            self.imu3.setEnabled(False)
            self.imu4.setEnabled(False)
            self.imu5.setEnabled(False)
            self.imu6.setEnabled(False)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        elif self.imu2.isChecked():
            self.ims(1)
            self.imu1.setEnabled(False)
            self.imu2.setEnabled(True)
            self.imu3.setEnabled(False)
            self.imu4.setEnabled(False)
            self.imu5.setEnabled(False)
            self.imu6.setEnabled(False)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        elif self.imu3.isChecked():
            self.ims(2)
            self.imu1.setEnabled(False)
            self.imu2.setEnabled(False)
            self.imu3.setEnabled(True)
            self.imu4.setEnabled(False)
            self.imu5.setEnabled(False)
            self.imu6.setEnabled(False)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        elif self.imu4.isChecked():
            self.ims(3)
            self.imu1.setEnabled(False)
            self.imu2.setEnabled(False)
            self.imu3.setEnabled(False)
            self.imu4.setEnabled(True)
            self.imu5.setEnabled(False)
            self.imu6.setEnabled(False)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        elif self.imu5.isChecked():
            self.ims(4)
            self.imu1.setEnabled(False)
            self.imu2.setEnabled(False)
            self.imu3.setEnabled(False)
            self.imu4.setEnabled(False)
            self.imu5.setEnabled(True)
            self.imu6.setEnabled(False)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        elif self.imu6.isChecked():
            self.ims(5)
            self.imu1.setEnabled(False)
            self.imu2.setEnabled(False)
            self.imu3.setEnabled(False)
            self.imu4.setEnabled(False)
            self.imu5.setEnabled(False)
            self.imu6.setEnabled(True)
            for j in range(15):
                self.checkers[j].setEnabled(True)
        else:
            self.imu1.setEnabled(True)
            self.imu2.setEnabled(True)
            self.imu3.setEnabled(True)
            self.imu4.setEnabled(True)
            self.imu5.setEnabled(True)
            self.imu6.setEnabled(True)
            for i in range(15):
                self.checkers[i].setChecked(False)
            for i in range(len(self.plotter)):
                self.plotter[i].clear()
            for j in range(15):
                self.checkers[j].setEnabled(False)

    def ims(self, ind):
        if self.Switch_index == 0:
            if self.checkers[0].isChecked():
                self.plotter[0].setData(self.axis, self.GyroX[ind])
            else:
                self.plotter[0].clear()

            if self.checkers[1].isChecked():
                self.plotter[1].setData(self.axis, self.GyroY[ind])
            else:
                self.plotter[1].clear()

            if self.checkers[2].isChecked():
                self.plotter[2].setData(self.axis, self.GyroZ[ind])
            else:
                self.plotter[2].clear()

            if self.checkers[3].isChecked():
                self.plotter[3].setData(self.axis, self.AccX[ind])
            else:
                self.plotter[3].clear()

            if self.checkers[4].isChecked():
                self.plotter[4].setData(self.axis, self.AccY[ind])
            else:
                self.plotter[4].clear()

            if self.checkers[5].isChecked():
                self.plotter[5].setData(self.axis, self.AccZ[ind])
            else:
                self.plotter[5].clear()

            if self.checkers[6].isChecked():
                self.plotter[6].setData(self.axis, self.MagX[ind])
            else:
                self.plotter[6].clear()

            if self.checkers[7].isChecked():
                self.plotter[7].setData(self.axis, self.MagY[ind])
            else:
                self.plotter[7].clear()

            if self.checkers[8].isChecked():
                self.plotter[8].setData(self.axis, self.MagZ[ind])
            else:
                self.plotter[8].clear()

            if self.checkers[9].isChecked():
                self.plotter[9].setData(self.axis, self.Count[ind])
            else:
                self.plotter[9].clear()

            if self.checkers[10].isChecked():
                self.plotter[10].setData(self.axis, self.rs_si[ind])
                self.plotter[11].setData(self.axis, self.rs_first[ind])
            else:
                self.plotter[10].clear()
                self.plotter[11].clear()

            if self.checkers[11].isChecked():
                self.plotter[12].setData(self.axis, self.temp_1[ind])
            else:
                self.plotter[12].clear()

            if self.checkers[12].isChecked():
                self.plotter[13].setData(self.axis, self.press[ind])
            else:
                self.plotter[13].clear()

            if self.checkers[13].isChecked():
                self.plotter[14].setData(self.axis, self.MTemp[ind])
            else:
                self.plotter[14].clear()

            if self.checkers[14].isChecked():
                self.plotter[15].setData(self.axis, self.Bat[ind])
            else:
                self.plotter[15].clear()

        else:
            if self.checkers[0].isChecked():
                self.plotter[0].setData(self.axis, self.GyroXX[ind])
            else:
                self.plotter[0].clear()

            if self.checkers[1].isChecked():
                self.plotter[1].setData(self.axis, self.GyroYY[ind])
            else:
                self.plotter[1].clear()

            if self.checkers[2].isChecked():
                self.plotter[2].setData(self.axis, self.GyroZZ[ind])
            else:
                self.plotter[2].clear()

            if self.checkers[3].isChecked():
                self.plotter[3].setData(self.axis, self.AccXX[ind])
            else:
                self.plotter[3].clear()

            if self.checkers[4].isChecked():
                self.plotter[4].setData(self.axis, self.AccYY[ind])
            else:
                self.plotter[4].clear()

            if self.checkers[5].isChecked():
                self.plotter[5].setData(self.axis, self.AccZZ[ind])
            else:
                self.plotter[5].clear()

            if self.checkers[6].isChecked():
                self.plotter[6].setData(self.axis, self.MagXX[ind])
            else:
                self.plotter[6].clear()

            if self.checkers[7].isChecked():
                self.plotter[7].setData(self.axis, self.MagYY[ind])
            else:
                self.plotter[7].clear()

            if self.checkers[8].isChecked():
                self.plotter[8].setData(self.axis, self.MagZZ[ind])
            else:
                self.plotter[8].clear()

            if self.checkers[9].isChecked():
                self.plotter[9].setData(self.axis, self.Count[ind])
            else:
                self.plotter[9].clear()

            if self.checkers[10].isChecked():
                self.plotter[10].setData(self.axis, self.rs_si[ind])
                self.plotter[11].setData(self.axis, self.rs_first[ind])
            else:
                self.plotter[10].clear()
                self.plotter[11].clear()

            if self.checkers[11].isChecked():
                self.plotter[12].setData(self.axis, self.temp_1E[ind])
            else:
                self.plotter[12].clear()

            if self.checkers[12].isChecked():
                self.plotter[13].setData(self.axis, self.pressE[ind])
            else:
                self.plotter[13].clear()

            if self.checkers[13].isChecked():
                self.plotter[14].setData(self.axis, self.MTempE[ind])
            else:
                self.plotter[14].clear()

            if self.checkers[14].isChecked():
                self.plotter[15].setData(self.axis, self.BatE[ind])
            else:
                self.plotter[15].clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    exc = DisplaySavedData()
    exc.show()
    sys.exit(app.exec_())
