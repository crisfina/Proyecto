from clases.enum_tramos import Tramos
from clases.curso import Curso
from database import data_base

class Alumno:
    def __init__(self, NIE: str, nombre: str, apellidos: str,
                 tramo: Tramos = Tramos.NADA, bilingue: bool = False,
                 curso: Curso | None = None):
        self.NIE = NIE #preguntar a César porque en la carga de csv no hay nie, sólo número de estudiante y los menores?
        self.nombre = nombre
        self.apellidos = apellidos
        self.tramo = tramo
        self.bilingue = bilingue
        self.curso = curso

    def __str__(self):
        return f"{self.NIE} - {self.nombre} {self.apellidos} | Tramo: {self.tramo.name} | Bilingüe: {'Sí' if self.bilingue else 'No'}"

    def crear_alumno(self):
        return data_base.insertar_alumno(
            self.NIE, self.nombre, self.apellidos,
            self.tramo.name[-1] if self.tramo != Tramos.NADA else '0',
            int(self.bilingue)
        )

    def modificar_alumno(self):
        return data_base.modificar_alumno(
            self.NIE, self.nombre, self.apellidos,
            self.tramo.name[-1] if self.tramo != Tramos.NADA else '0',
            int(self.bilingue)
        )

    def borrar_alumno(self):
        return data_base.borrar_alumno(self.NIE)

    def seleccionar_alumno(self):
        datos = data_base.obtener_alumno(self.NIE)
        if datos:
            alumno_data = datos[0]
            self.nombre = alumno_data['nombre']
            self.apellidos = alumno_data['apellidos']
            self.tramo = Tramos['TRAMO_' + alumno_data['tramo']] if alumno_data['tramo'] != '0' else Tramos.NADA
            self.bilingue = bool(alumno_data['bilingue'])
        return datos

    @staticmethod
    def visualizar_lista_alumnos():
        alumnos = data_base.listar_alumnos()
        for alumno in alumnos:
            tramo = 'NADA' if alumno['tramo'] == '0' else f"TRAMO_{alumno['tramo']}"
            bilingue = 'Sí' if alumno['bilingue'] else 'No'
            print(f"{alumno['nie']} - {alumno['nombre']} {alumno['apellidos']} | Tramo: {tramo} | Bilingüe: {bilingue}")
