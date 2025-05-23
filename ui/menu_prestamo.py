

from datetime import date, timedelta

from ui.menu import Menu
from clases.enum_estados import Estado
from database.gestion_materias_cursos import GestionMateriasCursos

class MenuPrestamo(Menu):
    def __init__(self, database_prestamo, database_libro, database_alumno, database_materias_cursos, db_manager):
        super().__init__()
        self.database_prestamo = database_prestamo
        self.database_libro = database_libro
        self.database_alumno = database_alumno
        self.database_materias_cursos = database_materias_cursos
        self.db_manager = db_manager
        self.gestor_cursos = GestionMateriasCursos(db_manager)

    def _mostrar_menu(self):
        print("\n--- MENÚ DE PRÉSTAMOS ---")
        print("1. Realizar préstamo de libro")
        print("2. Realizar devolución de libro")
        print("3. Ver lista de préstamos")
        print("4. Borrar préstamo")
        print("5. Volver al menú principal")
        print("-------------------------")

    def _tratar_opcion(self, opcion):
        match opcion:
            case 1:
                self._realizar_prestamo()
            case 2:
                self._realizar_devolucion()
            case 3:
                self._ver_lista_prestamos()
            case 4:
                self._borrar_prestamo()
            case 5:
                print("Volviendo al menú principal...")
                return False
            case _:
                print("Opción no válida.")
        return True

    def main(self):
        while True:
            self._mostrar_menu()
            opcion = self._recoger_opcion()
            if not self._tratar_opcion(opcion):
                break

    def _recoger_opcion(self):
        while True:
            try:
                opcion = int(input("Seleccione una opción: "))
                return opcion
            except ValueError:
                print("Por favor, introduzca un número.")

    def _pedir_dato(self, mensaje, tipo, funcion_validacion=None, valor_por_defecto=None):
        while True:
            try:
                entrada = input(mensaje).strip()
                if not entrada and valor_por_defecto is not None:
                    return valor_por_defecto
                valor = tipo(entrada)
                if funcion_validacion is None or funcion_validacion(valor):
                    return valor
                else:
                    print("Dato no válido. Por favor, siga el formato requerido.")
            except ValueError:
                print(f"Por favor, introduzca un valor del tipo {tipo.__name__}.")
            except Exception as e:
                print(f"Ocurrió un error: {e}")

    def _seleccionar_alumno(self):
        nie = input("Introduzca el nie del alumno: ").strip()
        alumno = self.database_alumno.seleccionar_alumno(nie)
        if alumno:
            return nie, alumno[0]['nombre'] + ' ' + alumno[0]['apellidos']
        else:
            print(f"No se encontró ningún alumno con el nie '{nie}'.")
            return None, None

    def _seleccionar_libro(self):
        isbn = input("Introduzca el ISBN del libro: ").strip()
        libro = self.database_libro.seleccionar_libro(isbn)
        if libro:
            return isbn, libro.titulo
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn}'.")
            return None, None

    def _realizar_prestamo(self):
        print("\n--- REALIZAR PRÉSTAMO DE LIBRO ---")
        nie, nombre_alumno = self._seleccionar_alumno()
        if not nie:
            return

        isbn, titulo_libro = self._seleccionar_libro()
        if not isbn:
            return

        curso_alumno = self.gestor_cursos.mostrar_y_seleccionar_curso()

        if not curso_alumno:
            print("Selección de curso cancelada o fallida")
            return

        alumno_data = self.database_alumno.seleccionar_alumno(nie)
        if not alumno_data:
            print(f"Error: No se encontraron datos del alumno con nie '{nie}'.")
            return


        if self.database_libro.seleccionar_libro(isbn) is None:
            print(f"Error: No se encontró el libro con ISBN '{isbn}'.")
            return

        libro = self.database_libro.seleccionar_libro(isbn)
        if libro and libro.numero_ejemplares > 0:
            fecha_entrega = date.today()
            fecha_fin_curso_estandar = date(date.today().year, 6, 30)
            if fecha_entrega > fecha_fin_curso_estandar:
                print(
                    f"ERROR: No se pueden realizar préstamos. La fecha actual ({fecha_entrega}) es posterior a la fecha límite de préstamos para este curso ({fecha_fin_curso_estandar}).")
                return

            fecha_devolucion = fecha_fin_curso_estandar
            estado = Estado.PRESTADO.value

            if self.database_prestamo.crear_prestamo(nie, curso_alumno, isbn, fecha_entrega, fecha_devolucion, estado):
                print(f"Préstamo realizado: Alumno '{nombre_alumno}' - Libro '{titulo_libro}' (ISBN: {isbn}).")
                print("(Contrato de préstamo generado ficticiamente)")
            else:
                print("Error al realizar el préstamo.")
        elif libro:
            print(f"El libro '{titulo_libro}' (ISBN: {isbn}) no está disponible en este momento.")
        else:
            print("Error al verificar la disponibilidad del libro.")

    def _realizar_devolucion(self):
        print("\n--- REALIZAR DEVOLUCIÓN DE LIBRO ---")
        nie, nombre_alumno = self._seleccionar_alumno()
        if not nie:
            return

        isbn, titulo_libro = self._seleccionar_libro()
        if not isbn:
            return

        alumno_data = self.database_alumno.seleccionar_alumno(nie)
        if not alumno_data:
            print(f"Error: No se encontraron datos del alumno con nie '{nie}'.")
            return
        curso_alumno = alumno_data[0].get('curso')

        prestamo = self.database_prestamo.seleccionar_prestamo(nie, curso_alumno, isbn)
        if prestamo and prestamo.estado == Estado.PRESTADO.value:
            fecha_devolucion = date.today()
            estado = Estado.DEVUELTO.value
            if self.database_prestamo.update_prestamo(nie, curso_alumno, isbn, fecha_devolucion, estado):
                print(f"Devolución registrada: Alumno '{nombre_alumno}' - Libro '{titulo_libro}' (ISBN: {isbn}).")
            else:
                print("Error al registrar la devolución.")
        else:
            print(f"No se encontró ningún préstamo activo para el alumno '{nombre_alumno}' y el libro '{titulo_libro}'.")

    def _ver_lista_prestamos(self):
        print("\n--- LISTA DE PRÉSTAMOS ---")
        prestamos = self.database_prestamo.show_prestamos()
        if prestamos:
            for prestamo in prestamos:
                alumno = self.database_alumno.seleccionar_alumno(prestamo['nie'])
                libro = self.database_libro.seleccionar_libro(prestamo['isbn'])
                nombre_alumno = alumno[0]['nombre'] + ' ' + alumno[0]['apellidos'] if alumno else "Desconocido"
                titulo_libro = libro.titulo if libro else "Desconocido"
                print(f"nie Alumno: {prestamo['nie']} ({nombre_alumno}), "
                      f"Curso: {prestamo['curso']}, "
                      f"ISBN Libro: {prestamo['isbn']} ({titulo_libro}), "
                      f"Fecha Entrega: {prestamo['fecha_entrega']}, "
                      f"Fecha Devolución: {prestamo['fecha_devolucion'] if prestamo['fecha_devolucion'] else 'Pendiente'}, "
                      f"Estado: {prestamo['estado']}")
        else:
            print("No hay préstamos registrados.")

    def _borrar_prestamo(self):
        print("\n--- BORRAR PRÉSTAMO ---")
        nie = input("Introduzca el nie del alumno del préstamo a borrar: ").strip()
        isbn = input("Introduzca el ISBN del libro del préstamo a borrar: ").strip()

        alumno_data = self.database_alumno.seleccionar_alumno(nie)
        if not alumno_data:
            print(f"Error: No se encontraron datos del alumno con nie '{nie}'.")
            return
        curso_alumno = alumno_data[0].get('curso')

        prestamo_existente = self.database_prestamo.seleccionar_prestamo(nie, curso_alumno, isbn)
        if prestamo_existente:
            confirmacion = input(f"¿Está seguro de que desea borrar el préstamo del alumno con nie '{nie}' para el libro con ISBN '{isbn}'? (s/n): ").lower()
            if confirmacion == 's':
                if self.database_prestamo.del_prestamo(nie, curso_alumno, isbn):
                    print(f"Préstamo del alumno con nie '{nie}' para el libro con ISBN '{isbn}' borrado con éxito.")
                else:
                    print(f"Error al borrar el préstamo.")
            else:
                print("Operación de borrado cancelada.")
        else:
            print(f"No se encontró ningún préstamo para el alumno con nie '{nie}' y el libro con ISBN '{isbn}'.")