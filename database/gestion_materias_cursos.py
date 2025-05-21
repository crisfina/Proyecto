#no quitar las notas hasta el final para no volverme loca, pero recuerda quitarlas

from pymysql import err as pymysql_error

from clases.curso import Curso
from database.gestion import GestionBBDD
from database.gestion_libro import GestionLibro


class GestionMateriasCursos(GestionBBDD):
    def __init__(self):
        GestionBBDD.__init__(self)

    def cargar_csv_cursos_materias(self, archivo_csv="database/curso_materia.csv"):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file)
                for line in file:
                    try:
                        anio, curso_nombre, nivel, nombre_materia, departamento = map(str.strip,
                                                                                      line.strip().split(','))
                        curso_completo = f"{anio}-{curso_nombre}"

                        #Insertar curso sólo si NO existe
                        self.cursor.execute("SELECT curso FROM cursos WHERE curso = %s", (curso_completo,))
                        if not self.cursor.fetchone():
                            self.cursor.execute("INSERT INTO cursos (curso, nivel) VALUES (%s, %s)",
                                                (curso_completo, nivel))
                            self.conexion.commit()

                        #Inserta materia si no existe
                        self.cursor.execute(
                            "SELECT id_materia FROM materias WHERE nombre = %s AND departamento = %s",
                            (nombre_materia, departamento))
                        if not self.cursor.fetchone():
                            self.cursor.execute("INSERT INTO materias (nombre, departamento) VALUES (%s, %s)",
                                                (nombre_materia, departamento))
                            self.conexion.commit()
                    except ValueError as e:
                        print(f"Error al procesar la línea: {line.strip()} - {e}")
                        self.conexion.rollback()
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de cursos y materias: {e}")
            if self.conexion:
                self.conexion.rollback()

    def seleccionar_curso(self, curso_str):
        if not self.conexion:
            #mirar que no se haya ido a Parla al refactorizar
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.cursor.execute("SELECT * FROM cursos WHERE curso = %s", (curso_str,))
            curso_data = self.cursor.fetchone()
            if curso_data:
                anio = curso_data['curso'].split('-')[0] if '-' in curso_data['curso'] else []
                nombre_curso = curso_data['curso'].split('-')[1] if '-' in curso_data['curso'] else curso_data[
                    'curso']
                return Curso(anio=[anio] if anio else [], curso=nombre_curso)
            return None
        except pymysql_error.Error as err:
            print(f"Error al seleccionar curso: {err}")
            return None

    def show_cursos(self):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.cursor.execute("SELECT curso FROM cursos")
            return self.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar cursos: {err}")
            return []

    def show_materias(self):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.cursor.execute("SELECT id_materia, nombre, departamento FROM materias")
            return self.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar materias: {err}")
            return []