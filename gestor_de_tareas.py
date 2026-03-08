# Importamos la librería json para leer y guardar datos en un archivo de texto estructurado.
import json
# Importamos la librería os para interactuar con el sistema operativo (ej. verificar si un archivo existe).
import os
# Del módulo datetime, importamos la clase datetime para manejar y validar fechas.
from datetime import datetime

# CONSTANTES DEL SISTEMA
# Tuplas para definir opciones inmutables del sistema
PRIORIDADES_VALIDAS = ("Alta", "Media", "Baja")
ESTADOS_VALIDOS = ("Pendiente", "Completo")

# CLASES (Programación Orientada a Objetos)
class Tarea:
    """Clase que representa una tarea individual en el sistema."""
    
    def __init__(self, id_tarea, descripcion, responsable, fecha_limite, prioridad, estado="Pendiente"):
        self.id = id_tarea
        self.descripcion = descripcion
        self.responsable = responsable
        self.fecha_limite = fecha_limite
        self.prioridad = prioridad
        self.estado = estado

    def to_dict(self):
        """Convierte el objeto en un diccionario para poder guardarlo en JSON."""
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            "fecha_limite": self.fecha_limite,
            "responsable": self.responsable,
            "prioridad": self.prioridad,
            "estado": self.estado
        }

