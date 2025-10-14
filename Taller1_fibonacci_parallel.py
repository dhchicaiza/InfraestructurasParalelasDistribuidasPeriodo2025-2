# Objetivo: Implementar el cálculo paralelo de números de Fibonacci usando
# concurrent.futures, identificando ciclos for paralelizables y evitando trampas seriales.

import time
import concurrent.futures
from functools import lru_cache

# Número de elementos de Fibonacci a calcular
N = 20

# FUNCIONES DE CÁLCULO DE FIBONACCI
def fibonacci(n):
    # Calcula el n-ésimo número de Fibonacci de forma recursiva pura.
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@lru_cache(maxsize=None)
def fibonacci_memo(n):
    # Calcula el n-ésimo número de Fibonacci con memoización.
    # Más eficiente que la versión recursiva pura.
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)


def fibonacci_iterativo(n):
    # Calcula el n-ésimo número de Fibonacci de forma iterativa.
    if n <= 1:
        return n

    fib_prev, fib_curr = 0, 1
    # CICLO FOR NO PARALELIZABLE:
    # - Cada iteración depende del resultado de la anterior
    # - fib_curr y fib_prev se actualizan secuencialmente
    # - Paralelizar esto sería imposible debido a las dependencias de datos
    for _ in range(2, n + 1):
        fib_prev, fib_curr = fib_curr, fib_prev + fib_curr

    return fib_curr

# FUNCIÓN AUXILIAR PARA MANTENER ÍNDICES
def calcular_fib_con_indice(indice):
    # Función auxiliar que calcula Fibonacci manteniendo el índice original.
    # Permite mantener el orden correcto de los resultados incluso cuando los cálculos paralelos terminan en diferente orden.
    return (indice, fibonacci(indice))

# IMPLEMENTACIÓN SECUENCIAL (REFERENCIA)

def calcular_fibonacci_secuencial(n_elementos):
    """
    Calcula números de Fibonacci de forma secuencial (sin paralelización).

    ANÁLISIS DEL CICLO FOR:
    - Este ciclo ES PARALELIZABLE en teoría
    - Cada iteración calcula fibonacci(i) independientemente
    - No hay dependencias entre iteraciones
    - Sin embargo, aquí se mantiene secuencial como referencia
    """
    inicio = time.time()
    resultados = []

    # CICLO FOR PARALELIZABLE (pero aquí se ejecuta serial)
    # Cada iteración es independiente
    # No hay modificación de estado compartido
    # Cada fibonacci(i) puede calcularse sin conocer fibonacci(j)
    for i in range(n_elementos):
        fib = fibonacci(i)
        resultados.append(fib)

    fin = time.time()
    tiempo_ejecucion = fin - inicio

    return tiempo_ejecucion, resultados

# IMPLEMENTACIÓN PARALELA - VERSION CORRECTA
def calcular_fibonacci_paralelo_correcto(n_elementos, executor_type):
    """
    Calcula números de Fibonacci en paralelo.

    SOLUCIÓN A LA TRAMPA SERIAL:
    1. Usamos una tupla (índice, resultado) para mantener el orden
    2. Almacenamos los futures con sus índices correspondientes
    3. Ordenamos los resultados DESPUÉS de que todos terminen
    4. Imprimimos de forma secuencial al final

    ANÁLISIS DEL CICLO FOR:
    - Ciclo 1 [línea con submit]: PARALELIZABLE
      * Cada submit() es independiente
      * Solo envía tareas al executor
      * No hay dependencias entre iteraciones

    - Ciclo 2 [as_completed]: NO PARALELIZABLE
      * Debe esperar a que los futures completen
      * Recolecta resultados de forma ordenada
      * Necesita sincronización
    """
    inicio = time.time()

    # Lista para almacenar resultados con índices
    resultados_con_indices = []

    with executor_type() as executor:
        # CICLO FOR #1: PARALELIZABLE
        # Este ciclo envía tareas al executor en paralelo
        # Cada submit() es independiente y no bloquea
        futures = {executor.submit(calcular_fib_con_indice, i): i
                   for i in range(n_elementos)}

        # CICLO FOR #2: NO PARALELIZABLE ✗
        # Este ciclo debe esperar resultados de forma sincronizada
        # as_completed() maneja la sincronización internamente
        # NOTA: No usamos print() aquí para evitar trampa serial
        for future in concurrent.futures.as_completed(futures):
            indice, resultado = future.result()
            resultados_con_indices.append((indice, resultado))

    # EVITANDO TRAMPA SERIAL: Ordenar resultados después de completar
    resultados_con_indices.sort(key=lambda x: x[0])
    resultados = [fib for _, fib in resultados_con_indices]

    fin = time.time()
    tiempo_ejecucion = fin - inicio

    return tiempo_ejecucion, resultados

# IMPLEMENTACIÓN PARALELA - VERSION PROBLEMÁTICA (para demostración)
def calcular_fibonacci_paralelo_problematico(n_elementos, executor_type):
    """
    Versión con TRAMPA SERIAL para demostrar el problema.

    PROBLEMA: Usa as_completed() sin mantener índices, resultando en
    orden aleatorio basado en qué tarea termina primero.
    """
    inicio = time.time()
    resultados = []

    with executor_type() as executor:
        futures = [executor.submit(fibonacci, i) for i in range(n_elementos)]

        # TRAMPA SERIAL: Los resultados aparecen en orden de finalización no en orden de envío
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    fin = time.time()
    tiempo_ejecucion = fin - inicio

    return tiempo_ejecucion, resultados

