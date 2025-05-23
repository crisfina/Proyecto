#database.gestion.py

import pymysql
from pymysql import err as pymysql_error

import config.config



FILE_ALUMNOS = "alumnos.csv"
FILE_LIBROS = "libros.csv"
FILE_MATERIAS_CURSOS = "curso_materia.csv"
FILE_BACKUP = "backup.csv"

class GestionBBDD:
    def __init__(self):
        self.conexion = None
        self.cursor = None
        try:
            self.conexion = pymysql.connect(
                host=config.config.HOST,
                user=config.config.USER,
                password=config.config.PASSWORD,
                database=config.config.DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor #PAra pasas a diccionario.
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

    def _crear_tabla_users_si_no_existe(self):
        try:
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

    def cerrar_conexion(self):
        if self.conexion and self.conexion.open:
            self.cursor.close()
            self.conexion.close()
            print("Conexión a la base de datos cerrada.")

    def cargar_csv_alumnos(self, archivo_csv="database/alumnos.csv"):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file) #Saltar el encabezado
                for line in file:
                    try:
                        (apellidos_nombre, numero_escolar, numero_solicitud, fecha_solicitud,
                         campo_no_necesario1, curso_academico, campo_no_necesario2, campo_no_necesario3,
                         campo_no_necesario4, campo_no_necesario5, campo_no_necesario6, campo_no_necesario7,
                         campo_no_necesario8, campo_no_necesario9, resultado_libros, resultado_comedor,
                         matriculado, tipo_beca_libros, tipo_beca_comedor) = line.strip().split(',')
                        apellidos, nombre = map(str.strip, apellidos_nombre.split(','))
                        nie = numero_escolar.strip()
                        curso_str, nivel_str = map(str.strip, curso_academico.split('-'))
                        tramo_str = '0' #Si no tiene nada es que no tiene beca
                        bilingue_str = '1' #Como acordamos en clase, valor por defecto

                        self.cursor.execute("SELECT curso FROM cursos WHERE curso = %s", (curso_academico,))
                        curso_existe = self.cursor.fetchone()
                        if not curso_existe:
                            self.cursor.execute("INSERT INTO cursos (curso, nivel) VALUES (%s, %s)", (curso_academico, nivel_str))
                            self.conexion.commit()

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
            print(f"Ocurrió un error durante la carga de alumnos: {e}")
            if self.conexion:
                self.conexion.rollback()

    def cargar_csv_libros(self, archivo_csv="database/libros.csv"):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                next(file)
                for line in file:
                    try:
                        isbn, titulo, autor, numero_ejemplares, nombre_materia, departamento_materia, curso_str = map(str.strip, line.strip().split(','))
                        numero_ejemplares = int(numero_ejemplares)

                        #PAra crear o sacar la materia
                        self.cursor.execute("SELECT id_materia FROM materias WHERE nombre = %s \
                        AND departamento = %s", (nombre_materia, departamento_materia))
                        materia_existe = self.cursor.fetchone()
                        if not materia_existe:
                            self.cursor.execute("INSERT INTO materias (nombre, departamento) \
                            VALUES (%s, %s)", (nombre_materia, departamento_materia))
                            self.conexion.commit()
                            materia_id = self.conexion.insert_id()
                        else:
                            materia_id = materia_existe['id_materia']

                        #Verificar si el curso existe
                        self.cursor.execute("SELECT curso FROM cursos WHERE curso = %s", (curso_str,))
                        curso_existe = self.cursor.fetchone()
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





    def obtener_password_hash(self, username):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = self.cursor.fetchone()
            return result['password'] if result else None
        except pymysql_error.Error as err:
            print(f"Error al obtener password hash: {err}")
            return None

    def almacenar_password(self, username, password_hash):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
            self.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al almacenar password: {err}")
            self.conexion.rollback()
            return False


    def bbdd_backup(self, archivo_backup="backup.sql"):
        if not self.conexion:
                print("No hay conexión a la base de datos.")