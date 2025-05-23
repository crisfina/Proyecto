#clases.curso.py

class Curso:
    def __init__(self, anio=None, curso=None):
        self.anio = anio if anio else []
        self.curso = curso if curso else ""

    def __str__(self):
        return f"{'-'.join(self.anio)}-{self.curso}" if self.anio and self.curso else "Sin curso especificado"

    @property
    def anio(self):
        return self._anio

    @anio.setter
    def anio(self, value):
        if isinstance(value, list):
            self._anio = [str(item).strip() for item in value]
        elif isinstance(value, str):
            self._anio = [value.strip()]
        else:
            self._anio = []

    @property
    def curso(self):
        return self._curso

    @curso.setter
    def curso(self, value):
        if isinstance(value, str):
            self._curso = value.strip()
        else:
            self._curso = ""