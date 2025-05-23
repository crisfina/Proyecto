#clases.libro.py

from clases.materia import Materia
from clases.curso import Curso

class Libro:
    def __init__(self, isbn, titulo, autor, numero_ejemplares=0, materia=None, curso=None):
        self.isbn = isbn.strip()
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.numero_ejemplares = numero_ejemplares
        self.materia = materia if materia else Materia()
        self.curso = curso if curso else Curso()

    def __str__(self):
        return f"ISBN: {self.isbn}, Título: {self.titulo}, Autor: {self.autor}, " \
               f"Ejemplares: {self.numero_ejemplares}, Materia: {self.materia.nombre}, Curso: {self.curso}"


    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        self._isbn = value.strip()

    @property
    def titulo(self):
        return self._titulo

    @titulo.setter
    def titulo(self, value):
        self._titulo = value.strip()

    @property
    def autor(self):
        return self._autor

    @autor.setter
    def autor(self, value):
        self._autor = value.strip()

    @property
    def numero_ejemplares(self):
        return self._numero_ejemplares

    @numero_ejemplares.setter
    def numero_ejemplares(self, value):
        if isinstance(value, int) and value >= 0:
            self._numero_ejemplares = value
        else:
            self._numero_ejemplares = 0

    @property
    def materia(self):
        return self._materia

    @materia.setter
    def materia(self, value):
        if isinstance(value, Materia):
            self._materia = value
        else:
            self._materia = Materia()

    @property
    def curso(self):
        return self._curso

    @curso.setter
    def curso(self, value):
        if isinstance(value, Curso):
            self._curso = value
        else:
            self._curso = Curso()