
from pymysql import err as pymysql_error

from clases.curso import Curso



class GestionMateriasCursos:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def cargar_csv_cursos_materias(self, archivo_csv="database/curso_materia.csv"):
        if not self.db_manager.conexion:
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

                        self.db_manager.cursor.execute("SELECT curso FROM cursos "
                                                       "WHERE curso = %s", (curso_completo,))
                        if not self.db_manager.cursor.fetchone():
                            self.db_manager.cursor.execute("INSERT INTO cursos (curso, nivel) "
                                                           "VALUES (%s, %s)",
                                                (curso_completo, nivel))
                            self.db_manager.conexion.commit()

                        self.db_manager.cursor.execute(
                            "SELECT id FROM materias WHERE nombre = %s AND departamento = %s",
                            (nombre_materia, departamento))
                        if not self.db_manager.cursor.fetchone():
                            self.db_manager.cursor.execute("INSERT INTO materias (nombre, departamento) "
                                                           "VALUES (%s, %s)",
                                                (nombre_materia, departamento))
                            self.db_manager.conexion.commit()
                    except ValueError as e:
                        print(f"Error al procesar la línea: {line.strip()} - {e}")
                        self.db_manager.conexion.rollback()
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de cursos y materias: {e}")
            if self.db_manager.conexion:
                self.db_manager.conexion.rollback()

    def seleccionar_curso(self, curso_str):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute("SELECT * FROM cursos "
                                           "WHERE curso = %s", (curso_str,))
            curso_data = self.db_manager.cursor.fetchone()
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
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.db_manager.cursor.execute("SELECT curso FROM cursos")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar cursos: {err}")
            return []

    def show_materias(self):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.db_manager.cursor.execute("SELECT id, nombre, departamento FROM materias")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar materias: {err}")
            return []

    def verificar_existencia_curso(self, curso_nombre):
        sql = "SELECT COUNT(*) FROM cursos WHERE curso = %s"
        result = self.db_manager.ejecutar_consulta_con_un_resultado(sql, (curso_nombre,))
        return result['COUNT(*)'] > 0 if result else False

    def mostrar_y_seleccionar_curso(self):
        cursos_disponibles = self.show_cursos()

        if not cursos_disponibles:
            print("No hay cursos disponibles.")
            return None

        print("\nCursos disponibles:")
        for i, curso in enumerate(cursos_disponibles, start=1):
            print(f"{i}. {curso['curso']}")

        while True:
            try:
                opcion = int(input("\nSeleccione el número del curso: "))
                if 1 <= opcion <= len(cursos_disponibles):
                    curso_seleccionado = cursos_disponibles[opcion - 1]['curso']
                    return curso_seleccionado
                else:
                    print("Opción fuera de rango. Intente nuevamente.")
            except ValueError:
                print("Entrada inválida. Introduzca un número.")
