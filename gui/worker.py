import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class Worker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(np.ndarray)
    connected = pyqtSignal(dict)
    connectionFailed = pyqtSignal()
    parametersUpdated = pyqtSignal(dict)
    offsetRangeUpdated = pyqtSignal(dict)

    def __init__(self, serial_number, camera_class):
        super().__init__()
        self.serial_number = serial_number
        self.camera_class = camera_class

    @pyqtSlot()
    def connect_camera(self):
        """Attempts to connect to the camera."""
        try:
            self.camera = self.camera_class(self.serial_number)
        except TypeError:
            self.connectionFailed.emit()
            return

        parameters = self._get_parameters()
        self.connected.emit(parameters)

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
        # Any image processing necessary
        self.update.emit(img)

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

    @pyqtSlot(int)
    def change_offsetY(self, value: float):
        self.camera.set_offsetY(value)
