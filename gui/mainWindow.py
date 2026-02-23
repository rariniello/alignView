import os
import time

import numpy as np
import pyqtgraph as pg
from PyQt6 import QtGui
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

import config
import gui.ui.ui_MainWindow as ui_MainWindow
from backends import camera_basler, camera_test, enumerate_basler, enumerate_test
from gui import lineoutWindow
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
    update = pyqtSignal(dict)

    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self.serial_number = None
        self.streamig = False
        self.first_image = True
        self.lastTime = time.time()

        self.N_elapsed = 20
        self.elapsed = np.zeros(self.N_elapsed)
        self.i_elapsed = 0

        self.max_level = 4096
        self.centroid = np.zeros(2)

        self.setupUi(self)
        self.set_icons()
        self.select_backend()
        self.connect_signal_slots()
        self.setup_plot()
        self.add_crosshairs()
        self.add_circles()
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
        self.bitDepthField.valueChanged.connect(self.on_change_bit_depth)
        self.normalizeCheckBox.checkStateChanged.connect(self.on_normalize_check)
        self.targetCosshairCheckBox.checkStateChanged.connect(
            self.toggle_target_crosshair
        )
        self.beamCenterCheckBox.checkStateChanged.connect(
            self.toggle_centroid_crosshair
        )
        self.targetXField.valueChanged.connect(self.set_target_crosshair_x)
        self.targetYField.valueChanged.connect(self.set_target_crosshair_y)
        self.markBeamButton.clicked.connect(self.mark_beam)
        self.targetCircleCheckBox.checkStateChanged.connect(self.toggle_target_circle)
        self.beamCircleCheckBox.checkStateChanged.connect(self.toggle_centroid_circle)
        self.targetCircleSizeField.valueChanged.connect(self.set_target_circle_size)
        self.beamCircleSizeField.valueChanged.connect(self.set_centroid_circle_size)
        self.displayLineoutsButton.clicked.connect(self.show_lineout_window)

    def set_icons(self):
        icon = QtGui.QIcon()
        path = os.path.join(config.iconPath, "arrow-circle-double-135.png")
        icon.addPixmap(QtGui.QPixmap(path))
        self.refreshButton.setIcon(icon)

    def setup_plot(self):
        plot = pg.PlotItem()
        plot.getViewBox().setDefaultPadding(0)
        self.imageView = pg.ImageView(view=plot)
        self.imageViewWidgetLayout.addWidget(self.imageView)
        self.imageView.ui.roiBtn.hide()
        self.imageView.ui.menuBtn.hide()
        view = self.imageView.getView()
        view.disableAutoRange()
        hist = self.imageView.getHistogramWidget()
        hist.vb.enableAutoRange("y", False)
        self.set_hist_range(self.max_level)
        hist.sigLevelsChanged.connect(self.on_levels_changed)
        cmap = pg.colormap.get("magma")
        hist.gradient.setColorMap(cmap)
        hist.gradient.showTicks(False)

    def set_hist_range(self, max):
        self.max_level = max
        hist = self.imageView.getHistogramWidget()
        hist.setLevels(0.0, self.max_level)
        hist.setHistogramRange(0.0, self.max_level, 0.0)
        hist.vb.setLimits(yMin=0.0, yMax=self.max_level, minYRange=10)

    def add_crosshairs(self):
        self.targetVLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("m", width=1.0)
        )
        self.targetHLine = pg.InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen("m", width=1.0)
        )
        self.targetVLine.setPos(0)
        self.targetHLine.setPos(0)
        self.imageView.addItem(self.targetVLine)
        self.imageView.addItem(self.targetHLine)
        self.targetVLine.setVisible(False)
        self.targetHLine.setVisible(False)

        self.centroidVLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("g", width=1.0)
        )
        self.centroidHLine = pg.InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen("g", width=1.0)
        )
        self.centroidVLine.setPos(0)
        self.centroidHLine.setPos(0)
        self.imageView.addItem(self.centroidVLine)
        self.imageView.addItem(self.centroidHLine)
        self.centroidVLine.setVisible(False)
        self.centroidHLine.setVisible(False)

    def add_circles(self):
        r_target = self.targetCircleSizeField.value()
        self.target_circle = pg.CircleROI(
            pos=(-r_target + 0.5, -r_target + 0.5),
            size=(r_target * 2, r_target * 2),
            pen=pg.mkPen("m", width=1.0),
            movable=False,
            resizable=False,
        )
        self.imageView.addItem(self.target_circle)
        self.target_circle.removeHandle(0)
        self.target_circle.setVisible(False)

        r_centroid = self.beamCircleSizeField.value()
        self.centroid_circle = pg.CircleROI(
            pos=(-r_centroid + 0.5, -r_centroid + 0.5),
            size=(r_centroid * 2, r_centroid * 2),
            pen=pg.mkPen("g", width=1.0),
            movable=False,
            resizable=False,
        )
        self.imageView.addItem(self.centroid_circle)
        self.centroid_circle.removeHandle(0)
        self.centroid_circle.setVisible(False)

    # Methods for connecting and disconnecting the camera
    # -----------------------------------------------------------------
    def refresh_camera_list(self):
        self.cameraSelectField.clear()
        self.enumerate_devices.enumerate_devices()
        serial_numbers = self.enumerate_devices.get_serial_numbers()
        names = self.enumerate_devices.get_names()
        N = len(serial_numbers)
        if N > 0 and (self.serial_number is None):
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
        # self.request_image.connect(self.worker.get_image)
        self.request_parameters.connect(self.worker.get_parameters)
        self.request_offset_range.connect(self.worker.get_offset_range)
        self.signal_stop_streaming.connect(self.worker.stop_streaming)

        self.worker.update.connect(self.doUpdate)
        self.worker.connected.connect(self.onConnect)
        self.worker.connectionFailed.connect(self.onFailedConnect)
        self.worker.parametersUpdated.connect(self.onParametersUpdated)
        self.worker.offsetRangeUpdated.connect(self.update_offset)
        self.worker.binningUpdated.connect(self.update_size_and_offset)
        self.worker.imageTransformUpdated.connect(self.set_image_transform)

        self.exposureField.valueChanged.connect(self.worker.change_exposure)
        self.gainField.valueChanged.connect(self.worker.change_gain)
        self.widthField.valueChanged.connect(self.worker.change_width)
        self.heightField.valueChanged.connect(self.worker.change_height)
        self.offsetXField.valueChanged.connect(self.worker.change_offsetX)
        self.offsetYField.valueChanged.connect(self.worker.change_offsetY)
        self.exposureModeField.currentTextChanged.connect(
            self.worker.change_exposure_mode
        )
        self.triggerModeField.currentTextChanged.connect(
            self.worker.change_trigger_mode
        )
        self.triggerSourceField.currentTextChanged.connect(
            self.worker.change_trigger_source
        )
        self.pixelFormatField.currentTextChanged.connect(
            self.worker.change_pixel_format
        )
        self.binningHorizontalField.valueChanged.connect(
            self.worker.change_binning_horizontal
        )
        self.binningVerticalField.valueChanged.connect(
            self.worker.change_binning_vertical
        )

        # Start the thread and set initial spectrometer parameters
        self.thread.start()

    def disconnect_camera(self):
        self.serial_number = None
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
        self.triggerModeField.setEnabled(False)
        self.triggerSourceField.setEnabled(False)
        self.exposureModeField.setEnabled(False)
        self.pixelFormatField.setEnabled(False)
        self.binningHorizontalField.setEnabled(False)
        self.binningVerticalField.setEnabled(False)

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
        self.triggerModeField.setEnabled(True)
        self.triggerSourceField.setEnabled(True)
        self.exposureModeField.setEnabled(True)
        self.pixelFormatField.setEnabled(True)
        self.binningHorizontalField.setEnabled(True)
        self.binningVerticalField.setEnabled(True)

        self.onParametersUpdated(parameters)

    @pyqtSlot(object)
    def onFailedConnect(self, error):
        QMessageBox.critical(self, "Error: Failed to connect", str(error))
        print(error)

    @pyqtSlot(dict)
    def onParametersUpdated(self, parameters):
        self.exposureField.setValue(parameters["exposure"])
        self.exposureField.setMinimum(parameters["exposure_range"][0])
        self.exposureField.setMaximum(parameters["exposure_range"][1])

        self.gainField.setValue(parameters["gain"])
        self.gainField.setMinimum(parameters["gain_range"][0])
        self.gainField.setMaximum(parameters["gain_range"][1])

        self.update_size_and_offset(parameters)

        self.triggerModeField.blockSignals(True)
        self.triggerModeField.clear()
        self.triggerModeField.addItems(parameters["trigger_mode_options"])
        self.triggerModeField.setCurrentText(parameters["trigger_mode"])
        self.triggerModeField.blockSignals(False)

        self.triggerSourceField.blockSignals(True)
        self.triggerSourceField.clear()
        self.triggerSourceField.addItems(parameters["trigger_source_options"])
        self.triggerSourceField.setCurrentText(parameters["trigger_source"])
        self.triggerSourceField.blockSignals(False)

        self.exposureModeField.blockSignals(True)
        self.exposureModeField.clear()
        self.exposureModeField.addItems(parameters["exposure_mode_options"])
        self.exposureModeField.setCurrentText(parameters["exposure_mode"])
        self.exposureModeField.blockSignals(False)

        self.pixelFormatField.blockSignals(True)
        self.pixelFormatField.clear()
        self.pixelFormatField.addItems(parameters["pixel_format_options"])
        self.pixelFormatField.setCurrentText(parameters["pixel_format"])
        self.pixelFormatField.blockSignals(False)

        self.binningHorizontalField.setValue(parameters["binning_horizontal"])
        self.binningHorizontalField.setMinimum(
            parameters["binning_horizontal_range"][0]
        )
        self.binningHorizontalField.setMaximum(
            parameters["binning_horizontal_range"][1]
        )

        self.binningVerticalField.setValue(parameters["binning_vertical"])
        self.binningVerticalField.setMinimum(parameters["binning_vertical_range"][0])
        self.binningVerticalField.setMaximum(parameters["binning_vertical_range"][1])

        print(parameters)

    @pyqtSlot(dict)
    def update_offset(self, parameters):
        self.offsetXField.setValue(parameters["offsetX"])
        self.offsetXField.setMinimum(parameters["offsetX_range"][0])
        self.offsetXField.setMaximum(parameters["offsetX_range"][1])

        self.offsetYField.setValue(parameters["offsetY"])
        self.offsetYField.setMinimum(parameters["offsetY_range"][0])
        self.offsetYField.setMaximum(parameters["offsetY_range"][1])

    @pyqtSlot(dict)
    def update_size_and_offset(self, parameters):
        self.widthField.setValue(parameters["width"])
        self.widthField.setMinimum(parameters["width_range"][0])
        self.widthField.setMaximum(parameters["width_range"][1])
        self.targetXField.setMaximum(
            parameters["width_range"][1] * parameters["binning_horizontal"]
        )

        self.heightField.setValue(parameters["height"])
        self.heightField.setMinimum(parameters["height_range"][0])
        self.heightField.setMaximum(parameters["height_range"][1])
        self.targetYField.setMaximum(
            parameters["height_range"][1] * parameters["binning_vertical"]
        )

        self.update_offset(parameters)

    @pyqtSlot(int, int, float, float)
    def set_image_transform(self, sx, sy, scalex, scaley):
        tr = QtGui.QTransform()
        tr.translate(sx * scalex, sy * scaley)
        tr.scale(scalex, scaley)
        self.imageView.getImageItem().setTransform(tr)
        # self.imageView.getImageItem().scale(scalex, scaley)
        # self.imageView.getImageItem().setPos(sx, sy)
        # self.imageView.getImageItem().setRect(sx, sy, sx + 100, sy + 200)

    # Methods for streaming data from the camera
    # -----------------------------------------------------------------
    @pyqtSlot(dict)
    def doUpdate(self, data):
        """Updates the plot/gui when a new image is recieved."""
        # self.img = img
        self.update_plot(data)
        # if self.streaming:
        #     self.request_image.emit()
        self.printFramerate()
        self.update.emit(data)

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
        # self.request_image.emit()
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.widthField.setEnabled(False)
        self.heightField.setEnabled(False)
        self.binningHorizontalField.setEnabled(False)
        self.binningVerticalField.setEnabled(False)
        self.pixelFormatField.setEnabled(False)

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
        self.binningHorizontalField.setEnabled(True)
        self.binningVerticalField.setEnabled(True)
        self.pixelFormatField.setEnabled(True)

    def update_plot(self, data):
        img = data["image"]
        self.centroid = data["centroid"]
        if self.first_image:
            # Set the imageView rather than the imageViewItem to use autoRange on the first image
            self.imageView.setImage(
                img, autoRange=True, autoLevels=False, autoHistogramRange=False
            )
            self.first_image = False
            # This is a bit of an akward way to do this, but it needs to be done after setting the image
            self.set_image_transform(
                self.offsetXField.value(),
                self.offsetYField.value(),
                self.binningHorizontalField.value(),
                self.binningVerticalField.value(),
            )
            self.imageView.autoRange()
        else:
            self.imageView.getImageItem().setImage(
                img, autoLevels=False, autoHistogramRange=False
            )
        if self.normalizeCheckBox.isChecked():
            self.set_hist_range(np.max(img))
        self.set_centroid_crosshair_x(data["centroid"][0])
        self.set_centroid_crosshair_y(data["centroid"][1])

    def on_levels_changed(self, hist):
        # Ensure the histogram limits are enforced if something tries to change them
        # To change the histogram range, use set_hist_range()
        min_level, max_level = hist.getLevels()
        if max_level > self.max_level:
            max_level = self.max_level
        if min_level < 0.0:
            min_level = 0.0
        hist.setLevels(min_level, max_level)

    def do_request_parameters(self):
        self.request_parameters.emit()

    @pyqtSlot(int)
    def on_change_bit_depth(self, value):
        max_level = int(2**value)
        self.set_hist_range(max_level)

    @pyqtSlot()
    def on_normalize_check(self):
        if self.normalizeCheckBox.isChecked():
            self.bitDepthField.setEnabled(False)
        else:
            self.bitDepthField.setEnabled(True)

    @pyqtSlot()
    def toggle_target_crosshair(self):
        if self.targetCosshairCheckBox.isChecked():
            self.targetVLine.setVisible(True)
            self.targetHLine.setVisible(True)
        else:
            self.targetVLine.setVisible(False)
            self.targetHLine.setVisible(False)

    @pyqtSlot()
    def toggle_centroid_crosshair(self):
        if self.beamCenterCheckBox.isChecked():
            self.centroidVLine.setVisible(True)
            self.centroidHLine.setVisible(True)
        else:
            self.centroidVLine.setVisible(False)
            self.centroidHLine.setVisible(False)

    @pyqtSlot()
    def toggle_target_circle(self):
        if self.targetCircleCheckBox.isChecked():
            self.target_circle.setVisible(True)
        else:
            self.target_circle.setVisible(False)

    @pyqtSlot()
    def toggle_centroid_circle(self):
        if self.beamCircleCheckBox.isChecked():
            self.centroid_circle.setVisible(True)
        else:
            self.centroid_circle.setVisible(False)

    def set_target_circle_size(self, size):
        self.target_circle.setSize(2 * size, 2 * size)
        self.set_target_crosshair_x(self.targetXField.value())
        self.set_target_crosshair_y(self.targetYField.value())

    def set_centroid_circle_size(self, size):
        self.centroid_circle.setSize(2 * size, 2 * size)
        self.set_centroid_crosshair_x(self.centroid[0])
        self.set_centroid_crosshair_y(self.centroid[1])

    def set_target_crosshair_x(self, tx):
        self.targetXField.setValue(tx)
        self.targetVLine.setPos(tx + 0.5)

        pos = self.target_circle.pos()
        size = self.target_circle.size()
        self.target_circle.setPos(tx + 0.5 - 0.5 * size[0], pos[1])

    def set_target_crosshair_y(self, ty):
        self.targetYField.setValue(ty)
        self.targetHLine.setPos(ty + 0.5)

        pos = self.target_circle.pos()
        size = self.target_circle.size()
        self.target_circle.setPos(pos[0], ty + 0.5 - 0.5 * size[1])

    def set_centroid_crosshair_x(self, cx):
        self.centroidVLine.setPos(cx)

        pos = self.centroid_circle.pos()
        size = self.centroid_circle.size()
        self.centroid_circle.setPos(cx - 0.5 * size[0], pos[1])

    def set_centroid_crosshair_y(self, cy):
        self.centroidHLine.setPos(cy)

        pos = self.centroid_circle.pos()
        size = self.centroid_circle.size()
        self.centroid_circle.setPos(pos[0], cy - 0.5 * size[1])

    @pyqtSlot()
    def mark_beam(self):
        self.set_target_crosshair_x(self.centroidVLine.getPos()[0])
        self.set_target_crosshair_y(self.centroidHLine.getPos()[1])

    @pyqtSlot()
    def show_lineout_window(self):
        self.lineWin = lineoutWindow.AlignViewLineoutWindow()
        self.update.connect(self.lineWin.on_new_image)
        self.lineWin.show()
