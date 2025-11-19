from pypylon import genicam, pylon
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from interfaces import camera_interface


class Basler(QObject):
    # class Basler(camera_interface.Camera, QObject):
    exposure_changed = pyqtSignal(float)
    gain_changed = pyqtSignal(float)
    width_changed = pyqtSignal(int)
    height_changed = pyqtSignal(float)
    offsetX_changed = pyqtSignal(float)
    offsetY_changed = pyqtSignal(float)

    def __init__(self, serial_number):
        super().__init__()
        # Create the object with the properties the transport layer will search for
        info = pylon.DeviceInfo()
        info.SetSerialNumber(serial_number)

        # Find the matching device with the transport layer and connect
        tlFactory = pylon.TlFactory.GetInstance()
        camera = pylon.InstantCamera(tlFactory.CreateDevice(info))
        camera.Open()
        self.camera = camera
        genicam.Register(camera.ExposureTime.GetNode(), self._on_exposure_change)
        genicam.Register(camera.Gain.GetNode(), self._on_gain_change)
        genicam.Register(camera.Width.GetNode(), self._on_width_change)
        genicam.Register(camera.Height.GetNode(), self._on_height_change)
        genicam.Register(camera.OffsetX.GetNode(), self._on_offsetX_change)
        genicam.Register(camera.OffsetY.GetNode(), self._on_offsetY_change)

    def close(self):
        self.camera.Close()

    def start_streaming(self):
        self.camera.StartGrabbing()

    def stop_streaming(self):
        self.camera.StopGrabbing()

    def get_image(self):
        # Use a 10sec timeout
        grabResult = self.camera.RetrieveResult(
            10000, pylon.TimeoutHandling_ThrowException
        )
        if grabResult.GrabSucceeded():
            img = grabResult.Array
        else:
            print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
        grabResult.Release()
        return img

    def set_exposure(self, value):
        self.camera.ExposureTime.Value = value * 1.0e3

    def get_exposure(self):
        """Returns the camera's expsoure time [ms]."""
        return self.camera.ExposureTime.Value * 1.0e-3

    def _on_exposure_change(self, update):
        try:
            self.exposure_changed.emit(update.Value * 1.0e-3)
        except:
            pass

    def set_gain(self, value):
        self.camera.Gain.Value = value

    def get_gain(self):
        """Returns the camera's gain [dB]."""
        return self.camera.Gain.Value

    def _on_gain_change(self, update):
        try:
            self.gain_changed.emit(update.Value)
        except:
            pass

    def set_width(self, value):
        self.camera.Width.Value = value

    def get_width(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.Width.Value

    def _on_width_change(self, update):
        try:
            self.width_changed.emit(update.Value)
        except:
            pass

    def set_height(self, value):
        self.camera.Height.Value = value

    def get_height(self):
        """Returns the camera's ROI height [px]."""
        return self.camera.Height.Value

    def _on_height_change(self, update):
        try:
            self.height_changed.emit(update.Value)
        except:
            pass

    def set_offsetX(self, value):
        self.camera.OffsetX.Value = value

    def get_offsetX(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.OffsetX.Value

    def _on_offsetX_change(self, update):
        try:
            self.offsetX_changed.emit(update.Value)
        except:
            pass

    def set_offsetY(self, value):
        self.camera.OffsetY.Value = value

    def get_offsetY(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.OffsetY.Value

    def _on_offsetY_change(self, update):
        try:
            self.offsetY_changed.emit(update.Value)
        except:
            pass
