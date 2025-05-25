
from clases.enum_tramos import Tramos
from database.gestion_alumno import GestionAlumno


class Alumno:
    def __init__(self, nie: str, nombre: str, apellidos: str,
                 tramo: Tramos = Tramos.NADA, bilingue: bool = False):
        self.nie = nie
        self.nombre = nombre
        self.apellidos = apellidos
        self.tramo = tramo
        self.bilingue = bilingue


    def __str__(self):
        return (f"{self.nie} - {self.nombre} {self.apellidos} | Tramo: {self.tramo.name} "
                f"| Bilingüe: {'Sí' if self.bilingue else 'No'}")

    def crear_alumno(self):
        return database.gestion_alumno.insertar_alumno(
            self.nie, self.nombre, self.apellidos,
            self.tramo.name[-1] if self.tramo != Tramos.NADA else '0',
            int(self.bilingue)
        )

    def modificar_alumno(self):
        return database.gestion_alumno.modificar_alumno(
            self.nie, self.nombre, self.apellidos,
            self.tramo.name[-1] if self.tramo != Tramos.NADA else '0',
            int(self.bilingue)
        )

    def borrar_alumno(self):
        return database.borrar_alumno(self.nie)

    def seleccionar_alumno(self):
        datos = database.obtener_alumno(self.nie)
        if datos:
            alumno_data = datos[0]
            self.nombre = alumno_data['nombre']
            self.apellidos = alumno_data['apellidos']
            self.tramo = Tramos['TRAMO_' + alumno_data['tramo']] if alumno_data['tramo'] != '0' else Tramos.NADA
            self.bilingue = bool(alumno_data['bilingue'])
        return datos

    @staticmethod
    def visualizar_lista_alumnos():
        alumnos = database.listar_alumnos()
        for alumno in alumnos:
            tramo = 'NADA' if alumno['tramo'] == '0' else f"TRAMO_{alumno['tramo']}"
            bilingue = 'Sí' if alumno['bilingue'] else 'No'
            print(f"{alumno['nie']} - {alumno['nombre']} {alumno['apellidos']} | Tramo: {tramo} | Bilingüe: {bilingue}")
