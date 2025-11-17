from abc import ABC, abstractmethod


class Enumerate(ABC):
    @abstractmethod
    def enumerate_devices(self):
        pass

    @abstractmethod
    def get_serial_numbers(self):
        pass

    @abstractmethod
    def get_names(self):
        pass
