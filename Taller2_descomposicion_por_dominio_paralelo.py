import os
import time
from multiprocessing import Pool, cpu_count
from PIL import Image

def convertir_a_gris(ruta_imagen):
    try:
        imagen = Image.open(ruta_imagen)
        imagen_gris = imagen.convert('L')
        nombre_archivo, extension = os.path.splitext(ruta_imagen)
        ruta_gris = nombre_archivo + "_gris" + extension
        imagen_gris.save(ruta_gris)
        print(f"Imagen convertida: {ruta_imagen} -> {ruta_gris}")
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen {ruta_imagen}")
    except Exception as e:
        print(f"Error al procesar {ruta_imagen}: {e}")

def procesar_imagenes_paralelo(lista_imagenes: list[str], num_procesos: int | None = None):
    """Procesa una lista de imágenes en paralelo usando descomposición por dominio."""
    if num_procesos is None:
        num_procesos = min(cpu_count(), len(lista_imagenes))
    with Pool(processes=num_procesos) as pool:
        pool.map(convertir_a_gris, lista_imagenes)

if __name__ == '__main__':
    directorio_imagenes = "imagenes_prueba" # Reemplaza con el nombre de tu directorio
    lista_imagenes = [
        os.path.join(directorio_imagenes, f) 
        for f in os.listdir(directorio_imagenes) 
        if os.path.isfile(os.path.join(directorio_imagenes, f))
    ]
    print(f"\n Imágenes encontradas: {len(lista_imagenes)}\n")
    inicio = time.time()
    procesar_imagenes_paralelo(lista_imagenes)
    fin = time.time()
    print(f"Tiempo total paralelo: {fin - inicio:.2f} segundos\n")


        
