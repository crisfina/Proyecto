from ui.menu import Menu
from clases.libro import Libro
from clases.materia import Materia
from clases.curso import Curso
from typing import Optional, Tuple, List, Any, Union


class MenuLibro(Menu):
    def __init__(self, database_libro: Any, database_curso: Any, database_materias_cursos: Any):
        super().__init__()
        self.database_libro = database_libro
        self.database_curso = database_curso
        self.database_materias_cursos = database_materias_cursos

    def _mostrar_menu(self) -> None:
        print("\n--- MENÚ DE LIBROS ---")
        print("1. Añadir libro")
        print("2. Ver datos de un libro")
        print("3. Modificar libro")
        print("4. Ver lista de libros")
        print("5. Borrar libro")
        print("6. Volver al menú principal")
        print("----------------------")

    def _tratar_opcion(self, opcion: int) -> bool:
        match opcion:
            case 1:
                self._anadir_libro()
            case 2:
                self._ver_datos_libro()
            case 3:
                self._modificar_libro()
            case 4:
                self._ver_lista_libros()
            case 5:
                self._borrar_libro()
            case 6:
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

    def _pedir_dato(self, mensaje: str, tipo: type,
                    funcion_validacion: Optional[Any] = None, valor_por_defecto: Optional[Any] = None) -> Any:
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

    def _seleccionar_materia(self) -> Optional[int]:
        materias: Optional[List[dict]] = self.database_materias_cursos.show_materias()
        if not materias:
            print("No hay materias disponibles.")
            return None
        print("Seleccione la materia:")
        for i, materia in enumerate(materias):
            print(f"{i + 1}. {materia['nombre']} ({materia['departamento']})")
        while True:
            try:
                opcion: int = int(input("Opción: "))
                if 1 <= opcion <= len(materias):
                    return materias[opcion - 1]['id']
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, introduzca un número.")

    def _seleccionar_curso(self) -> Optional[str]:
        cursos: Optional[List[dict]] = self.database_materias_cursos.show_cursos()
        if not cursos:
            print("No hay cursos disponibles.")
            return None
        print("Seleccione el curso:")
        for i, curso in enumerate(cursos):
            print(f"{i + 1}. {curso['curso']}")
        while True:
            try:
                opcion: int = int(input("Opción: "))
                if 1 <= opcion <= len(cursos):
                    return cursos[opcion - 1]['curso']
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, introduzca un número.")

    def _anadir_libro(self) -> None:
        print("\n--- AÑADIR LIBRO ---")

        while True:
            isbn_input: str = self._pedir_dato("ISBN: ", str)
            try:
                Libro(isbn=isbn_input, titulo="temp", autor="temp")
                isbn: str = isbn_input
                break
            except ValueError as e:
                print(f"Error de formato de ISBN: {e}. Por favor, intente de nuevo.")

        if self.database_libro.seleccionar_libro(isbn):
            print(f"Error: Ya existe un libro con el ISBN '{isbn}'. No se puede añadir duplicado.")
            return

        titulo: str = self._pedir_dato("Título: ", str)
        autor: str = self._pedir_dato("Autor: ", str)
        while True:
            num_ejemplares_str: str = input("Número de ejemplares: ").strip()
            if num_ejemplares_str.isdigit():
                num_ejemplares: int = int(num_ejemplares_str)
                if num_ejemplares >= 0:
                    break
                else:
                    print("El número de ejemplares debe ser un valor no negativo.")
            else:
                print("Por favor, introduzca un número entero para los ejemplares.")

        materia_id: Optional[int] = self._seleccionar_materia()
        curso_str: Optional[str] = self._seleccionar_curso()

        if materia_id and curso_str:
            libro: Libro = Libro(isbn=isbn, titulo=titulo, autor=autor, numero_ejemplares=num_ejemplares,
                          materia=Materia(id_materia=materia_id, nombre="", departamento=""),
                          curso=Curso(anio=curso_str.split('-')[0], curso=curso_str.split('-')[1]))
            if self.database_libro.insertar_libro(libro.isbn,
                                                  libro.titulo,
                                                  libro.autor,
                                                  libro.numero_ejemplares,
                                                  libro.materia.id_materia,
                                                  curso_str):
                print(f"Libro '{libro.titulo}' con ISBN '{libro.isbn}' añadido.")
            else:
                print("Error al añadir el libro.")
        else:
            print("No se pudo añadir el libro porque no se seleccionaron materia y/o curso.")

    def _ver_datos_libro(self) -> None:
        print("\n--- VER DATOS DE UN LIBRO ---")
        isbn: str = input("Introduzca el ISBN del libro que desea ver: ").strip()
        libro_data: Optional[Libro] = self.database_libro.seleccionar_libro(isbn)
        if libro_data:
            print(f"ISBN: {libro_data.isbn}")
            print(f"Título: {libro_data.titulo}")
            print(f"Autor: {libro_data.autor}")
            print(f"Número de ejemplares: {libro_data.numero_ejemplares}")
            print(f"Materia: {libro_data.materia.nombre} ({libro_data.materia.departamento})")
            print(f"Curso: {libro_data.curso.curso}")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn}'.")

    def _modificar_libro(self) -> None:
        print("\n--- MODIFICAR LIBRO ---")
        isbn_modificar: str = input("Introduzca el ISBN del libro que desea modificar: ").strip()
        libro_existente: Optional[Libro] = self.database_libro.seleccionar_libro(isbn_modificar)
        if libro_existente:
            print("\nDeje los campos en blanco si no desea modificarlos.")
            titulo: str = input(f"Nuevo título ({libro_existente.titulo}): ").strip() or libro_existente.titulo
            autor: str = input(f"Nuevo autor ({libro_existente.autor}): ").strip() or libro_existente.autor
            while True:
                num_ejemplares_str: str = input(f"Nuevo número de ejemplares "
                                           f"({libro_existente.numero_ejemplares}): ").strip()
                if not num_ejemplares_str:
                    nuevo_num_ejemplares: int = libro_existente.numero_ejemplares
                    break
                elif num_ejemplares_str.isdigit():
                    nuevo_num_ejemplares = int(num_ejemplares_str)
                    if nuevo_num_ejemplares >= 0:
                        break
                    else:
                        print("El número de ejemplares debe ser un valor no negativo.")
                else:
                    print("Por favor, introduzca un número entero para los ejemplares.")

            if self.database_libro.modificar_libro(isbn_modificar, titulo, autor, nuevo_num_ejemplares):
                print(f"Libro con ISBN '{isbn_modificar}' modificado con éxito.")
            else:
                print(f"Error al modificar el libro con ISBN '{isbn_modificar}'.")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn_modificar}'.")

    def _ver_lista_libros(self) -> None:
        print("\n--- LISTA DE LIBROS ---")
        libros: Optional[List[dict]] = self.database_libro.show_libros()
        if libros:
            for libro in libros:
                print(f"ISBN: {libro['isbn']}, Título: {libro['titulo']}, Autor: {libro['autor']}, "
                      f"Ejemplares: {libro['numero_ejemplares']}, "
                      f"Materia: {libro['materia_nombre']}, Curso: {libro['curso_nivel']}")
        else:
            print("No hay libros registrados.")

    def _borrar_libro(self) -> None:
        print("\n--- BORRAR LIBRO ---")
        isbn_borrar: str = input("Introduzca el ISBN del libro que desea borrar: ").strip()
        libro_existente: Optional[Libro] = self.database_libro.seleccionar_libro(isbn_borrar)
        if libro_existente:
            confirmacion: str = input(f"¿Está seguro de que desea borrar el libro con ISBN '{isbn_borrar}'? (s/n): ").lower()
            if confirmacion == 's':
                if self.database_libro.del_libro(isbn_borrar):
                    print(f"Libro con ISBN '{isbn_borrar}' borrado con éxito.")
                else:
                    print(f"Error al borrar el libro con ISBN '{isbn_borrar}'.")
            else:
                print("Operación de borrado cancelada.")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn_borrar}'.")
