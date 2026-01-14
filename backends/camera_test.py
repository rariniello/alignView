import time

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from interfaces import camera_interface


class TestCam(QObject):
    # class Basler(camera_interface.Camera, QObject):
    exposure_changed = pyqtSignal(float)
    gain_changed = pyqtSignal(float)
    width_changed = pyqtSignal(int)
    height_changed = pyqtSignal(float)
    offsetX_changed = pyqtSignal(float)
    offsetY_changed = pyqtSignal(float)

    def __init__(self, serial_number):
        super().__init__()
        self._exposure = 1.0
        self._gain = 0.0
        self._width = 1024
        self._height = 1024
        self._offsetX = 0
        self._offsetY = 0

    def close(self):
        pass

    def start_streaming(self):
        pass

    def stop_streaming(self):
        pass

    def get_image(self):
        time.sleep(0.05)
        x0 = 600 - self._offsetX + int(np.random.normal(0.0, 2.0))
        y0 = 400 - self._offsetY + int(np.random.normal(0.0, 2.0))
        sigma = 50
        img = np.random.randint(0, 5, (self._height, self._width), dtype="int")
        x = np.arange(self._width)
        y = np.arange(self._height)
        data = (
            512
            * np.exp(
                -((x[None, :] - x0) ** 2 + (y[:, None] - y0) ** 2) / (2 * sigma**2)
            )
            * self._exposure
        )
        img += np.int_(data)
        img *= np.int_(10 ** (self._gain / 10))
        return img

    def set_exposure(self, value):
        self._exposure = value

    def get_exposure(self):
        """Returns the camera's expsoure time [ms]."""
        return self._exposure

    def get_exposure_range(self):
        return [0.001, 1000.00]

    def set_gain(self, value):
        self._gain = value

    def get_gain(self):
        """Returns the camera's gain [dB]."""
        return self._gain

    def get_gain_range(self):
        return [0.0, 48.0]

    def set_width(self, value):
        self._width = value

    def get_width(self):
        """Returns the camera's ROI width [px]."""
        return self._width

    def get_width_range(self):
        return [4, 1024]

    def set_height(self, value):
        self._height = value

    def get_height(self):
        """Returns the camera's ROI height [px]."""
        return self._height

    def get_height_range(self):
        return [4, 1024]

    def set_offsetX(self, value):
        self._offsetX = value

    def get_offsetX(self):
        """Returns the camera's ROI width [px]."""
        return self._offsetX

    def get_offsetX_range(self):
        return [0, 1024 - self._width]

    def set_offsetY(self, value):
        self._offsetY = value

    def get_offsetY(self):
        """Returns the camera's ROI width [px]."""
        return self._offsetY

    def get_offsetY_range(self):
        return [0, 1024 - self._height]
