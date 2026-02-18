import time

import numpy as np
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot

from interfaces import camera_interface


class ImageGenerator(QObject):
    finished = pyqtSignal()
    imageGrabbedSignal = pyqtSignal(dict)

    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_image)
        self.timer.start(100)

    def create_image(self):
        try:
            x0 = 600 - self.camera._offsetX + int(np.random.normal(0.0, 2.0))
            y0 = 400 - self.camera._offsetY + int(np.random.normal(0.0, 2.0))
            sigma = 50
            img = np.random.randint(
                0, 5, (self.camera._height, self.camera._width), dtype="int"
            )
            x = np.arange(self.camera._width)
            y = np.arange(self.camera._height)
            data = (
                512
                * np.exp(
                    -((x[None, :] - x0) ** 2 + (y[:, None] - y0) ** 2) / (2 * sigma**2)
                )
                * self.camera._exposure
            )
            img += np.int_(data)
            img *= np.int_(10 ** (self.camera._gain / 10))
            data = {"image": img}
            self.imageGrabbedSignal.emit(data)
        except:
            print("Error generating test image")

    def stop(self):
        self.timer.stop()
        self.finished.emit()


class TestCam(QObject):
    # class Basler(camera_interface.Camera, QObject):
    exposure_changed = pyqtSignal(float)
    gain_changed = pyqtSignal(float)
    width_changed = pyqtSignal(int)
    height_changed = pyqtSignal(int)
    offsetX_changed = pyqtSignal(int)
    offsetY_changed = pyqtSignal(int)
    binning_horizontal_changed = pyqtSignal(int)
    binning_vertical_changed = pyqtSignal(int)
    image_grabbed = pyqtSignal(dict)

    stop = pyqtSignal()

    def __init__(self, serial_number):
        super().__init__()
        self._exposure = 1.0
        self._gain = 0.0
        self._width = 1024
        self._height = 1024
        self._offsetX = 0
        self._offsetY = 0
        self._exposureMode = "None"
        self._triggerMode = "None"
        self._triggerSource = "None"
        self._pixelFormat = "Mono 8"
        self._binning_horizontal = 1
        self._binning_vertical = 1

    def close(self):
        pass

    def start_streaming(self):
        self.thread = QThread()
        self.worker = ImageGenerator(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.stop.connect(self.worker.stop)
        self.worker.finished.connect(self.thread.quit)
        self.worker.imageGrabbedSignal.connect(self.emit_image)

        self.thread.start()

    def stop_streaming(self):
        self.stop.emit()

    def emit_image(self, data):
        self.image_grabbed.emit(data)

    # XXX Should not be used when using the grabbing thread
    # def get_image(self):
    #     time.sleep(0.05)
    #     x0 = 600 - self._offsetX + int(np.random.normal(0.0, 2.0))
    #     y0 = 400 - self._offsetY + int(np.random.normal(0.0, 2.0))
    #     sigma = 50
    #     img = np.random.randint(0, 5, (self._height, self._width), dtype="int")
    #     x = np.arange(self._width)
    #     y = np.arange(self._height)
    #     data = (
    #         512
    #         * np.exp(
    #             -((x[None, :] - x0) ** 2 + (y[:, None] - y0) ** 2) / (2 * sigma**2)
    #         )
    #         * self._exposure
    #     )
    #     img += np.int_(data)
    #     img *= np.int_(10 ** (self._gain / 10))
    #     return img

    # Exposure
    # -----------------------------------------------------------------
    def set_exposure(self, value):
        self._exposure = value

    def get_exposure(self):
        """Returns the camera's expsoure time [ms]."""
        return self._exposure

    def get_exposure_range(self):
        return [0.001, 1000.00]

    # Gain
    # -----------------------------------------------------------------
    def set_gain(self, value):
        self._gain = value

    def get_gain(self):
        """Returns the camera's gain [dB]."""
        return self._gain

    def get_gain_range(self):
        return [0.0, 48.0]

    # Width
    # -----------------------------------------------------------------

    def set_width(self, value):
        self._width = value

    def get_width(self):
        """Returns the camera's ROI width [px]."""
        return self._width

    def get_width_range(self):
        return [4, 1024]

    # Height
    # -----------------------------------------------------------------
    def set_height(self, value):
        self._height = value

    def get_height(self):
        """Returns the camera's ROI height [px]."""
        return self._height

    def get_height_range(self):
        return [4, 1024]

    # Offset X
    # -----------------------------------------------------------------
    def set_offsetX(self, value):
        self._offsetX = value
        self.offsetX_changed.emit(value)

    def get_offsetX(self):
        """Returns the camera's ROI width [px]."""
        return self._offsetX

    def get_offsetX_range(self):
        return [0, 1024 - self._width]

    # Offset Y
    # -----------------------------------------------------------------
    def set_offsetY(self, value):
        self._offsetY = value
        self.offsetY_changed.emit(value)

    def get_offsetY(self):
        """Returns the camera's ROI width [px]."""
        return self._offsetY

    def get_offsetY_range(self):
        return [0, 1024 - self._height]

    # Exposure Mode
    # -----------------------------------------------------------------
    def set_exposure_mode(self, value):
        self._exposureMode = value

    def get_exposure_mode(self):
        return self._exposureMode

    def enumerate_exposure_mode(self):
        return ["None"]

    # Trigger Mode
    # -----------------------------------------------------------------
    def set_trigger_mode(self, value):
        self._triggerMode = value

    def get_trigger_mode(self):
        return self._triggerMode

    def enumerate_trigger_mode(self):
        return ["None"]

    # Trigger Source
    # -----------------------------------------------------------------
    def set_trigger_source(self, value):
        self._triggerSource = value

    def get_trigger_source(self):
        return self._triggerSource

    def enumerate_trigger_source(self):
        return ["None"]

    # Pixel Format
    # -----------------------------------------------------------------
    def set_pixel_format(self, value):
        self._pixelFormat = value

    def get_pixel_format(self):
        return self._pixelFormat

    def enumerate_pixel_format(self):
        return ["Mono 8"]

    # Binning Horizontal
    # -----------------------------------------------------------------
    def set_binning_horizontal(self, value):
        self._binning_horizontal = value
        self.binning_horizontal_changed.emit(value)

    def get_binning_horizontal(self):
        return self._binning_horizontal

    def get_binning_horizontal_range(self):
        return [0, 4]

    # Binning Vertical
    # -----------------------------------------------------------------
    def set_binning_vertical(self, value):
        self._binning_vertical = value
        self.binning_vertical_changed.emit(value)

    def get_binning_vertical(self):
        return self._binning_vertical

    def get_binning_vertical_range(self):
        return [0, 4]
