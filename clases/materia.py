#clases.materia.py

class Materia:
    def __init__(self, id_materia=None, nombre=None, departamento=None):
        self.id_materia = id_materia
        self.nombre = nombre.strip() if nombre else ""
        self.departamento = departamento.strip() if departamento else ""

    def __str__(self):
        return f"{self.nombre} ({self.departamento})"

    @property
    def id_materia(self):
        return self._id_materia

    @id_materia.setter
    def id_materia(self, value):
        if value is not None:
            try:
                self._id_materia = int(value)
            except ValueError:
                self._id_materia = None
        else:
            self._id_materia = None

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value.strip() if value else ""

    @property
    def departamento(self):
        return self._departamento

    @departamento.setter
    def departamento(self, value):
        self._departamento = value.strip() if value else ""