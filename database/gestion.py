import pymysql
from pymysql import err as pymysql_error
import csv

import config.config
import os
from typing import Optional, Tuple, List, Any, Union


FILE_ALUMNOS: str = "alumnos.csv"
FILE_LIBROS: str = "libros.csv"
FILE_MATERIAS_CURSOS: str = "curso_materia.csv"
FILE_BACKUP: str = "backup.csv"

class GestionBBDD:
    def __init__(self) -> None:
        self.conexion: Optional[pymysql.connections.Connection] = None
        self.cursor: Optional[pymysql.cursors.DictCursor] = None
        try:
            self.conexion = pymysql.connect(
                host=config.config.HOST,
                user=config.config.USER,
                password=config.config.PASSWORD,
                database=config.config.DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conexion.cursor()
            self._crear_tabla_users_si_no_existe()
        except pymysql_error.OperationalError as err:
            if err.args[0] == 1045:
                print("Error de acceso a la base de datos: usuario o contraseña incorrectos.")
            elif err.args[0] == 1049:
                print(f"La base de datos '{config.config.DATABASE}' no existe.")
            else:
                print(f"Error al conectar a la base de datos: {err}")
        except Exception as e:
            print(f"Ocurrió un error durante la inicialización de la base de datos: {e}")

    def _crear_tabla_users_si_no_existe(self) -> None:
        try:
            if self.cursor is not None and self.conexion is not None:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username VARCHAR(50) NOT NULL PRIMARY KEY,
                        password VARCHAR(255) NOT NULL
                    )
                """)
                self.conexion.commit()
                print("Tabla 'users' creada.")
        except pymysql_error.Error as e:
            print(f"Error al crear la tabla 'users': {e}")
            if self.conexion:
                self.conexion.rollback()

    def cerrar_conexion(self) -> None:
        if self.conexion and self.conexion.open:
            if self.cursor:
                self.cursor.close()
            self.conexion.close()
            print("Conexión a la base de datos cerrada.")

    def cargar_csv_alumnos(self, archivo_csv: str = "database/alumnos.csv") -> None:
        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file)
                for line in file:
                    try:
                        isbn: str
                        titulo: str
                        autor: str
                        numero_ejemplares_str: str
                        nombre_materia: str
                        departamento_materia: str
                        curso_str: str
                        isbn, titulo, autor, numero_ejemplares_str, nombre_materia, departamento_materia, curso_str = map(
                            str.strip, line.strip().split(','))
                        numero_ejemplares: int = int(numero_ejemplares_str)

                        self.cursor.execute("SELECT id FROM materias WHERE nombre = %s \
                            AND departamento = %s", (nombre_materia, departamento_materia))
                        materia_existe: Optional[dict] = self.cursor.fetchone()
                        materia_id: int
                        if not materia_existe:
                            self.cursor.execute("INSERT INTO materias (nombre, departamento) \
                                VALUES (%s, %s)", (nombre_materia, departamento_materia))
                            self.conexion.commit()
                            materia_id = self.conexion.insert_id()
                        else:
                            materia_id = materia_existe['id']

                        self.cursor.execute("SELECT curso FROM cursos WHERE curso = %s", (curso_str,))
                        curso_existe: Optional[dict] = self.cursor.fetchone()
                        if not curso_existe:
                            print(f"Advertencia: El curso '{curso_str}' no existe. El libro '{titulo}' no se cargará.")
                            continue

                        self.cursor.execute("INSERT INTO libros (isbn, titulo, autor, numero_ejemplares, \
                            id_materia, id_curso) VALUES (%s, %s, %s, %s, %s, %s)",
                                            (isbn, titulo, autor, numero_ejemplares, materia_id, curso_str))
                        self.conexion.commit()
                    except ValueError as e:
                        print(f"Error al procesar la línea: {line.strip()} - {e}")
                        self.conexion.rollback()
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de libros: {e}")
            if self.conexion:
                self.conexion.rollback()

    def cargar_csv_libros(self, archivo_csv: str = "database/libros.csv") -> None:
        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file)
                for line in file:
                    try:
                        isbn: str
                        titulo: str
                        autor: str
                        numero_ejemplares_str: str
                        nombre_materia: str
                        departamento_materia: str
                        curso_str: str
                        isbn, titulo, autor, numero_ejemplares_str, nombre_materia, departamento_materia, curso_str = map(
                            str.strip, line.strip().split(','))
                        numero_ejemplares: int = int(numero_ejemplares_str)

                        self.cursor.execute("SELECT id FROM materias WHERE nombre = %s \
                            AND departamento = %s", (nombre_materia, departamento_materia))
                        materia_existe: Optional[dict] = self.cursor.fetchone()
                        materia_id: int
                        if not materia_existe:
                            self.cursor.execute("INSERT INTO materias (nombre, departamento) \
                                VALUES (%s, %s)", (nombre_materia, departamento_materia))
                            self.conexion.commit()
                            materia_id = self.conexion.insert_id()
                        else:
                            materia_id = materia_existe['id']

                        self.cursor.execute("SELECT curso FROM cursos WHERE curso = %s", (curso_str,))
                        curso_existe: Optional[dict] = self.cursor.fetchone()
                        if not curso_existe:
                            print(f"Advertencia: El curso '{curso_str}' no existe. El libro '{titulo}' no se cargará.")
                            continue

                        self.cursor.execute("INSERT INTO libros (isbn, titulo, autor, numero_ejemplares, \
                            id_materia, id_curso) VALUES (%s, %s, %s, %s, %s, %s)",
                                            (isbn, titulo, autor, numero_ejemplares, materia_id, curso_str))
                        self.conexion.commit()
                    except ValueError as e:
                        print(f"Error al procesar la línea: {line.strip()} - {e}")
                        self.conexion.rollback()
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de libros: {e}")
            if self.conexion:
                self.conexion.rollback()

    def cargar_csv_cursos_materias(self, archivo_csv: str = "database/curso_materia.csv") -> None:

        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.cursor.execute("INSERT IGNORE INTO cursos (curso, nivel) VALUES (%s, %s)",
                                        (row['curso_completo'], row['nivel']))
                    self.conexion.commit()

                    self.cursor.execute("INSERT IGNORE INTO materias (nombre, departamento) VALUES (%s, %s)",
                                        (row['nombre_materia'], row['departamento']))
                    self.conexion.commit()
            print(f"Datos de cursos y materias cargados desde '{archivo_csv}'.")
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de cursos/materias: {e}")
            if self.conexion:
                self.conexion.rollback()


    def obtener_password_hash(self, username: str) -> Optional[str]:
        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result: Optional[dict] = self.cursor.fetchone()
            return result['password'] if result else None
        except pymysql_error.Error as err:
            print(f"Error al obtener password hash: {err}")
            return None

    def almacenar_password(self, username: str, password_hash: str) -> bool:
        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.cursor.execute("INSERT INTO users (username, password) "
                                "VALUES (%s, %s)", (username, password_hash))
            self.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al almacenar password: {err}")
            self.conexion.rollback()
            return False

    def bbdd_backup(self, archivo_backup: str = "backup_curso.csv") -> bool:
        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos para realizar el backup.")
            return False

        try:
            self.cursor.execute("SELECT DATABASE()")
            db_name_result: Optional[dict] = self.cursor.fetchone()
            db_name: Optional[str] = db_name_result['DATABASE()'] if db_name_result else None

            if not db_name:
                print("No se pudo obtener el nombre de la base de datos actual.")
                return False

            with open(archivo_backup, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer: csv.writer = csv.writer(csvfile)

                self.cursor.execute(f"SHOW TABLES FROM `{db_name}`")
                tables: List[dict] = self.cursor.fetchall()
                table_names: List[str] = [table[f'Tables_in_{db_name}'] for table in tables]

                if not table_names:
                    print("No se encontraron tablas en la base de datos para hacer backup.")
                    return False

                print(f"Realizando backup de {len(table_names)} tablas a '{archivo_backup}'...")

                for table_name in table_names:
                    csv_writer.writerow([f"--- Tabla: {table_name} ---"])

                    self.cursor.execute(f"SELECT * FROM `{table_name}`")

                    column_names: List[str] = [i[0] for i in self.cursor.description]
                    csv_writer.writerow(column_names)

                    for row in self.cursor.fetchall():
                        processed_row: List[Any] = []
                        for value in row.values():
                            if isinstance(value, (int, float, str)):
                                processed_row.append(value)
                            elif isinstance(value, (type(None))):
                                processed_row.append('')
                            else:
                                processed_row.append(str(value))
                        csv_writer.writerow(processed_row)

                    csv_writer.writerow([])

                print(f"Backup de la base de datos completado exitosamente en '{os.path.abspath(archivo_backup)}'.")
            return True
        except pymysql_error.Error as err:
            print(f"Error de base de datos al realizar el backup: {err}")
            return False
        except IOError as err:
            print(f"Error de E/S al escribir el archivo de backup: {err}")
            return False
        except Exception as err:
            print(f"Ocurrió un error inesperado al realizar el backup: {err}")
            return False

    def cargar_alumnos_nuevo_curso(self, archivo_csv: str) -> None:

        if not self.conexion or not self.cursor:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file)
                for line in file:
                    try:
                        (apellidos_nombre, numero_escolar, numero_solicitud, fecha_solicitud,
                         campo_no_necesario1, curso_academico, campo_no_necesario2, campo_no_necesario3,
                         campo_no_necesario4, campo_no_necesario5, campo_no_necesario6, campo_no_necesario7,
                         campo_no_necesario8, campo_no_necesario9, resultado_libros, resultado_comedor,
                         matriculado, tipo_beca_libros, tipo_beca_comedor) = line.strip().split(',')
                        apellidos: str
                        nombre: str
                        apellidos, nombre = map(str.strip, apellidos_nombre.split(','))
                        nie: str = numero_escolar.strip()
                        curso_str: str
                        nivel_str: str
                        curso_str, nivel_str = map(str.strip, curso_academico.split('-'))
                        tramo_str: str = '0' # Si no tiene nada es que no tiene beca
                        bilingue_str: str = '1' # Como acordamos en clase, valor por defecto

                        # Verificar si el curso existe, si no, crearlo
                        self.cursor.execute("SELECT curso "
                                            "FROM cursos "
                                            "WHERE curso = %s", (curso_academico,))
                        curso_existe: Optional[dict] = self.cursor.fetchone()
                        if not curso_existe:
                            self.cursor.execute("INSERT INTO cursos (curso, nivel) "
                                                "VALUES (%s, %s)", (curso_academico, nivel_str))
                            self.conexion.commit()

                        # Insertar alumno
                        self.cursor.execute("INSERT INTO alumnos (nie, nombre, apellidos, tramo, bilingue) \
                        VALUES (%s, %s, %s, %s, %s)",
                                            (nie, nombre, apellidos, tramo_str, bilingue_str))
                        self.conexion.commit()
                    except ValueError as e:
                        print(f"Error al procesar la línea: {line.strip()} - {e}")
                        self.conexion.rollback()
        except FileNotFoundError:
            print(f"El archivo '{archivo_csv}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error durante la carga de alumnos del nuevo curso: {e}")
            if self.conexion:
                self.conexion.rollback()
