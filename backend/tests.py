import pandas as pd
import unittest
from Model.transformationData import TransformationData
from Model.exploreData import exploreData
from Model.NetworkAnalysis import NetworkAnalysis, networkStatistics, NetworkCommunities
import timeit
import matplotlib.pyplot as plt
from scipy.io import mmread
from scipy.sparse import csr_matrix
import statistics
import networkx as nx


"""class TestNetworkAnalysis(unittest.TestCase):

    def test_create_network_graph(self):
        data = pd.DataFrame({
            'source': [1, 2, 3],
            'destination': [2, 3, 1],
            'weight': [4.0, 5.0, 6.0]
        })
        G = NetworkAnalysis.create_network_graph(data)
        self.assertEqual(G.number_of_nodes(), 3)
        self.assertEqual(G.number_of_edges(), 3)
        self.assertEqual(G[1][2]['weight'], 4.0)

    def test_compute_large_layout(self):
        G = nx.karate_club_graph()  # Un grafo de prueba estándar
        na = NetworkAnalysis()
        layout = na.compute_large_layout(G)
        self.assertEqual(len(layout), G.number_of_nodes())

    def test_compute_medium_layout(self):
        G = nx.karate_club_graph()
        na = NetworkAnalysis()
        layout = na.compute_medium_layout(G)
        self.assertEqual(len(layout), G.number_of_nodes())

    def test_compute_small_layout(self):
        G = nx.karate_club_graph()
        na = NetworkAnalysis()
        layout = na.compute_small_layout(G)
        self.assertEqual(len(layout), G.number_of_nodes())



class TestNetworkStatistics(unittest.TestCase):

    def setUp(self):
        self.G = nx.karate_club_graph()

    def test_numberofNodes(self):
        self.assertEqual(networkStatistics.numberofNodes(self.G), 34)

    def test_numberofEdges(self):
        self.assertEqual(networkStatistics.numberofEdges(self.G), 78)

    def test_maximumDegree(self):
        self.assertEqual(networkStatistics.maximumDegree(self.G), 17)

    def test_minumumDegree(self):
        self.assertEqual(networkStatistics.minumumDegree(self.G), 1)

    def test_averageDegree(self):
        self.assertAlmostEqual(round(networkStatistics.averageDegree(self.G), 3), 4.588)

    def test_assortativity(self):
        self.assertAlmostEqual(round(networkStatistics.assortativity(self.G),4), -0.4756)

    def test_numberOfTriangles(self):
        self.assertEqual(networkStatistics.numberOfTriangles(self.G), 135)

    def test_networkDensity(self):
        self.assertAlmostEqual(round(networkStatistics.networkDensity(self.G),3), 0.139)

    def test_networkDiameter(self):
        self.assertEqual(networkStatistics.networkDiameter(self.G), 5)

    def test_networkRadius(self):
        self.assertEqual(networkStatistics.networkRadius(self.G), 3)

    def test_networkAverageClustering(self):
        self.assertAlmostEqual(round(networkStatistics.networkAverageClustering(self.G), 3), 0.571)

    def test_networkAveragePathLength(self):
        self.assertAlmostEqual(round(networkStatistics.networkAveragePathLength(self.G),3), 2.408)

    def test_networkDegreeDistribution(self):
        degree_dist = networkStatistics.networkDegreeDistribution(self.G)
        self.assertEqual(len(degree_dist), 18)  # Tiene 18 grados diferentes

    def test_networkClusteringCoefficient(self):
        clustering_coeff = networkStatistics.networkClusteringCoefficient(self.G)
        self.assertIsInstance(clustering_coeff, dict)

class TestNetworkCommunities(unittest.TestCase):

    def setUp(self):
        self.G = nx.karate_club_graph()

    def test_networkCommunities(self):
        communities = NetworkCommunities.networkCommunities(self.G)
        self.assertGreaterEqual(len(communities), 2)

    def test_networkModularity(self):
        modularity = NetworkCommunities.networkModularity(self.G)
        self.assertGreaterEqual(modularity, 0)

    def test_NoOfCommunities(self):
        no_of_communities = NetworkCommunities.NoOfCommunities(self.G)
        self.assertGreaterEqual(no_of_communities, 2)

    def test_networkCommunitySize(self):
        community_sizes = NetworkCommunities.networkCommunitySize(self.G)
        self.assertTrue(all(size > 0 for size in community_sizes))

    def test_networkKeyNodes(self):
        key_nodes = NetworkCommunities.networkKeyNodes(self.G)
        self.assertTrue(isinstance(key_nodes, list))

    def test_communityLeaderNodes(self):
        leaders = NetworkCommunities.communityLeaderNodes(self.G)
        self.assertTrue(isinstance(leaders, list))

    def test_networkIsolates(self):
        isolates = NetworkCommunities.networkIsolates(self.G)
        self.assertEqual(len(isolates), 0)

    def test_networkDegreeCentrality(self):
        degree_centrality = NetworkCommunities.networkDegreeCentrality(self.G)
        self.assertIsInstance(degree_centrality, dict)

    def test_networkBetweennessCentrality(self):
        betweenness_centrality = NetworkCommunities.networkBetweennessCentrality(self.G)
        self.assertIsInstance(betweenness_centrality, dict)

    def test_networkClosenessCentrality(self):
        closeness_centrality = NetworkCommunities.networkClosenessCentrality(self.G)
        self.assertIsInstance(closeness_centrality, dict)

    def test_networkEigenvectorCentrality(self):
        eigenvector_centrality = NetworkCommunities.networkEigenvectorCentrality(self.G)
        self.assertIsInstance(eigenvector_centrality, dict)

    def test_networkPageRank(self):
        pagerank = NetworkCommunities.networkPageRank(self.G)
        self.assertIsInstance(pagerank, dict)

if __name__ == '__main__':
        unittest.main()
        print(unittest.result.TestResult.addSuccess)"""
    
