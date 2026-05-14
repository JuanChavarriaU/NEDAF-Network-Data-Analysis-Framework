import networkx as nx
import logging
import threading
from fa2_modified import ForceAtlas2
import polars as pl
logger = logging.getLogger("nedaf.network_analysis")

_community_cache = {}
_community_cache_lock = threading.Lock()
_COMMUNITY_CACHE_MAX = 32


def _get_communities_cached(G: nx.Graph):
    """
    Get communities with caching to avoid repeated expensive computation.

    Thread-safe. Bounded to _COMMUNITY_CACHE_MAX entries (oldest evicted first).
    """
    graph_hash = (G.number_of_nodes(), G.number_of_edges(), tuple(sorted(G.nodes())[:10]))

    with _community_cache_lock:
        if graph_hash in _community_cache:
            logger.debug("Using cached community detection result")
            return _community_cache[graph_hash]

    logger.debug(f"Computing communities for graph with {G.number_of_nodes()} nodes")
    if G.number_of_nodes() > 5000:
        import igraph as ig
        ig_g = ig.Graph.from_networkx(G)
        weight_attr = 'weight' if 'weight' in ig_g.edge_attributes() else None
        clustering = ig_g.community_multilevel(weights=weight_attr)
        result = [frozenset(ig_g.vs[c]['_nx_name']) for c in clustering]
    else:
        result = nx.algorithms.community.greedy_modularity_communities(G, weight='weight')

    with _community_cache_lock:
        if len(_community_cache) >= _COMMUNITY_CACHE_MAX:
            oldest_key = next(iter(_community_cache))
            del _community_cache[oldest_key]
        _community_cache[graph_hash] = result

    return result


class NetworkAnalysis():
    
    def __init__(self):
        super().__init__()
      
    @staticmethod
    def filter_important_nodes(data: pl.DataFrame, max_nodes: int = 5000) -> pl.DataFrame:
        """
        Filtra el DataFrame para retener únicamente las aristas que conectan los N nodos
        con mayor grado (hubs). Esto permite descubrir patrones en grafos masivos
        al eliminar el ruido de nodos periféricos o menos conectados.
        """
        cols = data.columns
        if len(cols) < 2:
            return data
            
        src_col = cols[0]
        dst_col = cols[1]
        
        # Calcular grados sumando las apariciones como source y target
        src_counts = data.select(pl.col(src_col).alias("node")).group_by("node").agg(pl.len().alias("deg"))
        dst_counts = data.select(pl.col(dst_col).alias("node")).group_by("node").agg(pl.len().alias("deg"))
        
        degree_df = pl.concat([src_counts, dst_counts]).group_by("node").agg(pl.sum("deg"))
        
        # Top N nodos por grado
        top_nodes_df = degree_df.sort("deg", descending=True).head(max_nodes)
        top_nodes = top_nodes_df.select("node").to_series()
        
        # Filtrar edges donde AMBOS nodos están en el top N
        filtered_data = data.filter(
            pl.col(src_col).is_in(top_nodes) & pl.col(dst_col).is_in(top_nodes)
        )
        
        logger.info(f"Filtro aplicado: Reducido de {len(data)} a {len(filtered_data)} aristas usando top {max_nodes} nodos.")
        return filtered_data

    @staticmethod    
    def create_network_graph(data: pl.DataFrame, max_nodes_auto_filter: int = 5000) -> nx.Graph:
        """
        Crea un grafo a partir de un DataFrame de Polars.
        Aplica un filtro para mantener solo el 'núcleo' de la red en caso de grafos inmensos.
    
        Parámetros:
        data: Un DataFrame que contiene los datos de los bordes.
        max_nodes_auto_filter: El límite de nodos principales a retener si la red es masiva.
    
        Devuelve:
        nx.Graph: Un grafo de NetworkX.
        """
        if len(data) > 50000:
            logger.info(f"Dataset masivo detectado ({len(data)} aristas). Extrayendo el núcleo principal.")
            data = NetworkAnalysis.filter_important_nodes(data, max_nodes_auto_filter)
            
        G = nx.Graph()

        num_cols = len(data.columns)

        if num_cols == 2 or num_cols == 3:
            # Soporte para Polars
            if hasattr(data, 'rows'):
                edges = data.rows()
            else:
                edges = data.values.tolist()
                
            if num_cols == 3:
                G.add_weighted_edges_from(edges)
            else:
                G.add_edges_from(edges)
        else:
            raise ValueError("Error: DataFrame should have either 2 or 3 columns.")        
        return G


    def compute_large_layout(self, G: nx.Graph):
        num_nodes = G.number_of_nodes()
        if num_nodes > 50000:
            import igraph as ig
            ig_g = ig.Graph.from_networkx(G)
            # DrL is highly optimized for massive graphs
            layout = ig_g.layout_drl()
            pos = {}
            for i, vertex in enumerate(ig_g.vs):
                nx_node = vertex['_nx_name']
                pos[nx_node] = layout[i]
            return pos
        
        forceAtlas2 = ForceAtlas2(
            outboundAttractionDistribution=True,
            linLogMode=False,
            adjustSizes=False,
            edgeWeightInfluence=1.0,

            jitterTolerance=4.0,
            barnesHutOptimize=True,
            barnesHutTheta=1.0,
            multiThreaded=False,

            scalingRatio=2.0,
            strongGravityMode=False,
            gravity=1.0,

            verbose=False
        )

        return forceAtlas2.forceatlas2_networkx_layout(G, pos=None, iterations=100)


    def compute_medium_layout(self, G: nx.Graph):
        # Usar el algoritmo de Fruchterman-Reingold con igraph para mayor rendimiento
        import igraph as ig
        ig_g = ig.Graph.from_networkx(G)
        
        # 'grid' option significantly speeds up FR in igraph for larger graphs
        use_grid = 'grid' if G.number_of_nodes() > 500 else 'nogrid'
        layout = ig_g.layout_fruchterman_reingold(grid=use_grid)
        
        pos = {}
        for i, vertex in enumerate(ig_g.vs):
            pos[vertex['_nx_name']] = layout[i]
        return pos
    
    def compute_small_layout(self, G: nx.Graph):
        # Usar KK Algo con igraph para mayor rendimiento
        import igraph as ig
        ig_g = ig.Graph.from_networkx(G)
        layout = ig_g.layout_kamada_kawai()
        
        pos = {}
        for i, vertex in enumerate(ig_g.vs):
            pos[vertex['_nx_name']] = layout[i]
        return pos

    def compute_layout(self, G: nx.Graph):
        """
        Orquesta el algoritmo de layout dependiendo del número de nodos:
        < 100: Kamada Kawai
        100 - 2000: Fruchterman-Reingold
        > 2000: ForceAtlas2 (o DrL si > 50000)
        """
        n_nodes = G.number_of_nodes()
        if n_nodes < 100:
            return self.compute_small_layout(G)
        elif n_nodes <= 2000:
            return self.compute_medium_layout(G)
        else:
            return self.compute_large_layout(G)

