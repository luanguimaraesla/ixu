from abc import ABC, abstractmethod

class BaseCommand:

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_root(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def export(self):
        return {
            'name': self.get_name(),
            'root': self.get_root(),
            'export': self.execute,
        }
