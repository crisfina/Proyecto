#En los comentarios están los prints de debug por los problemas con la base de datos. Algunos los he dejado ya que son
#útiles y aportan también info al usuario del proceso de carga del programa.

from database.gestion import GestionBBDD
from database.gestion_alumno import GestionAlumno
from database.gestion_libro import GestionLibro
from database.gestion_prestamo import GestionPrestamo
from database.gestion_materias_cursos import GestionMateriasCursos
from ui.menu_principal import MenuPrincipal
import bcrypt
#import getpass de momento no, problemas con el portátil

def crear_usuario_inicial(db_manager):
    print("Entrando en crear_usuario_inicial")
    if db_manager.obtener_password_hash('admin') is None:
        password = input("Introduzca la contraseña para el usuario 'admin': ")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        if db_manager.almacenar_password('admin', hashed_password.decode('utf-8')):
            print("Usuario 'admin' creado con éxito.")
        else:
            print("Error al crear el usuario 'admin'.")
    else:
        print("Cargando usuario...")
    #print("Saliendo de crear_usuario_inicial")

if __name__ == "__main__":
    print("Iniciando...")
    db_manager = GestionBBDD()

    #print("GestionBBDD inicializado")
    if db_manager.conexion:
        print("Conexión a la base de datos exitosa")
        db_alumno = GestionAlumno(db_manager)
        db_libro = GestionLibro(db_manager)
        db_prestamo = GestionPrestamo(db_manager)
        db_materias_cursos = GestionMateriasCursos(db_manager)

        crear_usuario_inicial(db_manager)
        print("Usuario inicial correcto")
        menu_principal = MenuPrincipal(db_manager, db_libro, db_alumno, db_prestamo, db_materias_cursos)
        #print("MenuPrincipal inicializado")
        menu_principal.main()
        #print("MenuPrincipal.main() completado")
        db_manager.cerrar_conexion()
        print("Conexión a la base de datos cerrada")
    else:
        print("No se pudo iniciar la aplicación debido a un error en la conexión a la base de datos.")
    print("Saliendo de main")