class networkStatistics(NetworkAnalysis): 

    def __init__(self):
        super().__init__()

    def numberofNodes(G: nx.Graph):
        """Return the number of nodes in the network"""
        return G.number_of_nodes()

    def numberofEdges(G: nx.Graph):
        """Return the number of edges in the network"""
        return G.number_of_edges()

    def maximumDegree(G: nx.Graph):
        """Return the maximum degree of nodes in the network"""
        return max(dict(G.degree).values())

    def minumumDegree(G: nx.Graph):
        """Return the minimum degree of nodes in the network"""
        return min(dict(G.degree).values())

    def averageDegree(G: nx.Graph):
        """Return the average degree of nodes in the network"""
        return sum(dict(G.degree).values()) / len(G)

    def assortativity(G: nx.Graph):
        """Return the assortativity of the network"""
        return nx.assortativity.degree_assortativity_coefficient(G)

    def numberOfTriangles(G: nx.Graph):
        """Return the number of triangles in the network"""
        return sum(nx.triangles(G).values())

    def networkDegree(G: nx.Graph) -> dict:
        """Return the degree of each node in the network"""
        return dict(G.degree)

    def networkDensity(G: nx.Graph) -> float:
        """Return the density of the network"""
        return nx.density(G)


    def networkDiameter(G: nx.Graph) -> int:
        """Return the diameter of the network"""
        return nx.diameter(G)
    
    def networkRadius(G: nx.Graph) -> int:
        """Calcula el radio de la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el radio.

        Devuelve:
        int: El radio del grafo.
        """
        return nx.radius(G)
    
    def networkAverageClustering(G: nx.Graph) -> float:
        """
        Calcula el coeficiente de agrupamiento promedio de la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el coeficiente de agrupamiento promedio.

        Devuelve:
        float: El coeficiente de agrupamiento promedio del grafo.
        """
        return nx.average_clustering(G)
    
    def networkAverageDegreeConectivity(G: nx.Graph) -> dict:
        """
            Calcula la conectividad de grado promedio de la red.

            Parámetros:
            G (nx.Graph): El grafo del cual se calculará la conectividad de grado promedio.

            Devuelve:
            dict: Un diccionario donde las claves son los grados y los valores son la conectividad promedio de ese grado.
        """
        return nx.average_degree_connectivity(G)
    
    def networkAveragePathLength(G: nx.Graph) -> float:
        """
        Calcula la longitud promedio del camino más corto en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la longitud promedio del camino más corto.

        Devuelve:
        float: La longitud promedio del camino más corto del grafo.
        """
        return nx.average_shortest_path_length(G)
    
    def networkDegreeDistribution(G: nx.Graph) -> list:
        """
        Calcula la distribución de grados de la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la distribución de grados.

        Devuelve:
        list: Una lista donde el índice representa el grado y el valor en ese índice representa el número de nodos con ese grado.
        """
        return nx.degree_histogram(G)
    
    def networkClusteringCoefficient(G: nx.Graph) -> float | dict:
        """
        Calcula el coeficiente de agrupamiento de la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el coeficiente de agrupamiento.

        Devuelve:
        float, si escoges el nodo | dict, si node=None
        """
        return nx.clustering(G)
    

