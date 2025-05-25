
from abc import ABC, abstractmethod

class Menu(ABC):
    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def _tratar_opcion(self, opcion: int):
        pass

    @abstractmethod
    def _mostrar_menu(self):
        pass

    @abstractmethod
    def _recoger_opcion(self) -> int:
        pass