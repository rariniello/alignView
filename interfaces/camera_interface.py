from abc import ABC, abstractmethod


class Camera(ABC):
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def start_streaming(self):
        pass

    @abstractmethod
    def stop_streaming(self):
        pass

    @abstractmethod
    def get_image(self):
        pass

    @abstractmethod
    def set_exposure(self, value):
        pass

    @abstractmethod
    def get_exposure(self, value):
        pass

    @abstractmethod
    def set_gain(self, value):
        pass

    @abstractmethod
    def get_gain(self, value):
        pass

    @abstractmethod
    def set_width(self, value):
        pass

    @abstractmethod
    def get_width(self, value):
        pass

    @abstractmethod
    def set_height(self, value):
        pass

    @abstractmethod
    def get_height(self, value):
        pass

    @abstractmethod
    def set_offsetX(self, value):
        pass

    @abstractmethod
    def get_offsetX(self, value):
        pass

    @abstractmethod
    def set_offsetY(self, value):
        pass

    @abstractmethod
    def get_offsetY(self, value):
        pass
