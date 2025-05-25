

from ui.menu import Menu
from ui.menu_alumno import MenuAlumno
from ui.menu_libro import MenuLibro
from ui.menu_prestamo import MenuPrestamo
import bcrypt
import os
from typing import List

class MenuPrincipal(Menu):
    def __init__(self,
                 database_manager,
                 database_libro,
                 database_alumno,
                 database_prestamo,
                 database_materias_cursos):
        super().__init__()
        self.database_manager = database_manager
        self.database_libro = database_libro
        self.database_alumno = database_alumno
        self.database_prestamo = database_prestamo
        self.database_materias_cursos = database_materias_cursos
        self.menu_alumno = MenuAlumno(database_alumno, database_materias_cursos)
        self.menu_libro = MenuLibro(database_libro, database_materias_cursos, database_materias_cursos)
        self.menu_prestamo = MenuPrestamo(database_prestamo,
                                          database_libro,
                                          database_alumno,
                                          database_materias_cursos,
                                          database_manager)
        self.usuario_activo = None


    def _mostrar_menu(self):
        print("\n=== MENÚ PRINCIPAL ===")
        if self.usuario_activo:
            print(f"Usuario activo: {self.usuario_activo['username']}")
        else:
            print("Usuario no autenticado")
        print("1. Cargar datos iniciales")
        print("2. Menú de alumnos")
        print("3. Menú de libros")
        print("4. Menú de préstamos")
        print("5. Realizar backup de datos")
        print("6. Cargar alumnos del nuevo curso")
        print("7. Cerrar sesión")
        print("8. Salir")
        print("=======================")

    def _tratar_opcion(self, opcion):
        if not self.usuario_activo and opcion not in [8]:
            print("Debes iniciar sesión para acceder a esta opción.")
            return

        match opcion:
            case 1:
                self._cargar_datos_iniciales()
            case 2:
                self.menu_alumno.main()
            case 3:
                self.menu_libro.main()
            case 4:
                self.menu_prestamo.main()
            case 5:
                self._realizar_backup()
            case 6:
                self._cargar_alumnos_nuevo_curso()
            case 7:
                self._cerrar_sesion()
            case 8:
                print("Saliendo de la aplicación.")
                return False
            case _:
                print("Opción no válida.")
        return True

    def main(self):
        self._autenticar_usuario()
        if self.usuario_activo:
            while True:
                self._mostrar_menu()
                opcion = self._recoger_opcion()
                if not self._tratar_opcion(opcion):
                    break
        else:
            print("No se pudo iniciar sesión. Saliendo de la aplicación.")

    def _recoger_opcion(self) -> int:
        while True:
            try:
                opcion: int = int(input("Seleccione una opción: "))
                return opcion
            except ValueError:
                print("Por favor, introduzca un número.")


    def _autenticar_usuario(self):
        print("\n=== INICIO DE SESIÓN ===")
        username = input("Nombre de usuario: ")
        password = input("Contraseña: ")

        stored_hash = self.database_manager.obtener_password_hash(username)

        if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Inicio de sesión exitoso.")
            self.usuario_activo = {'username': username}
            return True
        else:
            print("Nombre de usuario o contraseña incorrectos.")
            return False

    def _cargar_datos_iniciales(self):
        print("\n=== CARGAR DATOS INICIALES ===")
        confirmacion = input("¿Está seguro de que desea cargar los datos iniciales? Esto puede sobrescribir los datos existentes. (s/n): ").lower()
        if confirmacion == 's':
            self.database_materias_cursos.cargar_csv_alumnos()
            self.database_materias_cursos.cargar_csv_libros()
            self.database_materias_cursos.cargar_csv_cursos_materias()
            print("Carga de datos iniciales completada.")
        else:
            print("Operación de carga de datos iniciales cancelada.")

    def _realizar_backup(self):
        print("\n=== REALIZAR BACKUP ===")
        self.database_manager.bbdd_backup()

    def _cargar_alumnos_nuevo_curso(self):
        print("\n=== CARGAR ALUMNOS NUEVO CURSO ===")
        archivo_nuevo_curso = input("Introduzca la ruta del archivo CSV con los alumnos del nuevo curso: ")
        if os.path.exists(archivo_nuevo_curso):
            self.database_manager.cargar_alumnos_nuevo_curso(archivo_nuevo_curso)
        else:
            print("El archivo especificado no existe.")

    def _cerrar_sesion(self):
        print("Cerrando sesión.")
        self.usuario_activo = None