"""data = {
            'source': [1, 2, 3, 4],
            'destination': [2, 3, 4, 1],
            'weight': [10, 20, 30, 40]
        }
df = pd.DataFrame(data)
        
        # Crear una instancia de TransformationData
transformation_data = TransformationData(df)
        
        # Llamar al método normalize_data
transformation_data.normalize_data()
print(transformation_data.dataframe)"""

"""
class TestTransformationData(unittest.TestCase):

    def test_normalize_data(self):
        # Datos de ejemplo
        data = {
            'source': [1, 2, 3, 4],
            'destination': [2, 3, 4, 1],
            'weight': [10, 20, 30, 40]
        }
        df = pd.DataFrame(data)
        
        # Crear una instancia de TransformationData
        transformation_data = TransformationData(df)
        
        # Llamar al método normalize_data
        transformation_data.normalize_data()
        print(transformation_data.dataframe)
        # Verificar si los valores normalizados están dentro del rango esperado
        normalized_weights = transformation_data.dataframe['normalized_weight']
        
        self.assertGreaterEqual(normalized_weights.min(), 0, "Los valores normalizados no están en el rango esperado (min < 0)")
        self.assertLessEqual(normalized_weights.max(), 1, "Los valores normalizados no están en el rango esperado (max > 1)")



    def test_cut_missing_values(self):
        data = {
            'source': [1, 2, 3, 4],
            'destination': [2,None, 4, 1],
            'weight': [10, 20, 30, 40]
        }
        df = pd.DataFrame(data)

        transformation_data = TransformationData(df)
        
        transformation_data.cut_missing_values()

        result = transformation_data.get_data()

        expected = df.dropna()

        pd.testing.assert_frame_equal(result, expected)  

        
    if __name__ == '__main__':
        unittest.main()
"""
  

