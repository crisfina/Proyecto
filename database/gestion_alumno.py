
from pymysql import err as pymysql_error
from clases.enum_tramos import Tramos
from database.gestion import GestionBBDD


class GestionAlumno(GestionBBDD):
    def __init__(self):
        super().__init__()
    def insertar_alumno(self, nie, nombre, apellidos, tramo, bilingue, curso):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql = "INSERT INTO alumnos (nie, nombre, apellidos, tramo, bilingue) VALUES (%s, %s, %s, %s, %s)"
            val = (nie, nombre, apellidos, tramo.value if isinstance(tramo, Tramos) else tramo, int(bilingue))
            self.cursor.execute(sql, val)
            self.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al insertar alumno: {err}")
            self.conexion.rollback()
            return False


    def seleccionar_alumno(self, nie):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.cursor.execute("SELECT * FROM alumnos WHERE nie = %s", (nie,))
            return self.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al seleccionar alumno: {err}")
            return None


    def show_alumnos(self):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return
        try:
            self.cursor.execute("SELECT * FROM alumnos")
            return self.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar alumnos: {err}")
            return


    def modificar_alumno(self, nie, nombre=None, apellidos=None, tramo=None, bilingue=None, curso=None):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql = "UPDATE alumnos SET "
            updates = []
            values = []
            if nombre is not None:
                updates.append("nombre = %s")
                values.append(nombre)
            if apellidos is not None:
                updates.append("apellidos = %s")
                values.append(apellidos)
            if tramo is not None:
                updates.append("tramo = %s")
                values.append(tramo.value if isinstance(tramo, Tramos) else tramo)
            if bilingue is not None:
                updates.append("bilingue = %s")
                values.append(int(bilingue))
            sql += ", ".join(updates)
            sql += " WHERE nie = %s"
            values.append(nie)
            self.cursor.execute(sql, tuple(values))
            self.conexion.commit()
            return self.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al modificar alumno: {err}")
            self.conexion.rollback()
            return False


    def del_alumno(self, nie):
        if not self.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.cursor.execute("DELETE FROM alumnos WHERE nie = %s", (nie,))
            self.conexion.commit()
            return self.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al borrar alumno: {err}")
            self.conexion.rollback()
            return False