# FUNCIÓN DE IMPRESIÓN SEGURA (evita trampa serial)
def imprimir_resultados_seguro(resultados, titulo="Resultados"):
    """
    Imprime resultados de forma ordenada DESPUÉS de completar todos los cálculos.

    EVITANDO TRAMPA SERIAL:
    - No imprimimos durante el procesamiento paralelo
    - Esperamos a tener todos los resultados
    - Imprimimos secuencialmente al final
    """
    print(f"{titulo}")
    print(f"{'='*70}")

    for i, fib in enumerate(resultados):
        print(f"F({i:2d}) = {fib:,}")

# FUNCIÓN DE COMPARACIÓN Y ANÁLISIS
def comparar_implementaciones(n_elementos):
    """
    Compara las diferentes implementaciones y muestra análisis de rendimiento.
    """
    print(f"COMPARACIÓN DE IMPLEMENTACIONES - Calculando {n_elementos} números")
    print("="*70)

    # 1. Versión Secuencial
    print("\n[1] VERSIÓN SECUENCIAL (referencia)")
    tiempo_seq, resultados_seq = calcular_fibonacci_secuencial(n_elementos)
    print(f"Tiempo de ejecución: {tiempo_seq:.4f} segundos")

    # 2. Versión Paralela con ThreadPoolExecutor
    print("\n[2] VERSIÓN PARALELA - ThreadPoolExecutor (correcta)")
    tiempo_thread, resultados_thread = calcular_fibonacci_paralelo_correcto(
        n_elementos, concurrent.futures.ThreadPoolExecutor
    )
    print(f"Tiempo de ejecución: {tiempo_thread:.4f} segundos")
    speedup_thread = tiempo_seq / tiempo_thread if tiempo_thread > 0 else 0
    print(f"Speedup: {speedup_thread:.2f}x")

    # 3. Versión Paralela con ProcessPoolExecutor
    print("\n[3] VERSIÓN PARALELA - ProcessPoolExecutor (correcta)")
    tiempo_process, resultados_process = calcular_fibonacci_paralelo_correcto(
        n_elementos, concurrent.futures.ProcessPoolExecutor
    )
    print(f"Tiempo de ejecución: {tiempo_process:.4f} segundos")
    speedup_process = tiempo_seq / tiempo_process if tiempo_process > 0 else 0
    print(f"Speedup: {speedup_process:.2f}x")

    # Verificación de resultados
    print("VERIFICACIÓN DE RESULTADOS")
    print("="*70)

    if resultados_seq == resultados_thread == resultados_process:
        print("Todos los métodos producen resultados idénticos y correctos")
    else:
        print("Los resultados difieren entre métodos")

    # Imprimir resultados (evitando trampa serial)
    imprimir_resultados_seguro(resultados_thread, "Números de Fibonacci Calculados")

    # Análisis de rendimiento
    print("ANÁLISIS DE RENDIMIENTO")
    print("="*70)
    print(f"Secuencial:              {tiempo_seq:.4f}s (baseline)")
    print(f"ThreadPoolExecutor:      {tiempo_thread:.4f}s (speedup: {speedup_thread:.2f}x)")
    print(f"ProcessPoolExecutor:     {tiempo_process:.4f}s (speedup: {speedup_process:.2f}x)")

    mejor = "Threads" if tiempo_thread < tiempo_process else "Procesos"
    print(f"\nMejor rendimiento: {mejor}")

    return {
        'secuencial': (tiempo_seq, resultados_seq),
        'threads': (tiempo_thread, resultados_thread),
        'processes': (tiempo_process, resultados_process)
    }

# DEMOSTRACIÓN DE TRAMPA SERIAL
def demostrar_trampa_serial():
    """
    Demuestra el problema de la trampa serial y su solución.
    """
    print("DEMOSTRACIÓN: TRAMPA SERIAL EN IMPRESIÓN")
    print("="*70)

    n_demo = 10

    print("\n VERSIÓN PROBLEMÁTICA (orden aleatorio):")
    tiempo_prob, resultados_prob = calcular_fibonacci_paralelo_problematico(
        n_demo, concurrent.futures.ThreadPoolExecutor
    )
    print(f"Tiempo: {tiempo_prob:.4f}s")
    print(f"Resultados en orden de finalización: {resultados_prob}")
    print("NOTA: El orden depende de qué tarea termina primero")

    print("\n VERSIÓN CORRECTA (orden preservado):")
    tiempo_correcto, resultados_correcto = calcular_fibonacci_paralelo_correcto(
        n_demo, concurrent.futures.ThreadPoolExecutor
    )
    print(f"Tiempo: {tiempo_correcto:.4f}s")
    print(f"Resultados en orden correcto: {resultados_correcto}")
    print("NOTA: El orden se mantiene usando índices y ordenamiento posterior")

# FUNCIÓN PRINCIPAL
def main():
    """
    Función principal que ejecuta todas las demostraciones y análisis.
    """
    print("\nUsando concurrent.futures para paralelización")
    print("="*70)

    comparar_implementaciones(N)

    demostrar_trampa_serial()

if __name__ == "__main__":
    main()
