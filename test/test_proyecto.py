import unittest
from unittest.mock import MagicMock, patch
from datetime import date

from clases.alumno import Alumno
from clases.libro import Libro
from clases.prestamo import Prestamo
from clases.materia import Materia
from clases.curso import Curso
from clases.enum_estados import Estado
from clases.enum_tramos import Tramos

from database.gestion_alumno import GestionAlumno
from database.gestion_libro import GestionLibro
from database.gestion_prestamo import GestionPrestamo


# from database.gestion_materias_cursos import GestionMateriasCursos

class TestModelClasses(unittest.TestCase):
    def test_alumno_creation(self):
        alumno = Alumno("12345678A", "Juan", "Perez", Tramos.TRAMO_I, True)
        self.assertEqual(alumno.nie, "12345678A")
        self.assertEqual(alumno.nombre, "Juan")
        self.assertEqual(alumno.apellidos, "Perez")
        self.assertEqual(alumno.tramo, Tramos.TRAMO_I)
        self.assertTrue(alumno.bilingue)
        self.assertIn("Juan Perez", str(alumno))

    def test_libro_creation(self):
        materia = Materia(id_materia=1, nombre="Matematicas", departamento="Ciencias")
        curso = Curso(curso="1A-ESO")
        libro = Libro("978-1234567890", "Algebra", "Autor A", 5, materia, curso)
        self.assertEqual(libro.isbn, "978-1234567890")
        self.assertEqual(libro.titulo, "Algebra")
        self.assertEqual(libro.numero_ejemplares, 5)
        self.assertEqual(libro.materia.nombre, "Matematicas")
        self.assertEqual(libro.curso.curso, "1A-ESO")

    def test_prestamo_creation(self):
        prestamo = Prestamo(nie="NIE1", curso="CURSO1", isbn="ISBN1",
                            fecha_entrega=date(2024, 1, 1),
                            fecha_devolucion=date(2024, 12, 31),
                            estado=Estado.PRESTADO)
        self.assertEqual(prestamo.nie, "NIE1")
        self.assertEqual(prestamo.estado, Estado.PRESTADO)
        self.assertEqual(prestamo.fecha_entrega, date(2024, 1, 1))


class TestGestionAlumnoMocked(unittest.TestCase):
    def setUp(self):
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.conexion = MagicMock()
        self.mock_db_manager.cursor = MagicMock()

        self.gestion_alumno = GestionAlumno(self.mock_db_manager)

    def test_insertar_alumno(self):
        nie = "12345678A"
        nombre = "Juan"
        apellidos = "Perez"
        tramo = Tramos.TRAMO_I
        bilingue = True

        self.mock_db_manager.cursor.execute.return_value = None

        result = self.gestion_alumno.insertar_alumno(nie, nombre, apellidos, tramo, bilingue)
        self.assertTrue(result)

        self.mock_db_manager.cursor.execute.assert_called_once()
        args, kwargs = self.mock_db_manager.cursor.execute.call_args
        self.assertIn("INSERT INTO alumnos", args[0])
        self.assertEqual(args[1][0], nie)
        self.mock_db_manager.conexion.commit.assert_called_once()

    def test_seleccionar_alumno(self):
        nie = "12345678A"
        self.mock_db_manager.cursor.fetchall.return_value = [
            {'nie': nie, 'nombre': 'Juan', 'apellidos': 'Perez', 'tramo': 'I', 'bilingue': 1}]

        alumno_data = self.gestion_alumno.seleccionar_alumno(nie)
        self.assertIsNotNone(alumno_data)
        self.assertEqual(alumno_data[0]['nie'], nie)
        self.mock_db_manager.cursor.execute.assert_called_once()


class TestGestionPrestamoMocked(unittest.TestCase):
    def setUp(self):
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.conexion = MagicMock()
        self.mock_db_manager.cursor = MagicMock()

        self.mock_gestion_libro = MagicMock()
        self.gestion_prestamo = GestionPrestamo(self.mock_db_manager)

        self.initial_book_data = {'isbn': 'ISBN1', 'titulo': 'Libro Test', 'numero_ejemplares': 5}
        self.mock_db_manager.cursor.fetchone.side_effect = [
            self.initial_book_data,
            {'estado': Estado.PRESTADO.value},
            None
        ]

        mock_libro_instance = MagicMock()
        mock_libro_instance.isbn = 'ISBN1'
        mock_libro_instance.numero_ejemplares = self.initial_book_data['numero_ejemplares']
        self.mock_gestion_libro.seleccionar_libro.return_value = mock_libro_instance

        self.current_stock = 5

        self.mock_db_manager.cursor.execute.side_effect = self._mock_libro_stock_query_logic

        self.mock_db_manager.cursor.execute.reset_mock()

    def _mock_libro_stock_query_logic(self, sql, params=None):
        if "SELECT numero_ejemplares FROM libros WHERE isbn" in sql:
            self.mock_db_manager.cursor.fetchone.return_value = {'numero_ejemplares': self.current_stock}
        elif "UPDATE libros SET numero_ejemplares = numero_ejemplares - 1" in sql:
            self.current_stock -= 1
        elif "UPDATE libros SET numero_ejemplares = numero_ejemplares + 1" in sql:
            self.current_stock += 1
        else:
            pass

    def test_crear_prestamo_y_stock_decrement(self):
        nie, curso, isbn = "NIE1", "CURSO1", "ISBN1"
        fecha_entrega = date.today()
        fecha_devolucion = date(date.today().year, 6, 30)
        estado = Estado.PRESTADO.value

        self.mock_db_manager.cursor.fetchone.reset_mock()

        result = self.gestion_prestamo.crear_prestamo(nie, curso, isbn, fecha_entrega, fecha_devolucion, estado)
        self.assertTrue(result)

        self.mock_db_manager.cursor.execute.assert_any_call(
            "UPDATE libros SET numero_ejemplares = numero_ejemplares - 1 WHERE isbn = %s",
            (isbn,)
        )
        self.mock_db_manager.conexion.commit.assert_called_once()

        self.assertEqual(self.current_stock, 4)

    def test_update_prestamo_y_stock_increment(self):
        nie, curso, isbn = "NIE1", "CURSO1", "ISBN1"
        fecha_entrega = date.today()
        fecha_devolucion_original = date(date.today().year, 6, 30)
        estado_original = Estado.PRESTADO.value

        self.current_stock = 4

        self.mock_db_manager.cursor.fetchone.side_effect = [
            {'nie': nie, 'curso': curso, 'isbn': isbn, 'estado': estado_original},
            None
        ]

        new_fecha_devolucion = date.today()
        new_estado = Estado.DEVUELTO.value

        result = self.gestion_prestamo.update_prestamo(nie, curso, isbn, new_fecha_devolucion, new_estado)
        self.assertTrue(result)

        self.mock_db_manager.cursor.execute.assert_any_call(
            "UPDATE alumnoscrusoslibros SET fecha_devolucion = %s, estado = %s WHERE nie = %s AND curso = %s AND isbn = %s",
            (new_fecha_devolucion, new_estado, nie, curso, isbn)
        )
        self.mock_db_manager.cursor.execute.assert_any_call(
            "UPDATE libros SET numero_ejemplares = numero_ejemplares + 1 WHERE isbn = %s",
            (isbn,)
        )
        self.mock_db_manager.conexion.commit.assert_called_once()
        self.assertEqual(self.current_stock, 5)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
