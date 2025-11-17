from abc import ABC, abstractmethod


class Camera(ABC):
    @abstractmethod
    def set_exposure(self, value):
        pass
