

from ui.menu import Menu
from clases.alumno import Alumno
from clases.enum_tramos import Tramos

class MenuAlumno(Menu):
    def __init__(self, database_alumno, database_materias_cursos):
        super().__init__()
        self.database_alumno = database_alumno
        self.database_curso = database_materias_cursos

    def _mostrar_menu(self):
        print("\n--- MENÚ DE ALUMNOS ---")
        print("1. Crear alumno")
        print("2. Ver datos de un alumno")
        print("3. Modificar alumno")
        print("4. Ver lista de alumnos")
        print("5. Borrar alumno")
        print("6. Volver al menú principal")
        print("-----------------------")

    def _tratar_opcion(self, opcion):
        match opcion:
            case 1:
                self._crear_alumno()
            case 2:
                self._ver_datos_alumno()
            case 3:
                self._modificar_alumno()
            case 4:
                self._ver_lista_alumnos()
            case 5:
                self._borrar_alumno()
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

    def _seleccionar_tramo(self):
        print("Seleccione el tramo:")
        for tramo in Tramos:
            if tramo != Tramos.NADA:
                print(f"{tramo.value}. {tramo.name.replace('TRAMO_', 'Tramo ')}")
        while True:
            try:
                opcion = int(input("Opción: "))
                for tramo in Tramos:
                    if tramo != Tramos.NADA and tramo.value == opcion:
                        return tramo
                if opcion == 0:
                    return Tramos.NADA
                print("Opción no válida.")
            except ValueError:
                print("Por favor, introduzca un número.")



    def _crear_alumno(self):
        print("\n--- CREAR ALUMNO ---")
        nie = self._pedir_dato("nie (ej: 12345678A): ", str)
        nombre = self._pedir_dato("Nombre: ", str)
        apellidos = self._pedir_dato("Apellidos: ", str)
        tramo = self._seleccionar_tramo()
        bilingue_str = input("¿Es bilingüe? (s/n): ").strip().lower()
        bilingue = True if bilingue_str == 's' else False

        alumno = Alumno(nie=nie, nombre=nombre, apellidos=apellidos, tramo=tramo, bilingue=bilingue)
        if self.database_alumno.insertar_alumno(alumno.nie, alumno.nombre, alumno.apellidos, alumno.tramo,
                                                alumno.bilingue):
            print(f"Alumno '{alumno.nombre} {alumno.apellidos}' creado con nie '{alumno.nie}'.")
        else:
            print("Error al crear el alumno.")

    def _ver_datos_alumno(self):
        print("\n--- VER DATOS DE UN ALUMNO ---")
        nie = input("Introduzca el nie del alumno que desea ver: ").strip()
        alumno_data = self.database_alumno.seleccionar_alumno(nie)
        if alumno_data:
            alumno = alumno_data[0]
            tramo_str = Tramos(int(alumno['tramo'])).name.replace('TRAMO_', 'Tramo ') if alumno['tramo'] != '0' else 'Ninguno'
            bilingue_str = "Sí" if alumno['bilingue'] else "No"
            print(f"nie: {alumno['nie']}")
            print(f"Nombre: {alumno['nombre']}")
            print(f"Apellidos: {alumno['apellidos']}")
            print(f"Tramo: {tramo_str}")
            print(f"Bilingüe: {bilingue_str}")
        else:
            print(f"No se encontró ningún alumno con el nie '{nie}'.")

    def _modificar_alumno(self):
        print("\n--- MODIFICAR ALUMNO ---")
        nie_modificar = input("Introduzca el nie del alumno que desea modificar: ").strip()
        alumno_existente = self.database_alumno.seleccionar_alumno(nie_modificar)
        if alumno_existente:
            alumno_existente = alumno_existente[0]
            print("\nDeje los campos en blanco si no desea modificarlos.")
            nombre = input(f"Nuevo nombre ({alumno_existente['nombre']}): ").strip() or alumno_existente['nombre']
            apellidos = input(f"Nuevos apellidos ({alumno_existente['apellidos']}): ").strip() or alumno_existente['apellidos']

            print("Seleccione el nuevo tramo (deje en blanco para no modificar):")
            for tramo in Tramos:
                if tramo != Tramos.NADA:
                    print(f"{tramo.value}. {tramo.name.replace('TRAMO_', 'Tramo ')}")
            nuevo_tramo_input = input(f"Nuevo tramo ({Tramos(int(alumno_existente['tramo'])).name.replace('TRAMO_', 'Tramo ') if alumno_existente['tramo'] != '0' else 'Ninguno'}): ").strip()
            nuevo_tramo = Tramos(int(nuevo_tramo_input)) if nuevo_tramo_input else Tramos(int(alumno_existente['tramo']))

            bilingue_str = input(f"¿Es bilingüe? (s/n, actual: {'s' if alumno_existente['bilingue'] else 'n'}): ").strip().lower()
            nuevo_bilingue = True if bilingue_str == 's' else False if bilingue_str == 'n' else alumno_existente['bilingue']


            if self.database_alumno.modificar_alumno(nie_modificar, nombre, apellidos, nuevo_tramo, nuevo_bilingue):
                print(f"Alumno con nie '{nie_modificar}' modificado con éxito.")
            else:
                print(f"Error al modificar el alumno con nie '{nie_modificar}'.")
        else:
            print(f"No se encontró ningún alumno con el nie '{nie_modificar}'.")

    def _ver_lista_alumnos(self):
        print("\n--- LISTA DE ALUMNOS ---")
        alumnos = self.database_alumno.show_alumnos()
        if alumnos:
            for alumno in alumnos:
                tramo_str = Tramos(int(alumno['tramo'])).name.replace('TRAMO_', 'Tramo ') if alumno['tramo'] != '0' else 'Ninguno'
                bilingue_str = "Sí" if alumno['bilingue'] else "No"
                print(f"nie: {alumno['nie']}, Nombre: {alumno['nombre']} {alumno['apellidos']}, Tramo: {tramo_str}, Bilingüe: {bilingue_str}")
        else:
            print("No hay alumnos registrados.")

    def _borrar_alumno(self):
        print("\n--- BORRAR ALUMNO ---")
        nie_borrar = input("Introduzca el nie del alumno que desea borrar: ").strip()
        alumno_existente = self.database_alumno.seleccionar_alumno(nie_borrar)
        if alumno_existente:
            confirmacion = input(f"¿Está seguro de que desea borrar al alumno con nie '{nie_borrar}'? (s/n): ").lower()
            if confirmacion == 's':
                if self.database_alumno.del_alumno(nie_borrar):
                    print(f"Alumno con nie '{nie_borrar}' borrado con éxito.")
                else:
                    print(f"Error al borrar el alumno con nie '{nie_borrar}'.")
            else:
                print("Operación de borrado cancelada.")
        else:
            print(f"No se encontró ningún alumno con el nie '{nie_borrar}'.")