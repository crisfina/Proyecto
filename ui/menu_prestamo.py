from datetime import date
from typing import Optional, Tuple, List, Any

from ui.menu import Menu
from clases.enum_estados import Estado
from database.gestion_materias_cursos import GestionMateriasCursos
from clases.libro import Libro


class MenuPrestamo(Menu):
    def __init__(self, database_prestamo: Any,
                 database_libro: Any,
                 database_alumno: Any,
                 database_materias_cursos: Any,
                 db_manager: Any):
        super().__init__()
        self.database_prestamo = database_prestamo
        self.database_libro = database_libro
        self.database_alumno = database_alumno
        self.database_materias_cursos = database_materias_cursos
        self.db_manager = db_manager
        self.gestor_cursos = GestionMateriasCursos(db_manager)

    def _mostrar_menu(self) -> None:
        print("\n--- MENÚ DE PRÉSTAMOS ---")
        print("1. Realizar préstamo de libro")
        print("2. Realizar devolución de libro")
        print("3. Ver lista de préstamos")
        print("4. Borrar préstamo")
        print("5. Volver al menú principal")
        print("-------------------------")

    def _tratar_opcion(self, opcion: int) -> bool:
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

    def main(self) -> None:
        while True:
            self._mostrar_menu()
            opcion: int = self._recoger_opcion()
            if not self._tratar_opcion(opcion):
                break

    def _recoger_opcion(self) -> int:
        while True:
            try:
                opcion: int = int(input("Seleccione una opción: "))
                return opcion
            except ValueError:
                print("Por favor, introduzca un número.")

    def _pedir_dato(self, mensaje: str,
                    tipo: type,
                    funcion_validacion: Optional[Any] = None,
                    valor_por_defecto: Optional[Any] = None) -> Any:
        while True:
            try:
                entrada: str = input(mensaje).strip()
                if not entrada and valor_por_defecto is not None:
                    return valor_por_defecto
                valor: Any = tipo(entrada)
                if funcion_validacion is None or funcion_validacion(valor):
                    return valor
                else:
                    print("Dato no válido. Por favor, siga el formato requerido.")
            except ValueError:
                print(f"Por favor, introduzca un valor del tipo {tipo.__name__}.")
            except Exception as e:
                print(f"Ocurrió un error: {e}")

    def _seleccionar_alumno(self) -> Tuple[Optional[str], Optional[str]]:
        nie: str = input("Introduzca el nie del alumno: ").strip()
        alumno: Optional[List[dict]] = self.database_alumno.seleccionar_alumno(nie)
        if alumno:
            return nie, alumno[0]['nombre'] + ' ' + alumno[0]['apellidos']
        else:
            print(f"No se encontró ningún alumno con el nie '{nie}'.")
            return None, None

    def _seleccionar_libro(self) -> Tuple[Optional[str], Optional[str]]:
        isbn: str = input("Introduzca el ISBN del libro: ").strip()
        libro: Optional[Libro] = self.database_libro.seleccionar_libro(isbn)
        if libro:
            return isbn, libro.titulo
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn}'.")
            return None, None

    def _realizar_prestamo(self) -> None:
        print("\n--- REALIZAR PRÉSTAMO DE LIBRO ---")
        nie: Optional[str]
        nombre_alumno: Optional[str]
        nie, nombre_alumno = self._seleccionar_alumno()
        if not nie:
            return

        isbn: Optional[str]
        titulo_libro: Optional[str]
        isbn, titulo_libro = self._seleccionar_libro()
        if not isbn:
            return

        curso_alumno: Optional[str] = self.gestor_cursos.mostrar_y_seleccionar_curso()

        if not curso_alumno:
            print("Selección de curso cancelada o fallida")
            return

        alumno_data: Optional[List[dict]] = self.database_alumno.seleccionar_alumno(nie)
        if not alumno_data:
            print(f"Error: No se encontraron datos del alumno con nie '{nie}'.")
            return

        libro: Optional[Libro] = self.database_libro.seleccionar_libro(isbn)
        if libro is None:
            print(f"Error: No se encontró el libro con ISBN '{isbn}'.")
            return

        if libro and libro.numero_ejemplares > 0:
            fecha_entrega: date = date.today()
            fecha_fin_curso_estandar: date = date(date.today().year, 6, 30)
            if fecha_entrega > fecha_fin_curso_estandar:
                print(
                    f"ERROR: No se pueden realizar préstamos. La fecha actual ({fecha_entrega}) "
                    f"es posterior a la fecha límite de préstamos para este curso ({fecha_fin_curso_estandar}).")
                return

            fecha_devolucion: date = fecha_fin_curso_estandar
            estado: str = Estado.PRESTADO.value

            if self.database_prestamo.crear_prestamo(nie, curso_alumno, isbn, fecha_entrega, fecha_devolucion, estado):
                print(f"Préstamo realizado: Alumno '{nombre_alumno}' - Libro '{titulo_libro}' (ISBN: {isbn}).")
                print("(Contrato de préstamo generado ficticiamente)")
            else:
                print("Error al realizar el préstamo.")
        elif libro:
            print(f"El libro '{titulo_libro}' (ISBN: {isbn}) no está disponible en este momento.")
        else:
            print("Error al verificar la disponibilidad del libro.")

    def _realizar_devolucion(self) -> None:
        print("\n--- REALIZAR DEVOLUCIÓN DE LIBRO ---")
        nie_alumno: Optional[str]
        nombre_alumno: Optional[str]
        nie_alumno, nombre_alumno = self._seleccionar_alumno()
        if not nie_alumno:
            return

        prestamos_activos: List[dict] = self.database_prestamo.listar_prestamos_activos_por_alumno(nie_alumno)

        if not prestamos_activos:
            print(f"El alumno '{nombre_alumno}' no tiene préstamos activos.")
            return

        print(f"\n--- Préstamos activos de {nombre_alumno} (NIE: {nie_alumno}) ---")
        for i, prestamo_data in enumerate(prestamos_activos):
            libro: Optional[Libro] = self.database_libro.seleccionar_libro(prestamo_data['isbn'])
            titulo_libro: str = libro.titulo if libro else "Título Desconocido"
            print(f"{i + 1}. ISBN: {prestamo_data['isbn']} ({titulo_libro}) | "
                  f"Curso: {prestamo_data['curso']} | "
                  f"Fecha Entrega: {prestamo_data['fecha_entrega']}")

        while True:
            try:
                opcion_prestamo: int = int(input("Seleccione el número del préstamo a devolver (0 para cancelar): "))
                if opcion_prestamo == 0:
                    print("Devolución cancelada.")
                    return
                if 1 <= opcion_prestamo <= len(prestamos_activos):
                    prestamo_seleccionado_data: dict = prestamos_activos[opcion_prestamo - 1]
                    break
                else:
                    print("Opción no válida. Por favor, ingrese un número de la lista.")
            except ValueError:
                print("Entrada no válida. Por favor, introduzca un número.")

        nie: str = prestamo_seleccionado_data['nie']
        curso: str = prestamo_seleccionado_data['curso']
        isbn: str = prestamo_seleccionado_data['isbn']
        titulo_libro_obj: Optional[Libro] = self.database_libro.seleccionar_libro(isbn)
        titulo_libro_str: str = titulo_libro_obj.titulo if titulo_libro_obj else "Título Desconocido"


        if Estado(prestamo_seleccionado_data['estado']) == Estado.PRESTADO:
            fecha_devolucion: date = date.today()
            estado_nuevo: str = Estado.DEVUELTO.value

            if self.database_prestamo.update_prestamo(nie, curso, isbn, fecha_devolucion, estado_nuevo):
                print(f"Devolución registrada: Alumno '{nombre_alumno}' - "
                      f"Libro '{titulo_libro_str}' (ISBN: {isbn}, "
                      f"Curso: {curso}).")
            else:
                print("Error al registrar la devolución.")
        else:
            print("El préstamo seleccionado ya no está en estado 'Prestado'.")

    def _ver_lista_prestamos(self) -> None:
        print("\n--- LISTA DE PRÉSTAMOS ---")
        prestamos: Optional[List[dict]] = self.database_prestamo.show_prestamos()
        if prestamos:
            for prestamo in prestamos:
                alumno: Optional[List[dict]] = self.database_alumno.seleccionar_alumno(prestamo['nie'])
                libro: Optional[Libro] = self.database_libro.seleccionar_libro(prestamo['isbn'])
                nombre_alumno: str = alumno[0]['nombre'] + ' ' + alumno[0]['apellidos'] if alumno else "Desconocido"
                titulo_libro: str = libro.titulo if libro else "Desconocido"
                print(f"nie Alumno: {prestamo['nie']} ({nombre_alumno}), "
                      f"Curso: {prestamo['curso']}, "
                      f"ISBN Libro: {prestamo['isbn']} ({titulo_libro}), "
                      f"Fecha Entrega: {prestamo['fecha_entrega']}, "
                      f"Fecha Devolución: {prestamo['fecha_devolucion'] if prestamo['fecha_devolucion'] 
                                                                        else 'Pendiente'}, "
                      f"Estado: {prestamo['estado']}")
        else:
            print("No hay préstamos registrados.")

    def _borrar_prestamo(self) -> None:
        print("\n--- BORRAR PRÉSTAMO ---")
        nie_alumno: Optional[str]
        nombre_alumno: Optional[str]
        nie_alumno, nombre_alumno = self._seleccionar_alumno()
        if not nie_alumno:
            return

        prestamos_del_alumno: List[dict] = self.database_prestamo.listar_prestamos_activos_por_alumno(nie_alumno)

        if not prestamos_del_alumno:
            print(f"El alumno '{nombre_alumno}' no tiene préstamos activos para borrar.")
            return

        print(f"\n--- Préstamos de {nombre_alumno} (NIE: {nie_alumno}) ---")
        for i, prestamo_data in enumerate(prestamos_del_alumno):
            libro: Optional[Libro] = self.database_libro.seleccionar_libro(prestamo_data['isbn'])
            titulo_libro: str = libro.titulo if libro else "Título Desconocido"
            estado_prestamo: str = Estado(prestamo_data['estado']).name
            print(f"{i + 1}. ISBN: {prestamo_data['isbn']} ({titulo_libro}) | "
                  f"Curso: {prestamo_data['curso']} | "
                  f"Estado: {estado_prestamo} | "
                  f"Fecha Entrega: {prestamo_data['fecha_entrega']}")

        while True:
            try:
                opcion_prestamo: int = int(input("Seleccione el número del préstamo a borrar (0 para cancelar): "))
                if opcion_prestamo == 0:
                    print("Borrado cancelado.")
                    return
                if 1 <= opcion_prestamo <= len(prestamos_del_alumno):
                    prestamo_seleccionado_data: dict = prestamos_del_alumno[opcion_prestamo - 1]
                    break
                else:
                    print("Opción no válida. Por favor, ingrese un número de la lista.")
            except ValueError:
                print("Entrada no válida. Por favor, introduzca un número.")


        nie: str = prestamo_seleccionado_data['nie']
        curso: str = prestamo_seleccionado_data['curso']
        isbn: str = prestamo_seleccionado_data['isbn']
        titulo_libro_obj: Optional[Libro] = self.database_libro.seleccionar_libro(isbn)
        titulo_libro_str: str = titulo_libro_obj.titulo if titulo_libro_obj else "Título Desconocido"


        confirmacion: str = input(f"¿Está seguro de que desea borrar el préstamo del alumno con nie '{nie}' para el "
                             f"libro con ISBN '{isbn}' y curso '{curso}'? (s/n): ").lower()
        if confirmacion == 's':
            if self.database_prestamo.del_prestamo(nie, curso, isbn):
                print(f"Préstamo del alumno '{nombre_alumno}' - "
                      f"Libro '{titulo_libro_str}' (ISBN: {isbn}, "
                      f"Curso: {curso}) borrado con éxito.")
            else:
                print(f"Error al borrar el préstamo.")
        else:
            print("Operación de borrado cancelada.")
