# unilab/modules/simulation/base.py
from abc import ABC, abstractmethod

class BaseSimulator(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def setup(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        pass

    @abstractmethod
    def get_status(self) -> dict:
        pass
        