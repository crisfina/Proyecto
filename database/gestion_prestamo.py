

from pymysql import err as pymysql_error

from clases.enum_estados import Estado
from clases.prestamo import Prestamo
from database.gestion import GestionBBDD

class GestionPrestamo:
    def __init__(self, db_manager):
        self.db_manager = db_manager


    def crear_prestamo(self, nie_alumno, curso_alumno, isbn_libro, fecha_entrega, fecha_devolucion, estado):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql = "INSERT INTO alumnoscrusoslibros (nie, curso, isbn, fecha_entrega, \
            fecha_devolucion, estado) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (nie_alumno, curso_alumno, isbn_libro, fecha_entrega, fecha_devolucion, estado)
            self.db_manager.cursor.execute(sql, val)
            self.db_manager.conexion.commit()

            self.db_manager.cursor.execute("UPDATE libros SET numero_ejemplares = numero_ejemplares - 1 WHERE isbn = %s",
                                (isbn_libro,))
            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al crear préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False

    def seleccionar_prestamo(self, nie_alumno, curso_alumno, isbn_libro):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute(
                "SELECT * FROM alumnoscrusoslibros WHERE nie_alumno = %s AND curso_alumno = %s AND isbn_libro = %s \
                AND estado = %s",
                (nie_alumno, curso_alumno, isbn_libro, Estado.PRESTADO.value))
            prestamo_data = self.db_manager.cursor.fetchone()
            if prestamo_data:
                return Prestamo(nie=prestamo_data['nie_alumno'], curso=prestamo_data['curso_alumno'],
                                isbn=prestamo_data['isbn_libro'], fecha_entrega=prestamo_data['fecha_prestamo'],
                                fecha_devolucion=prestamo_data['fecha_devolucion'],
                                estado=Estado(prestamo_data['estado']))
            return None
        except pymysql_error.Error as err:
            print(f"Error al seleccionar préstamo: {err}")
            return None

    def update_prestamo(self, nie_alumno, curso_alumno, isbn_libro, fecha_devolucion, estado):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql = "UPDATE alumnoscrusoslibros SET fecha_devolucion = %s, estado = %s WHERE nie_alumno = %s \
            AND curso_alumno = %s AND isbn_libro = %s AND estado = %s"
            val = (fecha_devolucion, estado, nie_alumno, curso_alumno, isbn_libro, Estado.PRESTADO.value)
            self.db_manager.cursor.execute(sql, val)
            self.db_manager.conexion.commit()

            #Incrementar ejemplares del libro al devolver ver si puedo reusar
            self.db_manager.cursor.execute("UPDATE libros SET numero_ejemplares = numero_ejemplares + 1 WHERE isbn = %s",
                                (isbn_libro,))
            self.db_manager.conexion.commit()
            return self.db_manager.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al actualizar préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False

    def show_prestamos(self):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.db_manager.cursor.execute("SELECT * FROM alumnoscrusoslibros")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar préstamos: {err}")
            return []

    def del_prestamo(self, nie_alumno, curso_alumno, isbn_libro):
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            #Obtener estado actual
            self.db_manager.cursor.execute(
                "SELECT estado FROM alumnoscrusoslibros WHERE nie_alumno = %s AND curso_alumno = %s \
                AND isbn_libro = %s",
                (nie_alumno, curso_alumno, isbn_libro))
            prestamo_info = self.db_manager.cursor.fetchone()

            self.db_manager.cursor.execute(
                "DELETE FROM alumnoscrusoslibros WHERE nie_alumno = %s AND curso_alumno = %s AND isbn_libro = %s",
                (nie_alumno, curso_alumno, isbn_libro))
            self.db_manager.conexion.commit()

            #Incrementar
            if prestamo_info and prestamo_info['estado'] == Estado.PRESTADO.value:
                self.db_manager.cursor.execute("UPDATE libros SET numero_ejemplares = numero_ejemplares + 1 WHERE isbn = %s",
                                    (isbn_libro,))
                self.db_manager.conexion.commit()

            return self.db_manager.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al borrar préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False