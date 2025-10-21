import time
import threading
from queue import Queue

def leer_lineas(ruta_entrada, cola_lectura):
    """Tarea 1: Lee líneas del archivo y las pone en una cola."""
    try:
        with open(ruta_entrada, 'r') as f:
            for linea in f:
                cola_lectura.put(linea)
        cola_lectura.put(None)  # Señal de finalización
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
        cola_lectura.put(None)

def limpiar_lineas(cola_lectura, cola_limpieza):
    """Tarea 2: Limpia las líneas (elimina espacios) y las pasa a la siguiente cola."""
    while True:
        linea = cola_lectura.get()
        if linea is None:
            cola_limpieza.put(None)
            break
        linea_limpia = linea.strip()
        cola_limpieza.put(linea_limpia)

def convertir_mayusculas(cola_limpieza, cola_mayusculas):
    """Tarea 3: Convierte las líneas a mayúsculas y las pasa a la siguiente cola."""
    while True:
        linea = cola_limpieza.get()
        if linea is None:
            cola_mayusculas.put(None)
            break
        linea_mayuscula = linea.upper()
        cola_mayusculas.put(linea_mayuscula)

def escribir_archivo(cola_mayusculas, ruta_salida):
    """Tarea 4: Escribe las líneas procesadas en el archivo de salida."""
    try:
        with open(ruta_salida, 'w') as f:
            while True:
                linea = cola_mayusculas.get()
                if linea is None:
                    break
                f.write(linea + '\n')
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")

def procesar_texto_pipeline(ruta_entrada, ruta_salida):
    """Procesa el texto usando un pipeline de tareas paralelas."""
    # Crear colas para comunicación entre tareas
    cola_lectura = Queue(maxsize=100)
    cola_limpieza = Queue(maxsize=100)
    cola_mayusculas = Queue(maxsize=100)

    # Crear hilos para cada tarea del pipeline
    hilo_leer = threading.Thread(target=leer_lineas, args=(ruta_entrada, cola_lectura))
    hilo_limpiar = threading.Thread(target=limpiar_lineas, args=(cola_lectura, cola_limpieza))
    hilo_mayusculas = threading.Thread(target=convertir_mayusculas, args=(cola_limpieza, cola_mayusculas))
    hilo_escribir = threading.Thread(target=escribir_archivo, args=(cola_mayusculas, ruta_salida))

    # Iniciar todos los hilos
    hilo_leer.start()
    hilo_limpiar.start()
    hilo_mayusculas.start()
    hilo_escribir.start()

    # Esperar a que todos los hilos terminen
    hilo_leer.join()
    hilo_limpiar.join()
    hilo_mayusculas.join()
    hilo_escribir.join()

if __name__ == '__main__':
    ruta_entrada = "texto_entrada.txt"
    ruta_salida = "texto_salida_pipeline.txt"

    inicio = time.time()
    procesar_texto_pipeline(ruta_entrada, ruta_salida)
    fin = time.time()

    print(f"Tiempo total de procesamiento con pipeline: {fin - inicio:.6f} segundos")
    print(f"Archivo procesado con pipeline guardado en {ruta_salida}")
