import os

from abc import ABC, abstractmethod

def move_to_dist(input_file: str):
    os.rename(input_file, os.path.join("dist", os.path.basename(input_file)))

class Config(ABC):
    def __init__(self, payload_parameters, output = "output.exe") -> None:
        ...

    @abstractmethod
    def run(self):
        pass
