import time

from pypylon import pylon

# Run the file directly to test Basler SDK
if __name__ == "__main__":
    tlFactory = pylon.TlFactory.GetInstance()

    # Get all attached devices and exit application if no device is found.
    devices = tlFactory.EnumerateDevices()
    print(devices[0].GetSerialNumber())
    print(devices[0].GetFullName())
    print(devices[0].GetPropertyNames())
    devices[0].SetUserDefinedName("Cam 3")
    print(devices[0].GetUserDefinedName())

    serial_number = devices[0].GetSerialNumber()

    info = pylon.DeviceInfo()
    info.SetSerialNumber(serial_number)

    camera = pylon.InstantCamera(tlFactory.CreateDevice(info))
    camera.Open()

    print(camera.ExposureTime.Value)
    print(camera.ExposureTime.Max)

    # camera.Open()
    # print("Using device ", camera.GetDeviceInfo().GetModelName())

    # camera.StartGrabbingMax(10)

    # # Camera.StopGrabbing() is called automatically by the RetrieveResult() method
    # # when c_countOfImagesToGrab images have been retrieved.
    # while camera.IsGrabbing():
    #     # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
    #     grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    #     # Image grabbed successfully?
    #     if grabResult.GrabSucceeded():
    #         # Access the image data.
    #         print("SizeX: ", grabResult.Width)
    #         print("SizeY: ", grabResult.Height)
    #         img = grabResult.Array
    #         print("Gray value of first pixel: ", img[0, 0])
    #     else:
    #         print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
    #     grabResult.Release()
    # camera.Close()

    # class QtImageHandler(pylon.ImageEventHandler):

    #     def OnImageGrabbed(self, camera, grabResult):
    #         print("Test")
    #         if grabResult.GrabSucceeded():
    #             img = grabResult.Array
    #             print(img[0, 0])

    # handler = QtImageHandler()

    # class ImageEventPrinter(pylon.ImageEventHandler):
    #     def OnImagesSkipped(self, camera, countOfSkippedImages):
    #         print(
    #             "OnImagesSkipped event for device ",
    #             camera.GetDeviceInfo().GetModelName(),
    #         )
    #         print(countOfSkippedImages, " images have been skipped.")
    #         print()

    #     def OnImageGrabbed(self, camera, grabResult):
    #         print(
    #             "OnImageGrabbed event for device ",
    #             camera.GetDeviceInfo().GetModelName(),
    #         )

    #         # Image grabbed successfully?
    #         if grabResult.GrabSucceeded():
    #             print("SizeX: ", grabResult.GetWidth())
    #             print("SizeY: ", grabResult.GetHeight())
    #             img = grabResult.GetArray()
    #             print("Gray values of first row: ", img[0])
    #             print()
    #         else:
    #             print(
    #                 "Error: ",
    #                 grabResult.GetErrorCode(),
    #                 grabResult.GetErrorDescription(),
    #             )

    # camera.RegisterImageEventHandler(
    #     handler, pylon.RegistrationMode_Append, pylon.Cleanup_Delete
    # )

    # # camera.RegisterImageEventHandler(
    # #     handler, pylon.RegistrationMode_Append, pylon.Cleanup_Delete
    # # )

    # # camera.StartGrabbing(pylon.GrabLoop_ProvidedByInstantCamera)

    # camera.StartGrabbing(
    #     pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera
    # )

    # while True:
    #     time.sleep(0.05)
