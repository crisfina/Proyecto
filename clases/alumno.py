from clases.curso import Curso
from clases.enum_tramos import Tramos

class Alumno:
    def __init__(self, nie, nombre, apellidos, tramo=Tramos.NADA, bilingue=False, curso=None):
        self.nie = nie
        self.nombre = nombre
        self.apellidos = apellidos
        self.tramo = tramo
        self.bilingue = bilingue
        self.curso = curso if curso else Curso()

    def __str__(self):
        tramo_str = self.tramo.name.replace("TRAMO_", "Tramo ") if self.tramo != Tramos.NADA else "Ninguno"
        bilingue_str = "Sí" if self.bilingue else "No"
        curso_str = str(self.curso) if self.curso else "Sin curso asignado"
        return f"NIE: {self.nie}, Nombre: {self.nombre} {self.apellidos}, Tramo: {tramo_str}, Bilingüe: {bilingue_str}, Curso: {curso_str}"

    @property
    def nie(self):
        return self._nie

    @nie.setter
    def nie(self, value):
        self._nie = value.strip()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value.strip()

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, value):
        self._apellidos = value.strip()

    @property
    def tramo(self):
        return self._tramo

    @tramo.setter
    def tramo(self, value):
        if isinstance(value, Tramos):
            self._tramo = value
        elif isinstance(value, int):
            try:
                self._tramo = Tramos(value)
            except ValueError:
                self._tramo = Tramos.NADA
        else:
            self._tramo = Tramos.NADA

    @property
    def bilingue(self):
        return self._bilingue

    @bilingue.setter
    def bilingue(self, value):
        if isinstance(value, bool):
            self._bilingue = value
        elif isinstance(value, (int, str)):
            self._bilingue = str(value).lower() in ['true', '1', 'sí', 's']
        else:
            self._bilingue = False

    @property
    def curso(self):
        return self._curso

    @curso.setter
    def curso(self, value):
        if isinstance(value, Curso):
            self._curso = value
        else:
            self._curso = Curso(curso=str(value)) # Intenta crear un Curso si se pasa un string