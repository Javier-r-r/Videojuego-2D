from abc import ABC, abstractmethod

class Observer(ABC):

    @abstractmethod
    def update(self, subject):
        pass


class Subject:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def delete_observer(self, observer):
        self.observer.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)