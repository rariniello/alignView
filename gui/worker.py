import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from scipy import optimize

import analysis.image as an


class Worker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(dict)
    connected = pyqtSignal(dict)
    connectionFailed = pyqtSignal()
    parametersUpdated = pyqtSignal(dict)
    offsetRangeUpdated = pyqtSignal(dict)

    def __init__(self, serial_number, camera_class):
        super().__init__()
        self.serial_number = serial_number
        self.camera_class = camera_class
        self.previousPx = None
        self.previousPy = None
        self.sx = None
        self.sy = None
        self.config = {}

    @pyqtSlot()
    def connect_camera(self):
        """Attempts to connect to the camera."""
        try:
            self.camera = self.camera_class(self.serial_number)
        except TypeError:
            self.connectionFailed.emit()
            return

        parameters = self._get_parameters()
        # self.sx = parameters["offsetX"]
        # self.sy = parameters["offsetY"]
        self.sx = 0
        self.sy = 0
        self.connected.emit(parameters)
        self.camera.offsetX_changed.connect(self.update_offsetX)
        self.camera.offsetY_changed.connect(self.update_offsetY)

    @pyqtSlot()
    def get_parameters(self):
        parameters = self._get_parameters()
        self.parametersUpdated.emit(parameters)

    def _get_parameters(self):
        parameters = {}
        parameters["exposure"] = self.camera.get_exposure()
        parameters["exposure_range"] = self.camera.get_exposure_range()
        parameters["gain"] = self.camera.get_gain()
        parameters["gain_range"] = self.camera.get_gain_range()
        parameters["width"] = self.camera.get_width()
        parameters["width_range"] = self.camera.get_width_range()
        parameters["height"] = self.camera.get_height()
        parameters["height_range"] = self.camera.get_height_range()
        parameters["offsetX"] = self.camera.get_offsetX()
        parameters["offsetX_range"] = self.camera.get_offsetX_range()
        parameters["offsetY"] = self.camera.get_offsetY()
        parameters["offsetY_range"] = self.camera.get_offsetY_range()
        return parameters

    def get_offset_range(self):
        parameters = {}
        parameters["offsetX"] = self.camera.get_offsetX()
        parameters["offsetX_range"] = self.camera.get_offsetX_range()
        parameters["offsetY"] = self.camera.get_offsetY()
        parameters["offsetY_range"] = self.camera.get_offsetY_range()
        return parameters

    @pyqtSlot()
    def disconnect_camera(self):
        """Closes the connection to the camera."""
        self.camera.close()
        self.finished.emit()

    def start_streaming(self):
        self.camera.start_streaming()

    def stop_streaming(self):
        self.camera.stop_streaming()

    @pyqtSlot()
    def get_image(self):
        """Retrieve the image from the camera."""
        img = self.camera.get_image()
        self.process_image(img)

    def process_image(self, img):
        data = {}
        # Any image processing necessary
        x, y = an.get_xy_arrays(img, self.sx, self.sy)
        centroid, px, py, x_proj, y_proj = an.findImageCenter(
            img, x, y, self.config, self.previousPx, self.previousPy
        )
        self.previousPx = px
        self.previousPy = py
        data["image"] = img
        data["x_proj"] = x_proj
        data["y_proj"] = y_proj
        data["centroid"] = centroid
        self.update.emit(data)

    @pyqtSlot(float)
    def change_exposure(self, value: float):
        """Changes the cameras exposure time.

        Args:
            value: Expsorue to set [ms].
        """
        self.camera.set_exposure(value)

    @pyqtSlot(float)
    def change_gain(self, value: float):
        self.camera.set_gain(value)

    @pyqtSlot(int)
    def change_width(self, value: float):
        self.camera.set_width(value)
        parameters = self.get_offset_range()
        self.offsetRangeUpdated.emit(parameters)

    @pyqtSlot(int)
    def change_height(self, value: float):
        self.camera.set_height(value)
        parameters = self.get_offset_range()
        self.offsetRangeUpdated.emit(parameters)

    @pyqtSlot(int)
    def change_offsetX(self, value: float):
        self.camera.set_offsetX(value)
        # self.sx = value

    @pyqtSlot(int)
    def change_offsetY(self, value: float):
        self.camera.set_offsetY(value)
        # self.sy = value

    @pyqtSlot(int)
    def update_offsetX(self, value):
        # self.sx = value
        pass

    @pyqtSlot(int)
    def update_offsetY(self, value):
        # self.sy = value
        pass