"""class TestExploreData(unittest.TestCase):
    
    def setUp(self):
        
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })

        # Create an instance of ExploreData
        self.explore_data = exploreData()
        self.explore_data.set_data(self.data)   
    
    def test_get_unique_values(self):
        # Create a sample DataFrame
       
        # Test the get_unique_values method
        unique_values = self.explore_data.get_unique_values('A')
        self.assertEqual(unique_values, [1, 2, 3, 4, 5])
        

    def test_get_summary_statistics(self):
        result = self.explore_data.get_summary_statistics('A')
        expected = self.data['A'].describe(include='all')
        pd.testing.assert_frame_equal(result, expected)

    def test_calculate_mean(self):
        result = self.explore_data.calculate_mean('A')
        expected = self.data['A'].mean()
        self.assertEqual(result, expected)

    def test_calculate_median(self):
        result = self.explore_data.calculate_median('C')
        expected = self.data['C'].median()
        self.assertEqual(result, expected)

    def test_calculate_variance(self):
        result = self.explore_data.calculate_variance('C')
        expected = self.data['C'].var()
        self.assertEqual(result, expected)    

    def test_calculate_covariance(self):
        result = self.explore_data.calculate_covariance('C')
        expected = self.data['C'].cov()
        self.assertEqual(result, expected)   

    def test_calculate_correlation(self):
        result = self.explore_data.calculate_correlation('C')
        expected = self.data['C'].corr(self.data.drop('C', axis=1))
        pd.testing.assert_frame_equal(result, expected)
    
    def test_calculate_distribution(self):
        result = self.explore_data.calculate_distribution()
        expected = {col: self.data[col].value_counts() for col in self.data.select_dtypes(include=['object', 'category'])}
        self.assertEqual(result, expected)

    def test_get_unique_values(self):
        result = self.explore_data.get_unique_values('B')
        expected = self.data['B'].nunique()
        self.assertEqual(result, expected)    

    def test_get_missing_values(self):
        result = self.explore_data.get_missing_values('B')
        expected = self.data['B'].isnull().sum()
        self.assertEqual(result, expected)    

    def test_calculate_standard_deviation(self):
        result = self.explore_data.calculate_standard_deviation('C')
        expected = self.data['C'].std()
        self.assertEqual(result, expected)    

    def test_calculate_min_max(self):
        result = self.explore_data.calculate_min_max('C')
        expected = {'min': self.data['C'].min(), 'max': self.data['C'].max()}
        self.assertEqual(result, expected)    
"""

