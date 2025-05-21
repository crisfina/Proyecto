#al separar los menús he duplicado seleccionar curso en menu libro o alumno, encontrar lo que llama al duplicado y cambiar
from database.gestion_materias_cursos import GestionMateriasCursos
from ui.menu import Menu
from clases.libro import Libro
from clases.materia import Materia
from clases.curso import Curso


class MenuLibro(Menu):
    def __init__(self, database_libro, database_curso, database_materias_cursos):
        super().__init__()
        self.database_libro = database_libro
        self.database_curso = database_curso
        self.database_materias_cursos = database_materias_cursos

    def _mostrar_menu(self):
        print("\n--- MENÚ DE LIBROS ---")
        print("1. Añadir libro")
        print("2. Ver datos de un libro")
        print("3. Modificar libro")
        print("4. Ver lista de libros")
        print("5. Borrar libro")
        print("6. Volver al menú principal")
        print("----------------------")

    def _tratar_opcion(self, opcion):
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

    def _seleccionar_materia(self):
        materias = self.database_materias_cursos.show_materias()
        if not materias:
            print("No hay materias disponibles.")
            return None
        print("Seleccione la materia:")
        for i, materia in enumerate(materias):
            print(f"{i + 1}. {materia['nombre']} ({materia['departamento']})")
        while True:
            try:
                opcion = int(input("Opción: "))
                if 1 <= opcion <= len(materias):
                    return materias[opcion - 1]['id']
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, introduzca un número.")

    def _seleccionar_curso(self):
        cursos = self.database_materias_cursos.show_cursos()
        if not cursos:
            print("No hay cursos disponibles.")
            return None
        print("Seleccione el curso:")
        for i, curso in enumerate(cursos):
            print(f"{i + 1}. {curso['curso']}")
        while True:
            try:
                opcion = int(input("Opción: "))
                if 1 <= opcion <= len(cursos):
                    return cursos[opcion - 1]['curso']
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, introduzca un número.")

    def _anadir_libro(self):
        print("\n--- AÑADIR LIBRO ---")
        isbn = self._pedir_dato("ISBN: ", str)
        titulo = self._pedir_dato("Título: ", str)
        autor = self._pedir_dato("Autor: ", str)
        while True:
            num_ejemplares_str = input("Número de ejemplares: ").strip()
            if num_ejemplares_str.isdigit():
                num_ejemplares = int(num_ejemplares_str)
                if num_ejemplares >= 0:
                    break
                else:
                    print("El número de ejemplares debe ser un valor no negativo.")
            else:
                print("Por favor, introduzca un número entero para los ejemplares.")

        materia_id = self._seleccionar_materia()
        curso_str = self._seleccionar_curso()

        if materia_id and curso_str:
            libro = Libro(isbn=isbn, titulo=titulo, autor=autor, numero_ejemplares=num_ejemplares,
                          materia=Materia(id_materia=materia_id, nombre="", departamento=""), #Carga BBDD
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

    def _ver_datos_libro(self):
        print("\n--- VER DATOS DE UN LIBRO ---")
        isbn = input("Introduzca el ISBN del libro que desea ver: ").strip()
        libro_data = self.database_libro.seleccionar_libro(isbn)
        if libro_data:
            print(f"ISBN: {libro_data.isbn}")
            print(f"Título: {libro_data.titulo}")
            print(f"Autor: {libro_data.autor}")
            print(f"Número de ejemplares: {libro_data.numero_ejemplares}")
            print(f"Materia: {libro_data.materia.nombre} ({libro_data.materia.departamento})")
            print(f"Curso: {libro_data.curso.curso}")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn}'.")

    def _modificar_libro(self):
        print("\n--- MODIFICAR LIBRO ---")
        isbn_modificar = input("Introduzca el ISBN del libro que desea modificar: ").strip()
        libro_existente = self.database_libro.seleccionar_libro(isbn_modificar)
        if libro_existente:
            print("\nDeje los campos en blanco si no desea modificarlos.")
            titulo = input(f"Nuevo título ({libro_existente.titulo}): ").strip() or libro_existente.titulo
            autor = input(f"Nuevo autor ({libro_existente.autor}): ").strip() or libro_existente.autor
            while True:
                num_ejemplares_str = input(f"Nuevo número de ejemplares "
                                           f"({libro_existente.numero_ejemplares}): ").strip()
                if not num_ejemplares_str:
                    nuevo_num_ejemplares = libro_existente.numero_ejemplares
                    break
                elif num_ejemplares_str.isdigit():
                    nuevo_num_ejemplares = int(num_ejemplares_str)
                    if nuevo_num_ejemplares >= 0:
                        break
                    else:
                        print("El número de ejemplares debe ser un valor numérico positivo.")
                else:
                    print("Por favor, introduzca un número entero para los ejemplares.")

            if self.database_libro.modificar_libro(isbn_modificar, titulo, autor, nuevo_num_ejemplares):
                print(f"Libro con ISBN '{isbn_modificar}' modificado con éxito.")
            else:
                print(f"Error al modificar el libro con ISBN '{isbn_modificar}'.")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn_modificar}'.")

    def _ver_lista_libros(self):
        print("\n--- LISTA DE LIBROS ---")
        libros = self.database_libro.show_libros()
        if libros:
            for libro in libros:
                print(f"ISBN: {libro['isbn']}, Título: {libro['titulo']}, Autor: {libro['autor']}, "
                      f"Ejemplares: {libro['numero_ejemplares']}, "
                      f"Materia: {libro['materia_nombre']}, Curso: {libro['curso_nivel']}")
        else:
            print("No hay libros registrados.")

    def _borrar_libro(self):
        print("\n--- BORRAR LIBRO ---")
        isbn_borrar = input("Introduzca el ISBN del libro que desea borrar: ").strip()
        libro_existente = self.database_libro.seleccionar_libro(isbn_borrar)
        if libro_existente:
            confirmacion = input(f"¿Está seguro de que desea borrar el libro con ISBN '{isbn_borrar}'? (s/n): ").lower()
            if confirmacion == 's':
                if self.database_libro.del_libro(isbn_borrar):
                    print(f"Libro con ISBN '{isbn_borrar}' borrado con éxito.")
                else:
                    print(f"Error al borrar el libro con ISBN '{isbn_borrar}'.")
            else:
                print("Operación de borrado cancelada.")
        else:
            print(f"No se encontró ningún libro con el ISBN '{isbn_borrar}'.")