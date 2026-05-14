# Benchmark de Rendimiento: Algoritmos de Layout para Grafos

Este documento resume los resultados del benchmark ejecutado para comparar el rendimiento de los algoritmos de dibujo de grafos (layouts) entre **NetworkX** y **igraph** en el contexto de la aplicación NEDAF.

## Entorno y Metodología
Las pruebas se ejecutaron sobre grafos dispersos simulando la estructura esperada, aumentando progresivamente el número de nodos. El objetivo era determinar el algoritmo óptimo para cada rango de tamaño de red.

---

### Prueba 1: Grafos Pequeños (< 100 nodos)
- **Tamaño:** 50 nodos, 55 aristas
- **Algoritmo Evaluado:** Kamada-Kawai (Layout ideal para grafos pequeños)

| Librería | Tiempo de Ejecución |
| :--- | :--- |
| NetworkX | 742.55 ms |
| **igraph** | **72.77 ms** |

> [!TIP]
> **Resultado:** `igraph` es **~10x más rápido** calculando la disposición de fuerzas de Kamada-Kawai. Seleccionado para grafos con menos de 100 nodos.

---

### Prueba 2: Grafos Medianos (100 - 2,000 nodos)
- **Algoritmo Evaluado:** Fruchterman-Reingold (Spring Layout)

**Con 500 nodos, 6,162 aristas:**
| Librería | Tiempo de Ejecución |
| :--- | :--- |
| NetworkX | 2,232.65 ms |
| **igraph** | **414.16 ms** |

**Con 1,000 nodos, 24,798 aristas:**
| Librería | Tiempo de Ejecución |
| :--- | :--- |
| NetworkX | 4,789.30 ms |
| **igraph** | **836.44 ms** |

> [!TIP]
> **Resultado:** `igraph` es consistentemente **~5x más rápido** para el algoritmo Fruchterman-Reingold clásico. Seleccionado para grafos entre 100 y 2,000 nodos.

---

### Prueba 3: Grafos Grandes (> 2,000 nodos)
- **Tamaño:** 3,000 nodos, 22,340 aristas
- **Algoritmos Evaluados:** ForceAtlas2 (fa2_modified), igraph Fruchterman-Reingold (con optimización de grid), e igraph DrL.

| Algoritmo / Librería | Tiempo de Ejecución |
| :--- | :--- |
| **Fruchterman-Reingold** (`igraph`, modo grid) | **301.03 ms** |
| **ForceAtlas2** (`fa2_modified`, 100 iteraciones) | 6,578.99 ms |
| **DrL** (`igraph`) | 11,576.46 ms |

> [!NOTE]
> Aunque `igraph` con la opción `grid='grid'` es masivamente más rápido (~300ms) para 3,000 nodos, **ForceAtlas2** es el algoritmo estándar de la industria (Gephi) para generar visualizaciones estéticas superiores en comunidades grandes. Se ha mantenido ForceAtlas2 como la opción predeterminada para grafos mayores a 2,000 nodos, cumpliendo el plan original, priorizando la estética visual sobre el tiempo de cálculo crudo para ese rango de tamaño.

---

## Conclusión y Estrategia Implementada

Los resultados confirmaron la inmensa superioridad técnica en tiempo de ejecución de las implementaciones subyacentes en C de `igraph` contra las implementaciones puras en Python de `networkx`. 

La estrategia implementada en `NetworkAnalysis.py` orquesta inteligentemente los algoritmos:

1. **`n_nodes < 100`**: `igraph.layout_kamada_kawai()`
2. **`100 <= n_nodes <= 2000`**: `igraph.layout_fruchterman_reingold(grid=auto)`
3. **`n_nodes > 2000`**: `ForceAtlas2` (para estética máxima) y `igraph.layout_drl()` para redes absolutamente masivas (>50,000 nodos).