import numpy as np
from scipy.stats import f_oneway, kruskal 
class TestPerformance():

    def __init__(self) -> None:
        self.na = NetworkAnalysis()

    def load_data(self, format):
        
        if format == 'mtx':
            matrixData = mmread('/home/vscode/soc-karate.mtx')
            rows, cols = matrixData.nonzero()
            if isinstance(matrixData, csr_matrix):
                weights = matrixData.data
                df = pd.DataFrame({'source': rows, 'destination': cols, 'weight': weights})
            else:
                df = pd.DataFrame({'source': rows, 'destination': cols}) 
        elif format == 'edges':
            df = pd.read_csv('/home/vscode/bio-CE-LC.edges', sep=' ', header=None, names=["source", "destination", "weight"] or ["source", "destination"])
        else:
            df = pd.read_csv('/home/vscode/od_cvegeo_09_01_2020_12_24.csv')

        return df
    
    def test_create_network_graph(self, df): 
        times = [{}]
        for i in range(1, 51, 1): #1500 iteraciones algoritmo KK 34 nodos
          times[0][i] = (timeit.timeit(lambda: NetworkAnalysis.create_network_graph(df), number=1))
        return times
    
    def test_compute_small_layout(self, G: nx.Graph): 
        times = [{}]
        for i in range(1, 51, 1): 
          times[0][i] = (timeit.timeit(lambda: NetworkAnalysis.compute_small_layout(G), number=1))
        return times

    def test_compute_medium_layout(self, G: nx.Graph): 
        times = [{}]
        for i in range(1, 51, 1): 
          times[0][i] = (timeit.timeit(lambda: NetworkAnalysis.compute_medium_layout(G), number=1))
        return times   

    def test_compute_large_layout(self, G: nx.Graph): 
        times = [{}]
        for i in range(1, 50, 1): 
            times[0][i] = (timeit.timeit(lambda: NetworkAnalysis.compute_large_layout(G), number=1))
        return times   
      
    def test_load_data(self, load_data, format:str):
        times = [{}]
        for i in range(1, 51, 1): 
          times[0][i] = (timeit.timeit(lambda: load_data(format), number=1))
        return times    

    def plot_times(self, times: dict, legend, title, upperLimit):
        fig, ax = plt.subplots()
        x_values = list(times[0].keys())
        y_values = list(times[0].values())
        ax.plot(times[0].keys(), times[0].values(), label=legend)  
        
        z = np.polyfit(x=x_values, y=y_values,deg=1)
        p = np.poly1d(z)
        ax.plot(x_values, p(x_values), "--", label=f"Tendencia (m={z[0]:.4f})")

        plt.grid()
        plt.title(title)
        plt.legend([legend, 'Linea de tendencia'])
        plt.xlabel('Iteraciones')
        plt.ylabel('Tiempo (s)')
        #plt.ylim(0, upperLimit)
        plt.show()  

    def plot_bar_times(self, times: dict, legend, title, upperLimit):
        fig, ax = plt.subplots()
        x_values = list(times[0].keys())
        y_values = list(times[0].values())

        # Cambiar de plot a bar para gráfico de barras
        ax.bar(x_values, y_values, label=legend)

        plt.grid()
        plt.title(title)
        plt.legend([legend])
        plt.xlabel('Iteraciones')
        plt.ylabel('Tiempo (s)')
        #plt.ylim(0, upperLimit)  # Esto se puede usar si necesitas limitar el rango superior
        plt.show()    

    def plot_grouped_bar_times(self, times_list: list[list], legends: list, title, upperLimit=None):
        fig, ax = plt.subplots()
        x_values = list(times_list[0][0].keys())  # Las iteraciones (eje X)

        bar_width = 0.2  # Ancho de las barras
        index = np.arange(len(x_values))  # Posiciones de las barras en el eje X

        for i, times in enumerate(times_list):
            y_values = list(times[0].values())
            ax.bar(index + i * bar_width, y_values, bar_width, label=legends[i])

        # Ajustes adicionales
        plt.grid()
        plt.title(title)
        plt.xlabel('Iteraciones')
        plt.ylabel('Tiempo (s)')
        plt.xticks(index + bar_width, x_values)  # Posición de las etiquetas del eje X
        plt.legend()
        plt.show()

    def plot_average_times(self, average_times: list[float], legends: list, title):
        """Genera una gráfica de barras para los tiempos promedio."""
        fig, ax = plt.subplots()

        # Asignar las operaciones al eje X y los tiempos promedio al eje Y
        x_values = np.arange(len(legends))
        ax.bar(x_values, average_times, tick_label=legends)

        # Etiquetas y título
        plt.grid()
        plt.title(title)
        plt.xlabel('Operaciones')
        plt.ylabel('Tiempo promedio (s)')
        plt.show()
    
    def calculate_average_times(self, times_list: list[dict]) -> list[float]:
        """Calcula el promedio de los tiempos de ejecución."""
        average_times = []
        for times in times_list:
            # Extraer los valores de tiempo y calcular el promedio
            y_values = list(times[0].values())
            avg_time = sum(y_values) / len(y_values)
            average_times.append(avg_time)
        return average_times
    

    def plot_average_times_subplots(self, avg_times_small: list[float], avg_times_medium: list[float], avg_times_large: list[float], legends: list, title):
            """Genera un subplot con las tres gráficas de barras para redes pequeñas, medianas y grandes."""
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))  # 1 fila, 3 columnas

            # Eje X con nombres de las operaciones
            x_values = np.arange(len(legends))

            # Gráfica para redes pequeñas
            axs[0].bar(x_values, avg_times_small, tick_label=legends)
            axs[0].set_title("Red Pequeña")
            axs[0].set_xlabel('Operaciones')
            axs[0].set_ylabel('Tiempo promedio (s)')

            # Gráfica para redes medianas
            axs[1].bar(x_values, avg_times_medium, tick_label=legends)
            axs[1].set_title("Red Mediana")
            axs[1].set_xlabel('Operaciones')

            # Gráfica para redes grandes
            axs[2].bar(x_values, avg_times_large, tick_label=legends)
            axs[2].set_title("Red Grande")
            axs[2].set_xlabel('Operaciones')

            # Ajustar espaciado
            plt.suptitle(title)
            plt.tight_layout()
            plt.show()

    def perform_anova(self, avg_times_small, avg_times_medium, avg_times_large):
            """Realiza un ANOVA de una vía para comparar los tiempos promedio entre las diferentes redes."""
            # ANOVA de una vía para cada operación (crear grafo, layout, cargar datos)
            fvalue, pvalue = f_oneway(avg_times_small, avg_times_medium, avg_times_large)
            # Mostrar los resultados
            print(f"F-value: {fvalue}")
            print(f"P-value: {pvalue}")

            if pvalue < 0.05:
                print("Hay diferencias significativas entre los grupos (p < 0.05)")
            else:
                print("No hay diferencias significativas entre los grupos (p >= 0.05)")
    def perform_kruskal(self,avg_times_small, avg_times_medium, avg_times_large ):
        fvalue, pvalue = kruskal(avg_times_small, avg_times_medium, avg_times_large)
                
        print(f"F-value: {fvalue}")
        print(f"P-value: {pvalue}")

        if pvalue < 0.05:
            print("Hay diferencias significativas entre los grupos (p < 0.05)")
        else:
            print("No hay diferencias significativas entre los grupos (p >= 0.05)")
    
    def perform_anova_per_operation(self, times_op1_small, times_op2_small, times_op3_small, times_op1_medium, times_op2_medium, times_op3_medium, times_op1_large, times_op2_large, times_op3_large):
        """Realiza ANOVA para cada operación (carga, layout, creación)."""
        # Extraer los promedios de cada operación
       
        # ANOVA para Carga
        fvalue_carga, pvalue_carga = f_oneway(times_op1_small, times_op2_small, times_op3_small)
        print(f"ANOVA - Carga de Archivos: F-value = {fvalue_carga}, P-value = {pvalue_carga}")

        # ANOVA para Layout
        fvalue_layout, pvalue_layout = f_oneway(times_op1_medium, times_op2_medium, times_op3_medium)
        print(f"ANOVA - Computación del Layout: F-value = {fvalue_layout}, P-value = {pvalue_layout}")

        # ANOVA para Creación de Grafo
        fvalue_creacion, pvalue_creacion = f_oneway(times_op1_large, times_op2_large, times_op3_large)
        print(f"ANOVA - Creación del Grafo: F-value = {fvalue_creacion}, P-value = {pvalue_creacion}")

        # Interpretar los resultados
        if pvalue_carga < 0.05:
            print("Diferencias significativas en los tiempos de carga entre redes.")
        if pvalue_layout < 0.05:
            print("Diferencias significativas en los tiempos de layout entre redes.")
        if pvalue_creacion < 0.05:
            print("Diferencias significativas en los tiempos de creación entre redes.")
        else:
            print("No hay diferencias significativas en alguna de las operaciones.")


