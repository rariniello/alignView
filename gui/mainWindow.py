import time

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMainWindow

import config
import gui.ui.ui_MainWindow as ui_MainWindow
from backends import camera_basler, camera_test, enumerate_basler, enumerate_test
from gui.worker import Worker


class AlignViewMainWindow(QMainWindow, ui_MainWindow.Ui_AlignView):
    """Class that handles the main window and the gui functionality.

    The camera data source operates in a different thread from th gui.
    """

    request_image = pyqtSignal()
    disconnect = pyqtSignal()
    signal_stop_streaming = pyqtSignal()
    request_parameters = pyqtSignal()
    request_offset_range = pyqtSignal()

    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self.serial_number = None
        self.cam = None
        self.streamig = False
        self.first_image = True
        self.lastTime = time.time()

        self.N_elapsed = 20
        self.elapsed = np.zeros(self.N_elapsed)
        self.i_elapsed = 0

        self.max_level = 4096

        self.setupUi(self)
        self.select_backend()
        self.connect_signal_slots()
        self.setup_plot()
        self.refresh_camera_list()

    def select_backend(self):
        if config.testing:
            self.enumerate_devices = enumerate_test.EnumTest()
            self.camera_class = camera_test.TestCam
        else:
            self.enumerate_devices = enumerate_basler.EnumBasler()
            self.camera_class = camera_basler.Basler

    def connect_signal_slots(self):
        """Connects signals from gui widgets to slots in this class."""
        self.refreshButton.clicked.connect(self.refresh_camera_list)
        self.connectButton.clicked.connect(self.connect_camera)
        self.disconnectButton.clicked.connect(self.disconnect_camera)
        self.startButton.clicked.connect(self.start_streaming)
        self.stopButton.clicked.connect(self.stop_streaming)

    def setup_plot(self):
        view = self.imageView.getView()
        view.disableAutoRange()
        hist = self.imageView.getHistogramWidget()
        hist.setLevels(0.0, self.max_level)
        hist.setHistogramRange(0.0, self.max_level, 0.0)
        hist.vb.enableAutoRange("y", False)
        hist.vb.setLimits(yMin=0.0, yMax=self.max_level, minYRange=10)
        hist.sigLevelsChanged.connect(self.on_levels_changed)
        # hist.vb.setLogMode("x", True)

    def on_levels_changed(self, hist):
        min_level, max_level = hist.getLevels()
        if max_level > self.max_level:
            max_level = self.max_level
        if min_level < 0.0:
            min_level = 0.0
        hist.setLevels(min_level, max_level)

    # Methods for connecting and disconnecting the camera
    # -----------------------------------------------------------------
    def refresh_camera_list(self):
        self.cameraSelectField.clear()
        self.enumerate_devices.enumerate_devices()
        serial_numbers = self.enumerate_devices.get_serial_numbers()
        names = self.enumerate_devices.get_names()
        N = len(serial_numbers)
        if N > 0:
            self.connectButton.setEnabled(True)
        for i in range(N):
            self.cameraSelectField.addItem(
                f"{names[i]} ({serial_numbers[i]})", serial_numbers[i]
            )

    def connect_camera(self):
        self.disconnect_camera()
        self.serial_number = self.cameraSelectField.currentData()
        self.name = self.cameraSelectField.currentText()
        if self.name == "":
            return

        self.statusbar.showMessage("Connecting to camera...")
        # Spawn the worker thread
        self.thread = QThread()
        self.worker = Worker(self.serial_number, self.camera_class)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots to control thread startup and shutdown
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.connect_camera)

        # Connect signals and slots between the worker and the gui
        self.disconnect.connect(self.worker.disconnect_camera)
        self.request_image.connect(self.worker.get_image)
        self.request_parameters.connect(self.worker.get_parameters)
        self.request_offset_range.connect(self.worker.get_offset_range)
        self.signal_stop_streaming.connect(self.worker.stop_streaming)

        self.worker.update.connect(self.doUpdate)
        self.worker.connected.connect(self.onConnect)
        self.worker.parametersUpdated.connect(self.onParametersUpdated)
        self.worker.offsetRangeUpdated.connect(self.onOffsetRangeUpdated)

        self.exposureField.valueChanged.connect(self.worker.change_exposure)
        self.gainField.valueChanged.connect(self.worker.change_gain)
        self.widthField.valueChanged.connect(self.worker.change_width)
        self.heightField.valueChanged.connect(self.worker.change_height)
        self.offsetXField.valueChanged.connect(self.worker.change_offsetX)
        self.offsetYField.valueChanged.connect(self.worker.change_offsetY)

        # Start the thread and set initial spectrometer parameters
        self.thread.start()

    def disconnect_camera(self):
        self.serial_number = None
        self.cam = None
        self.first_image = True
        self.stop_streaming()
        self.disconnect.emit()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.connectButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)
        # self.refreshButton.setEnabled(True)
        self.exposureField.setEnabled(False)
        self.gainField.setEnabled(False)
        self.widthField.setEnabled(False)
        self.heightField.setEnabled(False)
        self.offsetXField.setEnabled(False)
        self.offsetYField.setEnabled(False)

    @pyqtSlot(dict)
    def onConnect(self, parameters):
        """Updates the gui when the camera is connected."""
        self.statusbar.showMessage("Connected to camera {}".format(self.name))
        self.baseMessage = "Connected to camera {} | ".format(self.name)
        self.startButton.setEnabled(True)
        self.connectButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)
        # self.refreshButton.setEnabled(False)
        self.exposureField.setEnabled(True)
        self.gainField.setEnabled(True)
        self.widthField.setEnabled(True)
        self.heightField.setEnabled(True)
        self.offsetXField.setEnabled(True)
        self.offsetYField.setEnabled(True)

        self.onParametersUpdated(parameters)

    @pyqtSlot(dict)
    def onParametersUpdated(self, parameters):
        self.exposureField.setValue(parameters["exposure"])
        self.exposureField.setMinimum(parameters["exposure_range"][0])
        self.exposureField.setMaximum(parameters["exposure_range"][1])

        self.gainField.setValue(parameters["gain"])
        self.gainField.setMinimum(parameters["gain_range"][0])
        self.gainField.setMaximum(parameters["gain_range"][1])

        self.widthField.setValue(parameters["width"])
        self.widthField.setMinimum(parameters["width_range"][0])
        self.widthField.setMaximum(parameters["width_range"][1])

        self.heightField.setValue(parameters["height"])
        self.heightField.setMinimum(parameters["height_range"][0])
        self.heightField.setMaximum(parameters["height_range"][1])

        self.offsetXField.setValue(parameters["offsetX"])
        self.offsetXField.setMinimum(parameters["offsetX_range"][0])
        self.offsetXField.setMaximum(parameters["offsetX_range"][1])

        self.offsetYField.setValue(parameters["offsetY"])
        self.offsetYField.setMinimum(parameters["offsetY_range"][0])
        self.offsetYField.setMaximum(parameters["offsetY_range"][1])
        print(parameters)

    @pyqtSlot(dict)
    def onOffsetRangeUpdated(self, parameters):
        self.offsetXField.setValue(parameters["offsetX"])
        self.offsetXField.setMinimum(parameters["offsetX_range"][0])
        self.offsetXField.setMaximum(parameters["offsetX_range"][1])

        self.offsetYField.setValue(parameters["offsetY"])
        self.offsetYField.setMinimum(parameters["offsetY_range"][0])
        self.offsetYField.setMaximum(parameters["offsetY_range"][1])

    # Methods for streaming data from the camera
    # -----------------------------------------------------------------
    @pyqtSlot(np.ndarray)
    def doUpdate(self, img):
        """Updates the plot/gui when a new image is recieved."""
        # self.img = img
        self.update_plot(img)
        if self.streaming:
            self.request_image.emit()
        self.printFramerate()

    def printFramerate(self):
        """Calculates the framerate and prints it to the statusbar."""
        currentTime = time.time()
        elapsed = currentTime - self.lastTime
        if elapsed == 0:
            return
        self.elapsed[self.i_elapsed] = elapsed
        self.i_elapsed = (self.i_elapsed + 1) % self.N_elapsed
        frameRate = 1.0 / np.average(elapsed)
        self.statusbar.showMessage(
            self.baseMessage + "Streaming at {:0.2f} fps".format(frameRate)
        )
        self.lastTime = currentTime

    @pyqtSlot()
    def start_streaming(self):
        """Starts streaming images from the camera."""
        self.streaming = True
        self.worker.start_streaming()
        self.request_image.emit()
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.widthField.setEnabled(False)
        self.heightField.setEnabled(False)

    @pyqtSlot()
    def stop_streaming(self):
        """Stops streaming images from the camera."""
        self.streaming = False
        # self.worker.stop_streaming()
        self.signal_stop_streaming.emit()
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.widthField.setEnabled(True)
        self.heightField.setEnabled(True)

    def update_plot(self, img):
        if self.first_image:
            self.imageView.setImage(
                img.T, autoRange=True, autoLevels=False, autoHistogramRange=False
            )
            self.first_image = False
        else:
            self.imageView.setImage(
                img.T, autoRange=False, autoLevels=False, autoHistogramRange=False
            )

    def do_request_parameters(self):
        self.request_parameters.emit()
