#borrar comentarios al final.
from pymysql import err as pymysql_error
from clases.enum_tramos import Tramos



class GestionAlumno:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def insertar_alumno(self, nie, nombre, apellidos, tramo, bilingue):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql = "INSERT INTO alumnos (nie, nombre, apellidos, tramo, bilingue) VALUES (%s, %s, %s, %s, %s)"
            val = (nie, nombre, apellidos, tramo.value if isinstance(tramo, Tramos) else tramo, int(bilingue))
            self.db_manager.cursor.execute(sql, val)
            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al insertar alumno: {err}")
            self.db_manager.conexion.rollback()
            return False


    def seleccionar_alumno(self, nie):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute("SELECT * FROM alumnos WHERE nie = %s", (nie,))
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al seleccionar alumno: {err}")
            return None


    def show_alumnos(self):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return
        try:
            self.db_manager.cursor.execute("SELECT * FROM alumnos")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar alumnos: {err}")
            return


    def modificar_alumno(self, nie, nombre=None, apellidos=None, tramo=None, bilingue=None):
        if not self.db_manager.conexion:
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
            if not updates:
                print("No se proporcionaron campos para modificar.")
                return True
            sql = f"UPDATE alumnos SET {', '.join(updates)} WHERE nie = %s"
            values.append(nie)
            self.db_manager.cursor.execute(sql, tuple(values))
            self.db_manager.conexion.commit()
            return self.db_manager.cursor.rowcount > 0

        except pymysql_error.Error as err:
            print(f"Error al modificar alumno: {err}")
            return False
        except Exception as e:
            print(f"Error inesperado al modificar alumno: {e}")
            return False


    def del_alumno(self, nie):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.db_manager.cursor.execute("DELETE FROM alumnos WHERE nie = %s", (nie,))
            self.db_manager.conexion.commit()
            return self.db_manager.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al borrar alumno: {err}")
            self.db_manager.conexion.rollback()
            return False


