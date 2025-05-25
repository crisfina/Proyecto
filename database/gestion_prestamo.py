from pymysql import err as pymysql_error
from clases.enum_estados import Estado
from clases.prestamo import Prestamo
from typing import Optional, List, Any, Union, Tuple
from datetime import date


class GestionPrestamo:
    def __init__(self, db_manager: Any):
        self.db_manager = db_manager

    def crear_prestamo(self, nie_alumno: str,
                       curso_alumno: str, isbn_libro: str,
                       fecha_entrega: date,
                       fecha_devolucion: date,
                       estado: str) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql_prestamo: str = ("INSERT INTO alumnoscrusoslibros (nie, "
                                                                 "curso, "
                                                                 "isbn, "
                                                                 "fecha_entrega, "
                                                                 "fecha_devolucion,"
                                                                 "estado) "
                                 "VALUES (%s, %s, %s, %s, %s, %s)")
            val_prestamo: Tuple[Any, ...] = (nie_alumno, curso_alumno, isbn_libro, fecha_entrega, fecha_devolucion, estado)
            self.db_manager.cursor.execute(sql_prestamo, val_prestamo)

            sql_libro_update: str = ("UPDATE libros SET numero_ejemplares = numero_ejemplares - 1 "
                                     "WHERE isbn = %s")
            self.db_manager.cursor.execute(sql_libro_update, (isbn_libro,))

            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al crear préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False

    def seleccionar_prestamo(self, nie_alumno: str,
                             curso_prestamo: str,
                             isbn_libro: str) -> Optional[Prestamo]:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute(
                "SELECT * FROM alumnoscrusoslibros WHERE nie = %s "
                "AND curso = %s AND isbn = %s AND estado = %s",
                (nie_alumno, curso_prestamo, isbn_libro, Estado.PRESTADO.value))
            prestamo_data: Optional[dict] = self.db_manager.cursor.fetchone()
            if prestamo_data:
                return Prestamo(nie=prestamo_data['nie'],
                                curso=prestamo_data['curso'],
                                isbn=prestamo_data['isbn'],
                                fecha_entrega=prestamo_data['fecha_entrega'],
                                fecha_devolucion=prestamo_data['fecha_devolucion'],
                                estado=Estado(prestamo_data['estado']))
            return None
        except pymysql_error.Error as err:
            print(f"Error al seleccionar préstamo: {err}")
            return None

    def update_prestamo(self, nie: str,
                        curso: str,
                        isbn: str,
                        fecha_devolucion: date, estado: str) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql_prestamo_update: str = ("UPDATE alumnoscrusoslibros SET fecha_devolucion = %s, estado = %s "
                                   "WHERE nie = %s AND curso = %s AND isbn = %s")
            self.db_manager.cursor.execute(
                sql_prestamo_update,
                (fecha_devolucion, estado, nie, curso, isbn)
            )

            if estado == Estado.DEVUELTO.value:
                sql_libro_update: str = ("UPDATE libros SET numero_ejemplares = numero_ejemplares + 1 "
                                    "WHERE isbn = %s")
                self.db_manager.cursor.execute(sql_libro_update, (isbn,))

            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al actualizar préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False

    def show_prestamos(self) -> List[dict]:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.db_manager.cursor.execute("SELECT * FROM alumnoscrusoslibros")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar préstamos: {err}")
            return []

    def del_prestamo(self, nie: str, curso: str, isbn: str) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.db_manager.cursor.execute(
                "SELECT estado "
                "FROM alumnoscrusoslibros "
                "WHERE nie = %s "
                "AND curso = %s AND isbn = %s",
                (nie, curso, isbn)
            )
            prestamo_data: Optional[dict] = self.db_manager.cursor.fetchone()

            sql_delete_prestamo: str = ("DELETE FROM alumnoscrusoslibros "
                                   "WHERE nie = %s "
                                   "AND curso = %s "
                                   "AND isbn = %s")
            self.db_manager.cursor.execute(sql_delete_prestamo, (nie, curso, isbn))

            if prestamo_data and prestamo_data['estado'] == Estado.PRESTADO.value:
                sql_libro_update: str = ("UPDATE libros SET numero_ejemplares = numero_ejemplares + 1 "
                                    "WHERE isbn = %s")
                self.db_manager.cursor.execute(sql_libro_update, (isbn,))

            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al borrar préstamo: {err}")
            self.db_manager.conexion.rollback()
            return False

    def listar_prestamos_activos_por_alumno(self, nie_alumno: str) -> List[dict]:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return []
        try:
            self.db_manager.cursor.execute(
                "SELECT nie, curso, isbn, fecha_entrega, fecha_devolucion, estado "
                "FROM alumnoscrusoslibros "
                "WHERE nie = %s AND estado = %s",
                (nie_alumno, Estado.PRESTADO.value)
            )
            prestamos_data: List[dict] = self.db_manager.cursor.fetchall()
            return prestamos_data
        except pymysql_error.Error as err:
            print(f"Error al listar préstamos activos del alumno: {err}")
            return []