# Crear la instancia de TestPerformance
test_perf = TestPerformance() 

df_small = test_perf.load_data("mtx")  
G_small = NetworkAnalysis.create_network_graph(df_small) 

df_medium = test_perf.load_data("edges")  
G_medium = NetworkAnalysis.create_network_graph(df_medium) 

df_large = test_perf.load_data("csv")  
G_large = NetworkAnalysis.create_network_graph(df_large) 

# Ahora, calculamos los tiempos promedios
times_op1_small = test_perf.test_create_network_graph(df_small)
times_op2_small = test_perf.test_compute_small_layout(G_small)
times_op3_small = test_perf.test_load_data(test_perf.load_data, 'mtx')

times_op1_medium = test_perf.test_create_network_graph(df_medium)
times_op2_medium = test_perf.test_compute_medium_layout(G_medium)
times_op3_medium = test_perf.test_load_data(test_perf.load_data, 'edges')

times_op1_large = test_perf.test_create_network_graph(df_large)
times_op2_large = test_perf.test_compute_large_layout(G_large)
times_op3_large = test_perf.test_load_data(test_perf.load_data, 'csv')



# Calcular tiempos promedio
avg_times_small = test_perf.calculate_average_times([times_op1_small, times_op2_small, times_op3_small])
avg_times_medium = test_perf.calculate_average_times([times_op1_medium, times_op2_medium, times_op3_medium])
avg_times_large = test_perf.calculate_average_times([times_op1_large, times_op2_large, times_op3_large])