class NetworkCommunities():
    def __init__(self):
        super().__init__()
    def networkCommunities(G: nx.Graph) -> list:
        """
            Detecta comunidades en la red utilizando el algoritmo de modularidad codiciosa.

            Parámetros:
            G (nx.Graph): El grafo del cual se detectarán las comunidades.

            Devuelve:
            list: Una lista de comunidades, donde cada comunidad es una lista de nodos.
            """
        return _get_communities_cached(G)
    
    def networkModularity(G: nx.Graph) -> float:
        """
        Calcula la modularidad de la red en base a las comunidades detectadas.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la modularidad.

        Devuelve:
        float: La modularidad del grafo.
        """
        communities = _get_communities_cached(G)
        return nx.algorithms.community.modularity(G, communities, weight='weight')
    
    def NoOfCommunities(G: nx.Graph) -> int:
        """
        Calcula el número de comunidades en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el número de comunidades.

        Devuelve:
        int: El número de comunidades en el grafo.
        """
        return len(nx.algorithms.community.greedy_modularity_communities(G, weight='weight'))
    
    def networkCommunitySize( G: nx.Graph) -> list:
        """
        Calcula el tamaño de cada comunidad en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el tamaño de las comunidades.

        Devuelve:
        list: Una lista con los tamaños de cada comunidad.
        """
        return [len(c) for c in nx.algorithms.community.greedy_modularity_communities(G, weight='weight')]
    
    
    #key nodes
    def networkKeyNodes(G: nx.Graph):
        """
        Identifica los nodos clave en la red que tienen un grado mayor a 10.

        Parámetros:
        G (nx.Graph): El grafo del cual se identificarán los nodos clave.

        Devuelve:
        list: Una lista de nodos clave con un grado mayor a 10.
        """
        return [node for node, degree in G.degree() if degree > 10]
    
    def communityLeaderNodes(G: nx.Graph):
        
        c = nx.algorithms.community.greedy_modularity_communities(G)
        
        # Encontrar los nodos clave (líderes) de cada comunidad
        key_nodes = []
        for community in c:
          # Calcular la centralidad de grado para los nodos en la comunidad
          degree_centrality = nx.degree_centrality(G.subgraph(community))
          # El nodo con la mayor centralidad de grado es el líder
          leader = max(degree_centrality, key=degree_centrality.get)
          key_nodes.append(leader)

        # Imprimir los nodos clave

        return [f"Community: {i+1}: {leader}" for i, leader in enumerate(key_nodes)]
          

    #isolates
    def networkIsolates(G: nx.Graph):
        """
        Identifica los nodos aislados en la red que tienen un grado igual a 0.

        Parámetros:
        G (nx.Graph): El grafo del cual se identificarán los nodos aislados.

        Devuelve:
        list: Una lista de nodos aislados con un grado igual a 0.
        """
        return [n for n, d in G.degree() if d == 0]
    
    #degree centrality
    def networkDegreeCentrality(G: nx.Graph) -> dict:
        """
        Calcula la centralidad de grado para cada nodo en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la centralidad de grado.

        Devuelve:
        dict: Un diccionario donde las claves son los nodos y los valores son sus centralidades de grado.
        """
        return nx.degree_centrality(G)
    
    #betweenness centrality
    def networkBetweennessCentrality(G: nx.Graph) -> dict:
        """
        Calcula la centralidad de intermediación para cada nodo en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la centralidad de intermediación.

        Devuelve:
        dict: Un diccionario donde las claves son los nodos y los valores son sus centralidades de intermediación.
        """
        return nx.betweenness_centrality(G, weight='weight')
    
    #closeness centrality
    def networkClosenessCentrality(G: nx.Graph) -> dict:
        """
        Calcula la centralidad de cercanía para cada nodo en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la centralidad de cercanía.

        Devuelve:
        dict: Un diccionario donde las claves son los nodos y los valores son sus centralidades de cercanía.
        """
        return nx.closeness_centrality(G, distance='weight')
    
    #eigenvector centrality
    def networkEigenvectorCentrality(G: nx.Graph) -> dict:
        """
        Calcula la centralidad de vector propio para cada nodo en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará la centralidad de vector propio.

        Devuelve:
        dict: Un diccionario donde las claves son los nodos y los valores son sus centralidades de vector propio.
        """
        return nx.eigenvector_centrality(G, weight='weight')
    
    #pagerank
    def networkPageRank(G: nx.Graph):
        """
        Calcula el PageRank para cada nodo en la red.

        Parámetros:
        G (nx.Graph): El grafo del cual se calculará el PageRank.

        Devuelve:
        dict: Un diccionario donde las claves son los nodos y los valores son sus PageRank.
        """
        return nx.pagerank(G, weight='weight')
    