import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class Worker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(np.ndarray)
    connected = pyqtSignal()
    connectionFailed = pyqtSignal()

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
        self.connected.emit()

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
        """Changes the spectrometers exposure time to the given exposure.

        Args:
            value: Expsorue to set [ms].
        """
        self.camera.set_exposure(value)