print(f"avg creation time for small: {avg_times_small[0]}, avg compute layout time for small: {avg_times_small[1]}, avg load time for small: {avg_times_small[2]}")
print(f"avg creation time for medium: {avg_times_medium[0]}, avg compute layout time for medium: {avg_times_medium[1]}, avg load time for medium: {avg_times_medium[2]}")
print(f"avg creation time for large: {avg_times_large[0]}, avg compute layout time for large: {avg_times_large[1]}, avg load time for large: {avg_times_large[2]}")
# Graficar los tiempos promedio en un subplot
"""test_perf.plot_average_times_subplots(avg_times_small, avg_times_medium, avg_times_large, 
                                 ['Crear grafo', 'Layout', 'Cargar datos'],
                                 title="Comparación de tiempo promedio en redes pequeñas, medianas y grandes")
"""
# Realizar el ANOVA y calcular el p-value
#test_perf.perform_anova_per_operation(times_op1_small, times_op2_small, times_op3_small, times_op1_medium, times_op2_medium, times_op3_medium, times_op1_large, times_op2_large, times_op3_large)
#test_perf.perform_anova(avg_times_small, avg_times_medium, avg_times_large)
#test_perf.perform_kruskal(avg_times_small, avg_times_medium, avg_times_large)






"""#Small networks


times = test_perf.test_create_network_graph(df)
media= statistics.mean(times[0].values())
g = NetworkAnalysis.create_network_graph(df)
times2 = test_perf.test_compute_small_layout(G=g)
media2 = statistics.mean(times2[0].values())
times3 = test_perf.test_load_data(test_perf.load_data, 'mtx')
media3 = statistics.mean(times3[0].values())
test_perf.plot_bar_times(times, f'Tiempo promedio: {media:.4f}s', "Rendimiento de la creacion de una red pequeña (34 nodos)", 1) 
test_perf.plot_bar_times(times2, f'Tiempo promedio: {media2:.4f}s', "Rendimiento de la computación de layout de una red pequeña (34 nodos)", 2)
test_perf.plot_bar_times(times3, f'Tiempo promedio: {media3:.4f}s', "Rendimiento de la carga de una red pequeña (34 nodos)", 1)
"""

"""
test_perf = TestPerformance()
#Medium networks 
df2 = test_perf.load_data("edges")
G = NetworkAnalysis.create_network_graph(df2)
times = test_perf.test_create_network_graph(df2)
media= statistics.mean(times[0].values())
times2 = test_perf.test_compute_medium_layout(G)
media2 = statistics.mean(times2[0].values())
times3 = test_perf.test_load_data(test_perf.load_data, 'edges')
media3 = statistics.mean(times3[0].values())
test_perf.plot_times(times, f'Tiempo promedio de creacion de grafo: {media:.4f}s', "Rendimiento de la creacion de una red mediana (1,400 nodos)",1) 
test_perf.plot_times(times2, f'Tiempo promedio de computacion de layout: {media2:.4f}s', "Rendimiento de la computación de layout de una red mediana (1,400 nodos)", 3)
test_perf.plot_times(times3, f'Tiempo promedio de carga de datos: {media3:.4f}s', "Rendimiento de la carga de datos de una red mediana (1,400 nodos)", 3)

 """




"""test_perf = TestPerformance()  
    #large networks
df3 = test_perf.load_data("csv")
G = NetworkAnalysis.create_network_graph(df3)
print(G)
times = test_perf.test_create_network_graph(df3)
media= statistics.mean(times[0].values())

times2 = test_perf.test_compute_large_layout(G)
media2 = statistics.mean(times2[0].values())

times3 = test_perf.test_load_data(test_perf.load_data, 'csv')
media3 = statistics.mean(times3[0].values())
test_perf.plot_times(times, f'Tiempo promedio de creacion de grafo: {media:.4f}s', "Rendimiento de la creacion de una red grande (5,749 nodos)",1) 
test_perf.plot_times(times2, f'Tiempo promedio de computacion de layout: {media2:.4f}s', "Rendimiento de la computación de layout de una red grande (5,749 nodos)", 3)
test_perf.plot_times(times3, f'Tiempo promedio de carga de datos: {media3:.4f}s', "Rendimiento de la carga de datos de una red grande (5,749 nodos)", 3)
"""