class GestorTareas:
    """Clase controladora que maneja la lógica de negocio y la persistencia de datos."""
    
    def __init__(self):
        # Permite al usuario personalizar el nombre del archivo de guardado
        nombre_proyecto = input("Ingrese el nombre del proyecto o archivo (sin extensión): ").strip()
        self.archivo = f"{nombre_proyecto}.json"
        # Al instanciar el gestor, automáticamente cargamos las tareas guardadas
        self.tareas = self.cargar_tareas()

    def cargar_tareas(self):
        """Lee el archivo JSON y convierte los datos en objetos Tarea."""
        # Validamos si el archivo existe en el sistema operativo
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r", encoding="utf-8") as file:
                    datos = json.load(file)
                    
                    # Asignamos explícitamente cada llave del diccionario JSON 
                    # a su respectivo parámetro en el constructor de la clase Tarea para evitar el TypeError.
                    return [
                        Tarea(
                            id_tarea=t["id"],
                            descripcion=t["descripcion"],
                            responsable=t["responsable"],
                            fecha_limite=t["fecha_limite"],
                            prioridad=t["prioridad"],
                            estado=t["estado"]
                        ) for t in datos
                    ]
            except json.JSONDecodeError:
                print("Error: El archivo JSON está corrupto. Iniciando con lista vacía.")
                return []
        # Si el archivo no existe, retornamos una lista vacía para empezar
        return []

    def guardar_tareas(self):
        """Sobrescribe el archivo JSON con la lista actual de tareas."""
        with open(self.archivo, "w", encoding="utf-8") as file:
            # Convertimos los objetos Tarea a diccionarios antes de guardar
            json.dump([tarea.to_dict() for tarea in self.tareas], file, indent=4, ensure_ascii=False)

    def generar_id(self):
        """Genera un ID autoincrementable basado en las tareas existentes."""
        if not self.tareas:
            return 1
        return max(tarea.id for tarea in self.tareas) + 1

    def validar_fecha(self, fecha_str):
        """Valida que el texto ingresado sea una fecha correcta y no sea del pasado."""
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_obj < datetime.now().date():
                print("Error: Solo se permiten fechas actuales o posteriores.")
                return None
            return fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Error: Formato de fecha inválido. Use YYYY-MM-DD.")
            return None

    # MÉTODOS CRUD (Crear, Leer, Actualizar, Eliminar)
    def crear_tarea(self):
        print("\n--- NUEVA TAREA ---")
        descripcion = input("Descripción: ").strip()
        responsable = input("Responsable: ").strip()

        while True:
            fecha = input("Fecha límite (YYYY-MM-DD): ").strip()
            fecha_validada = self.validar_fecha(fecha)
            if fecha_validada:
                break

        while True:
            # Usamos strip() para quitar espacios y luego capitalize() para normalizar el texto
            prioridad = input("Prioridad (Alta/Media/Baja): ").strip().capitalize()
            if prioridad in PRIORIDADES_VALIDAS:
                break
            print("Prioridad inválida.")

        nueva_tarea = Tarea(self.generar_id(), descripcion, responsable, fecha_validada, prioridad)
        self.tareas.append(nueva_tarea)
        self.guardar_tareas()
        print("-> Tarea registrada exitosamente.")

    def visualizar_tareas(self):
        if not self.tareas:
            print("\nNo hay tareas registradas en este proyecto.")
            return

        fecha_actual = datetime.now().date()
        print(f"\n--- LISTA DE TAREAS [{self.archivo}] ---")
        
        for tarea in self.tareas:
            fecha_tarea = datetime.strptime(tarea.fecha_limite, "%Y-%m-%d").date()
            dias_restantes = (fecha_tarea - fecha_actual).days
            
            alerta = ""
            if dias_restantes < 0 and tarea.estado != "Completo":
                alerta = " [¡VENCIDA!]"
            elif dias_restantes <= 3 and tarea.estado != "Completo":
                alerta = " [Próxima a vencer]"

            print("-" * 40)
            print(f"ID: {tarea.id}")
            print(f"Descripción: {tarea.descripcion}")
            print(f"Fecha Límite: {tarea.fecha_limite} ({dias_restantes} días){alerta}")
            print(f"Responsable: {tarea.responsable}")
            print(f"Prioridad: {tarea.prioridad}")
            print(f"Estado: {tarea.estado}")
        print("-" * 40)

    def actualizar_tarea(self):
        try:
            id_tarea = int(input("\nIngrese el ID de la tarea a actualizar: ").strip())
        except ValueError:
            print("Error: El ID debe ser un número entero.")
            return

        for tarea in self.tareas:
            if tarea.id == id_tarea:
                print(f"Editando tarea: {tarea.descripcion}")
                
                # Si el usuario presiona Enter sin escribir nada, el strip() deja una cadena vacía ""
                # y el operador 'or' mantendrá el valor actual (tarea.descripcion)
                tarea.descripcion = input("Nueva descripción (Enter para omitir): ").strip() or tarea.descripcion
                tarea.responsable = input("Nuevo Responsable (Enter para omitir): ").strip() or tarea.responsable
                
                # Bucle de estado
                while True:
                    nuevo_estado = input("Nuevo estado (Pendiente/Completo): ").strip().capitalize()
                    if nuevo_estado in ESTADOS_VALIDOS:
                        tarea.estado = nuevo_estado
                        break
                    print("Estado inválido. Debe ser 'Pendiente' o 'Completo'.")
                
                self.guardar_tareas()
                print("-> Tarea actualizada correctamente.")
                return
        print("Tarea no encontrada.")

    def eliminar_tarea(self):
        try:
            id_tarea = int(input("\nIngrese el ID de la tarea a eliminar: ").strip())
        except ValueError:
            print("Error: El ID debe ser un número entero.")
            return

        for tarea in self.tareas:
            if tarea.id == id_tarea:
                self.tareas.remove(tarea)
                self.guardar_tareas()
                print("-> Tarea eliminada del sistema.")
                return
        print("Tarea no encontrada.")

# BLOQUE PRINCIPAL DE EJECUCIÓN
def main():
    print("=== SISTEMA DE GESTIÓN DE PROYECTOS ===")
    gestor = GestorTareas()

    while True:
        print("\n--- Menú Principal ---")
        print("1. Crear nueva tarea")
        print("2. Visualizar tareas")
        print("3. Actualizar tarea")
        print("4. Eliminar tarea")
        print("5. Salir")

        # Limpiamos también la opción del menú
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            gestor.crear_tarea()
        elif opcion == "2":
            gestor.visualizar_tareas()
        elif opcion == "3":
            gestor.actualizar_tarea()
        elif opcion == "4":
            gestor.eliminar_tarea()
        elif opcion == "5":
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    main()