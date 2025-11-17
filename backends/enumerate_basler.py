from pypylon import pylon

from interfaces import enumerate_interface


class EnumBasler(enumerate_interface.Enumerate):
    def __init__(self):
        self.tlFactory = pylon.TlFactory.GetInstance()
        self.devices = []

    def enumerate_devices(self):
        self.devices = self.tlFactory.EnumerateDevices()

    def get_serial_numbers(self):
        serial_numbers = []
        for device in self.devices:
            serial_numbers.append(device.GetSerialNumber())
        return serial_numbers

    def get_names(self):
        names = []
        for device in self.devices:
            names.append(device.GetModelName())
        return names
