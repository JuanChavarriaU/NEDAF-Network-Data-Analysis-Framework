import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class TestPerformance:
    def perform_anova_per_operation(self, times_small, times_medium, times_large):
        """
        Realiza ANOVA para cada operación (carga, layout, creación)
        basado en múltiples mediciones para cada tamaño de red.
        """
        carga_small, layout_small, creacion_small = times_small
        carga_medium, layout_medium, creacion_medium = times_medium
        carga_large, layout_large, creacion_large = times_large

        fvalue_carga, pvalue_carga = stats.f_oneway(carga_small, carga_medium, carga_large)
        print(f"ANOVA - Carga de Archivos: F-value = {fvalue_carga:.4f}, P-value = {pvalue_carga}")

        fvalue_layout, pvalue_layout = stats.f_oneway(layout_small, layout_medium, layout_large)
        print(f"ANOVA - Computación del Layout: F-value = {fvalue_layout:.4f}, P-value = {pvalue_layout}")

        fvalue_creacion, pvalue_creacion = stats.f_oneway(creacion_small, creacion_medium, creacion_large)
        print(f"ANOVA - Creación del Grafo: F-value = {fvalue_creacion:.4f}, P-value = {pvalue_creacion}")

    def plot_bar_chart(self, avg_times_small, avg_times_medium, avg_times_large, title, use_log_scale=True):
        """
        Genera un gráfico de barras para una operación específica con los tiempos promedio.
        
        Parameters:
        -----------
        use_log_scale : bool
            Si es True, usa escala logarítmica en el eje Y
        """
        bar_width = 0.25
        x = np.arange(1)

        plt.figure(figsize=(10, 6))
        
        # Crear las barras
        bars1 = plt.bar(x - bar_width, avg_times_small, bar_width, label='Red Pequeña', color='#2196F3')
        bars2 = plt.bar(x, avg_times_medium, bar_width, label='Red Mediana', color='#FF9800')
        bars3 = plt.bar(x + bar_width, avg_times_large, bar_width, label='Red Grande', color='#4CAF50')

        # Configuración del gráfico
        plt.title(title, pad=20)
        plt.ylabel('Tiempo promedio (s)')
        plt.gca().xaxis.set_visible(False)
        #plt.xticks(x, ['Red pequeña', 'Red Mediana', 'Red Grande'])
        
        if use_log_scale:
            plt.yscale('log')
        
        # Añadir valores sobre las barras
        def autolabel(bars):
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}s',
                        ha='center', va='bottom', rotation=0)
        
        autolabel(bars1)
        autolabel(bars2)
        autolabel(bars3)

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.tight_layout()
        
        plt.show()
        plt.close()

# Ejemplo de uso
test_perf = TestPerformance()

# Usar los mismos datos que proporcionaste
times_small = [
    [0.001846766340004251, 0.001922058400014066, 0.001972135119885934],
    [0.01949484101993221, 0.019841984419981598, 0.02109697126004903],
    [0.00011371089995009243, 0.0001151634199959517, 0.00011934847991142306]
]
times_medium = [
    [0.0009621440199589415, 0.0011955522400421614, 0.0011040996601150255],
    [6.791867219719952, 6.801581821260043, 7.367770386760003],
    [0.0021032216399726167, 0.0021281584200187353, 0.002657461159960803]
]
times_large = [
    [0.07209526836000806, 0.07352743556002679, 0.08196427403974667],
    [5.685829218469345, 6.063539443775528, 6.106179034061138],
    [0.4656753510599447, 0.4096609556400654, 0.4435139581400654]
]

# Calcular promedios
avg_times_small = [np.mean(times) for times in times_small]
avg_times_medium = [np.mean(times) for times in times_medium]
avg_times_large = [np.mean(times) for times in times_large]

# Realizar ANOVA
test_perf.perform_anova_per_operation(times_small, times_medium, times_large)

# Graficar carga de archivos con escala logarítmica
test_perf.plot_bar_chart([avg_times_small[0]], [avg_times_medium[0]], [avg_times_large[0]], 
                        'Rendimiento promedio de Carga de Archivos', use_log_scale=True)
test_perf.plot_bar_chart([avg_times_small[1]], [avg_times_medium[1]], [avg_times_large[1]], 
                        'Rendimiento promedio de Computación de Layout', use_log_scale=True)
test_perf.plot_bar_chart([avg_times_small[2]], [avg_times_medium[2]], [avg_times_large[2]], 
                        'Rendimiento promedio de Creación de grafo', use_log_scale=True)