import numpy as np
from pypylon import pylon

from interfaces import enumerate_interface


class EnumTest(enumerate_interface.Enumerate):
    def __init__(self):
        self.devices = []

    def enumerate_devices(self):
        self.devices = ["Test Camera"]

    def get_serial_numbers(self):
        serial_numbers = []
        for device in self.devices:
            serial_numbers.append(np.random.randint(1000000, 9999999))
        return serial_numbers

    def get_names(self):
        names = []
        for device in self.devices:
            names.append("TestCam")
        return names
