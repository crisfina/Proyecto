

from datetime import date
from clases.enum_estados import Estado

class Prestamo:
    def __init__(self, nie, curso, isbn, fecha_entrega=None, fecha_devolucion=None, estado=Estado.PRESTADO):
        self.nie = nie.strip()
        self.curso = curso.strip()
        self.isbn = isbn.strip()
        self.fecha_entrega = fecha_entrega if fecha_entrega else date.today()
        self.fecha_devolucion = fecha_devolucion
        self.estado = estado

    def __str__(self):
        return f"NIE: {self.nie}, Curso: {self.curso}, ISBN: {self.isbn}, " \
               f"Entrega: {self.fecha_entrega}, Devolución: {self.fecha_devolucion if self.fecha_devolucion else 'Pendiente'}, " \
               f"Estado: {self.estado.name}"

    @property
    def nie(self):
        return self._nie

    @nie.setter
    def nie(self, value):
        self._nie = value.strip()

    @property
    def curso(self):
        return self._curso

    @curso.setter
    def curso(self, value):
        self._curso = value.strip()

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        self._isbn = value.strip()

    @property
    def fecha_entrega(self):
        return self._fecha_entrega

    @fecha_entrega.setter
    def fecha_entrega(self, value):
        if isinstance(value, date):
            self._fecha_entrega = value
        else:
            try:
                self._fecha_entrega = date.fromisoformat(str(value).split(' ')[0])
            except (TypeError, ValueError):
                self._fecha_entrega = date.today()

    @property
    def fecha_devolucion(self):
        return self._fecha_devolucion

    @fecha_devolucion.setter
    def fecha_devolucion(self, value):
        if isinstance(value, date) or value is None:
            self._fecha_devolucion = value
        else:
            try:
                self._fecha_devolucion = date.fromisoformat(str(value).split(' ')[0])
            except (TypeError, ValueError):
                self._fecha_devolucion = None

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, value):
        if isinstance(value, Estado):
            self._estado = value
        elif isinstance(value, str):
            try:
                self._estado = Estado(value)
            except ValueError:
                self._estado = Estado.PRESTADO
        else:
            self._estado = Estado.PRESTADO