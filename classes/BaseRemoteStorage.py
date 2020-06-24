import abc
from classes.BaseScaner import BaseScaner

class BaseRemoteStorage:
    def __init__(self, scanner: BaseScaner, path: str):
        self.scanner = scanner
        self.path = path
        return

    @abc.abstractmethod
    def scan(self):
        pass

    @abc.abstractmethod
    def save_container(self, container: str, data):
        pass