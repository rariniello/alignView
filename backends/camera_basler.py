import numpy as np
from pypylon import genicam, pylon
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from interfaces import camera_interface


class ImageEventHandler(QObject, pylon.ImageEventHandler):
    imageGrabbedSignal = pyqtSignal(dict)

    def OnImageGrabbed(self, camera, grabResult):
        if grabResult.GrabSucceeded():
            data = {"image": grabResult.GetArray()}
            self.imageGrabbedSignal.emit(data)
        else:
            print(
                "Error: ", grabResult.GetErrorCode(), grabResult.GetErrorDescription()
            )


class Basler(QObject):
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
        genicam.Register(
            camera.BinningHorizontal.GetNode(), self._on_binning_horizontal_change
        )
        genicam.Register(
            camera.BinningVertical.GetNode(), self._on_binning_vertical_change
        )
        self.eventHandler = ImageEventHandler()
        self.image_grabbed = self.eventHandler.imageGrabbedSignal
        camera.RegisterImageEventHandler(
            self.eventHandler,
            pylon.RegistrationMode_Append,
            pylon.Cleanup_Delete,
        )

    def close(self):
        self.camera.Close()

    def start_streaming(self):
        self.camera.StartGrabbing(
            pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByInstantCamera
        )

    def stop_streaming(self):
        print("Stop grabbing")
        self.camera.StopGrabbing()

    # XXX Should not be used when using the grabbing thread
    # def get_image(self):
    #     # Use a 10sec timeout
    #     grabResult = self.camera.RetrieveResult(
    #         10000, pylon.TimeoutHandling_ThrowException
    #     )
    #     if grabResult.GrabSucceeded():
    #         img = grabResult.Array
    #     else:
    #         print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
    #     grabResult.Release()
    #     return img

    # Exposure
    # -----------------------------------------------------------------
    def set_exposure(self, value):
        self.camera.ExposureTime.Value = value * 1.0e3

    def get_exposure(self):
        """Returns the camera's expsoure time [ms]."""
        return self.camera.ExposureTime.Value * 1.0e-3

    def get_exposure_range(self):
        return [
            self.camera.ExposureTime.Min * 1.0e-3,
            self.camera.ExposureTime.Max * 1.0e-3,
        ]

    def _on_exposure_change(self, update):
        try:
            self.exposure_changed.emit(update.Value * 1.0e-3)
        except:
            pass

    # Gain
    # -----------------------------------------------------------------
    def set_gain(self, value):
        self.camera.Gain.Value = value

    def get_gain(self):
        """Returns the camera's gain [dB]."""
        return self.camera.Gain.Value

    def get_gain_range(self):
        return [
            self.camera.Gain.Min,
            self.camera.Gain.Max,
        ]

    def _on_gain_change(self, update):
        try:
            self.gain_changed.emit(update.Value)
        except:
            pass

    # Width
    # -----------------------------------------------------------------
    def set_width(self, value):
        self.camera.Width.Value = value

    def get_width(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.Width.Value

    def get_width_range(self):
        return [
            self.camera.Width.Min,
            self.camera.Width.Max,
        ]

    def _on_width_change(self, update):
        try:
            self.width_changed.emit(update.Value)
        except:
            pass

    # Height
    # -----------------------------------------------------------------
    def set_height(self, value):
        self.camera.Height.Value = value

    def get_height(self):
        """Returns the camera's ROI height [px]."""
        return self.camera.Height.Value

    def get_height_range(self):
        return [
            self.camera.Height.Min,
            self.camera.Height.Max,
        ]

    def _on_height_change(self, update):
        try:
            self.height_changed.emit(update.Value)
        except:
            pass

    # Offset X
    # -----------------------------------------------------------------
    def set_offsetX(self, value):
        self.camera.OffsetX.Value = value

    def get_offsetX(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.OffsetX.Value

    def get_offsetX_range(self):
        return [
            self.camera.OffsetX.Min,
            self.camera.OffsetX.Max,
        ]

    def _on_offsetX_change(self, update):
        try:
            self.offsetX_changed.emit(update.Value)
        except:
            pass

    # Offset Y
    # -----------------------------------------------------------------
    def set_offsetY(self, value):
        self.camera.OffsetY.Value = value

    def get_offsetY(self):
        """Returns the camera's ROI width [px]."""
        return self.camera.OffsetY.Value

    def get_offsetY_range(self):
        return [
            self.camera.OffsetY.Min,
            self.camera.OffsetY.Max,
        ]

    def _on_offsetY_change(self, update):
        try:
            self.offsetY_changed.emit(update.Value)
        except:
            pass

    # Exposure Mode
    # -----------------------------------------------------------------
    def set_exposure_mode(self, value):
        self.camera.ExposureMode.Value = value

    def get_exposure_mode(self):
        return self.camera.ExposureMode.Value

    def enumerate_exposure_mode(self):
        return self.camera.ExposureMode.Symbolics

    # Trigger Mode
    # -----------------------------------------------------------------
    def set_trigger_mode(self, value):
        self.camera.TriggerMode.Value = value

    def get_trigger_mode(self):
        return self.camera.TriggerMode.Value

    def enumerate_trigger_mode(self):
        return self.camera.TriggerMode.Symbolics

    # Trigger Source
    # -----------------------------------------------------------------
    def set_trigger_source(self, value):
        self.camera.TriggerSource.Value = value

    def get_trigger_source(self):
        return self.camera.TriggerSource.Value

    def enumerate_trigger_source(self):
        return self.camera.TriggerSource.Symbolics

    # Pixel Format
    # -----------------------------------------------------------------
    def set_pixel_format(self, value):
        self.camera.PixelFormat.Value = value

    def get_pixel_format(self):
        return self.camera.PixelFormat.Value

    def enumerate_pixel_format(self):
        return self.camera.PixelFormat.Symbolics

    # Binning Horizontal
    # -----------------------------------------------------------------
    def set_binning_horizontal(self, value):
        self.camera.BinningHorizontal.Value = value

    def get_binning_horizontal(self):
        return self.camera.BinningHorizontal.Value

    def get_binning_horizontal_range(self):
        return [
            self.camera.BinningHorizontal.Min,
            self.camera.BinningHorizontal.Max,
        ]

    def _on_binning_horizontal_change(self, update):
        try:
            self.binning_horizontal_changed.emit(update.Value)
        except:
            pass

    # Binning Vertical
    # -----------------------------------------------------------------
    def set_binning_vertical(self, value):
        self.camera.BinningVertical.Value = value

    def get_binning_vertical(self):
        return self.camera.BinningVertical.Value

    def get_binning_vertical_range(self):
        return [
            self.camera.BinningVertical.Min,
            self.camera.BinningVertical.Max,
        ]

    def _on_binning_vertical_change(self, update):
        try:
            self.binning_vertical_changed.emit(update.Value)
        except:
            pass

    # Binning Horizontal Mode
    # -----------------------------------------------------------------
    def set_binning_horizontal_mode(self, value):
        self.camera.BinningHorizontalMode.Value = value

    def get_binning_horizontal_mode(self):
        return self.camera.BinningHorizontalMode.Value

    def enumerate_binning_horizontal_mode(self):
        return self.camera.BinningHorizontalMode.Symbolics

    # Binning Vertical Mode
    # -----------------------------------------------------------------
    def set_binning_vertical_mode(self, value):
        self.camera.BinningVerticalMode.Value = value

    def get_binning_vertical_mode(self):
        return self.camera.BinningVerticalMode.Value

    def enumerate_binning_vertical_mode(self):
        return self.camera.BinningVerticalMode.Symbolics
