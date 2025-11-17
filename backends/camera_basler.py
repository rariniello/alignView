from pypylon import genicam, pylon
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from interfaces import camera_interface


class Basler(QObject):
    # class Basler(camera_interface.Camera, QObject):
    exposure_changed = pyqtSignal(float)

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
        self.exposure_changed.emit(update.Value * 1.0e-3)
