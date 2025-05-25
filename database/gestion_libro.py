from pymysql import err as pymysql_error
from typing import Optional, List, Any, Union, Tuple

from database.gestion import GestionBBDD
from clases.libro import Libro
from clases.curso import Curso
from clases.materia import Materia


class GestionLibro(GestionBBDD):
    def __init__(self, db_manager: Any):
        self.db_manager = db_manager

    def seleccionar_libro(self, isbn: str) -> Optional[Libro]:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute(
                "SELECT l.*, m.nombre as materia_nombre, "
                "m.departamento as materia_departamento, "
                "c.nivel as curso_nivel, "
                "c.curso as curso_completo "
                "FROM libros l "
                "JOIN materias m ON l.id_materia = m.id "
                "JOIN cursos c ON l.id_curso = c.curso "
                "WHERE l.isbn = %s",
                (isbn,))
            libro_data: Optional[dict] = self.db_manager.cursor.fetchone()
            if libro_data:
                materia: Materia = Materia(id_materia=libro_data['id_materia'],
                                           nombre=libro_data['materia_nombre'],
                                  departamento=libro_data['materia_departamento'])
                curso_anio: Union[str, List[Any]] = libro_data['curso_completo'].split('-')[0] \
                    if '-' in libro_data['curso_completo'] else []
                curso_nombre: str = libro_data['curso_completo'].split('-')[1] \
                    if '-' in libro_data['curso_completo'] else \
                libro_data['curso_completo']
                curso: Curso = Curso(anio=[curso_anio] if curso_anio else [], curso=curso_nombre)
                return Libro(titulo=libro_data['titulo'], isbn=libro_data['isbn'],
                             numero_ejemplares=libro_data['numero_ejemplares'],
                             autor=libro_data['autor'], materia=materia,
                             curso=curso)
            return None
        except pymysql_error.Error as err:
            print(f"Error al seleccionar libro: {err}")
            return None


    def show_libros(self) -> Optional[List[dict]]:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return None
        try:
            self.db_manager.cursor.execute(
                "SELECT l.*, m.nombre as materia_nombre, "
                "c.nivel as curso_nivel, "
                "c.curso as curso_completo "
                "FROM libros l "
                "JOIN materias m ON l.id_materia = m.id "
                "JOIN cursos c ON l.id_curso = c.curso")
            return self.db_manager.cursor.fetchall()
        except pymysql_error.Error as err:
            print(f"Error al mostrar libros: {err}")
            return None


    def modificar_libro(self, isbn: str, titulo: Optional[str] = None,
                        autor: Optional[str] = None,
                        numero_ejemplares: Optional[int] = None) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql: str = "UPDATE libros SET "
            updates: List[str] = []
            values: List[Any] = []
            if titulo is not None:
                updates.append("titulo = %s")
                values.append(titulo)
            if autor is not None:
                updates.append("autor = %s")
                values.append(autor)
            if numero_ejemplares is not None:
                updates.append("numero_ejemplares = %s")
                values.append(numero_ejemplares)
            if not updates:
                print("No se proporcionaron campos para modificar.")
                return True
            sql += ", ".join(updates)
            sql += " WHERE isbn = %s"
            values.append(isbn)
            self.db_manager.cursor.execute(sql, tuple(values))
            self.db_manager.conexion.commit()
            return self.db_manager.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al modificar libro: {err}")
            self.db_manager.conexion.rollback()
            return False


    def del_libro(self, isbn: str) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            self.db_manager.cursor.execute("DELETE FROM libros WHERE isbn = %s", (isbn,))
            self.db_manager.conexion.commit()
            return self.db_manager.cursor.rowcount > 0
        except pymysql_error.Error as err:
            print(f"Error al borrar libro: {err}")
            self.db_manager.conexion.rollback()
            return False

    def insertar_libro(self, isbn: str,
                       titulo: str,
                       autor: str,
                       numero_ejemplares: int,
                       materia_id: int,
                       curso_id: str) -> bool:
        if not self.db_manager.conexion:
            print("No hay conexión a la base de datos.")
            return False
        try:
            sql: str = ("INSERT INTO libros (isbn, "
                        "titulo, "
                        "autor, "
                        "numero_ejemplares, "
                        "id_materia, "
                        "id_curso) \
            VALUES (%s, %s, %s, %s, %s, %s)")
            val: Tuple[Any, ...] = (isbn, titulo, autor, numero_ejemplares, materia_id, curso_id)
            self.db_manager.cursor.execute(sql, val)
            self.db_manager.conexion.commit()
            return True
        except pymysql_error.Error as err:
            print(f"Error al insertar libro: {err}")
            self.db_manager.conexion.rollback()
            return False
