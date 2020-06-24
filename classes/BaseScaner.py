import abc


class BaseScaner:

    @abc.abstractmethod
    def scan(self, data: str):
        pass
