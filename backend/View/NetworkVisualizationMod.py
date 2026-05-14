from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QTextEdit, QProgressBar
from PyQt6.QtCore import (
  pyqtSignal,
  QThread
)
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen
import networkx as nx
import pyqtgraph as pg
import numpy as np
import time
<<<<<<<< HEAD:View/network_visualization.py
from ViewModel.data_manager import DataManager
from ViewModel import NetworkAnalysis as na 
========
from Model.DataManager import DataManager
from Model import NetworkAnalysis as na 
>>>>>>>> 5880c45 (Organizing Architechture in Model-View. Files were moved and place into their corresponding folders. and the refactoring was made.):View/NetworkVisualizationMod.py


class NetworkVisualizationMod(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        
        self.NetworkAnalysis = na.NetworkAnalysis()
        self.NetworkCommunities = na.NetworkCommunities()
        self.operation_to_function_map = {
            "Number of Nodes":na.networkStatistics.numberofNodes,
            "Number of Edges": na.networkStatistics.numberofEdges,
            "Maximum Degree": na.networkStatistics.maximumDegree,
            "Minimum Degree": na.networkStatistics.minumumDegree,
            "Average Degree": na.networkStatistics.averageDegree,
            "Assortativity": na.networkStatistics.assortativity,
            "Number of triangles": na.networkStatistics.numberOfTriangles,
            "Network Degree" : na.networkStatistics.networkDegree,
            "Network Density": na.networkStatistics.networkDensity,
            "Network Diameter": na.networkStatistics.networkDiameter, 
            "Network Radius": na.networkStatistics.networkRadius,
            "Network Average Clustering": na.networkStatistics.networkAverageClustering,
            "Network Average Degree Conectivity": na.networkStatistics.networkAverageDegreeConectivity,
            "Network Average Path Length": na.networkStatistics.networkAveragePathLength,
            "Network Degree Distribution": na.networkStatistics.networkDegreeDistribution,
            "Network Clustering Coefficient": na.networkStatistics.networkClusteringCoefficient,
            "Network Communities": na.NetworkCommunities.networkCommunities,
            "Network Modularity": na.NetworkCommunities.networkModularity,
            "Number of Communities": na.NetworkCommunities.NoOfCommunities,
            "Network Community Size": na.NetworkCommunities.networkCommunitySize,
            "Network Key Nodes": na.NetworkCommunities.networkKeyNodes,
            "Community Leader Nodes": na.NetworkCommunities.communityLeaderNodes,
            "Network Isolates": na.NetworkCommunities.networkIsolates, 
            "Network Degree Centrality": na.NetworkCommunities.networkDegreeCentrality,
            "Network Betweenness Centrality": na.NetworkCommunities.networkBetweennessCentrality,
            "Network Closeness Centrality": na.NetworkCommunities.networkClosenessCentrality,
            "Network Eigenvector Centrality": na.NetworkCommunities.networkEigenvectorCentrality,
            "Network PageRank": na.NetworkCommunities.networkPageRank
            
          }  # Populate with actual functions
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()  # canvas 

        # layout para la grafica
        pg.setConfigOptions(antialias=True)
        self.figure = pg.PlotWidget()
        self.figure.setBackground('w')
        self.figure.adjustSize()
        
      
        layout.addWidget(self.figure)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)


        self.is_fullscreen = False
        # layout para el dropdown
        self.GraphBasicMetricsDropDown = QComboBox()
        self.GraphBasicMetricsDropDown.setStyleSheet("QComboBox {combobox-popup: 0;}")
        self.GraphBasicMetricsDropDown.setMaxVisibleItems(5)
        self.GraphBasicMetricsDropDown.setPlaceholderText("Metricas del grafo")
        
        self.GraphBasicMetricsDropDown.activated.connect(self.on_operation_changed)

        layout.addWidget(self.GraphBasicMetricsDropDown)

        # layout para el label
        self.stats_text = QTextEdit(self)
        self.stats_text.setReadOnly(True)
        self.stats_text.verticalScrollBar()
        self.stats_text.setGeometry(100,50,100,50)
        layout.addWidget(self.stats_text)

        # layout para el boton
        button = QPushButton("Visualizar Red")
        layout.addWidget(button)

      
        button.clicked.connect(self.visualize_networks)
              
      
        self.setLayout(layout)
   
    def on_visualization_finished(self):
        print("Computation complete.")
            
    def visualize_networks(self):
        print("Button Pressed")
        self.progress_bar.setVisible(True)
        self.worker = Worker(self.NetworkAnalysis, self.data_manager.get_data())
        self.worker.update_progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_visualization_finished)
        self.worker.positions_ready.connect(self.set_graph)
        self.worker.positions_ready.connect(self.start_plotting_thread)
        self.worker.start()

    def start_plotting_thread(self, G: nx.Graph, positions):
        self.plot_worker = PlotWorker(G, positions)
        self.plot_worker.update_progress.connect(self.progress_bar.setValue)
        self.plot_worker.plot_ready.connect(self.on_plotting_finished)
        self.plot_worker.start()

    def on_plotting_finished(self, graph_item):
        self.figure.clear()
        self.figure.addItem(graph_item)
        print("Plotting complete.")
        self.progress_bar.setVisible(False)

    def set_graph(self, G: nx.Graph, _):
        self.Graph = G    

    def on_data_loaded(self) -> None:
        """Manejador para la señal de datos cargados."""
        self.GraphBasicMetricsDropDown.clear()  # Limpiar el dropdown
        self.GraphBasicMetricsDropDown.addItems([
                                                 "Number of Nodes",
                                                 "Number of Edges",
                                                 "Maximum Degree",
                                                 "Minimum Degree",
                                                 "Average Degree",
                                                 "Assortativity",
                                                 "Number of triangles",
                                                 "Network Degree",
                                                 "Network Density",
                                                 "Network Diameter", 
                                                 "Network Radius",
                                                 "Network Average Clustering",
                                                 "Network Average Degree Conectivity",
                                                 "Network Average Path Length",
                                                 "Network Degree Distribution",
                                                 "Network Clustering Coefficient",
                                                 "Network Communities",
                                                 "Network Modularity",
                                                 "Number of Communities",
                                                 "Network Community Size",
                                                 "Network Key Nodes",
                                                 "Community Leader Nodes",
                                                 "Network Isolates", 
                                                 "Network Degree Centrality",
                                                 "Network Betweenness Centrality",
                                                 "Network Closeness Centrality",
                                                 "Network Eigenvector Centrality",
                                                 "Network PageRank"])

    def on_operation_changed(self, G: nx.Graph):
        """Manejador para el cambio de operación seleccionado en el `graphbasicmetrics_dropdown`."""
        try:
            selected_operation = self.GraphBasicMetricsDropDown.currentText()
            print(selected_operation)
            if selected_operation in self.operation_to_function_map:

                functionSelected = self.operation_to_function_map[selected_operation]
                
                result = functionSelected(self.Graph)
                print(f"{selected_operation}: {result}")
                self.stats_text.setVisible(True)
                self.stats_text.setPlainText(str(result))
                
                #ocultar el qtextEdit para mejor vis
            else:
                QMessageBox.critical(self, "Error", f"Operación no soportada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando la operación {str(e)}")

class Worker(QThread):
    positions_ready = pyqtSignal(object, object) #signature
    update_progress = pyqtSignal(int)

    def __init__(self, network_analysis, data):
        super().__init__()
        self.network_analysis = network_analysis
        self.data = data

    def run(self):
        self.update_progress.emit(10)
        self.G = self.network_analysis.create_network_graph(self.data)
        num_nodes = self.G.number_of_nodes()

        if num_nodes > 5000:
            positions = self.network_analysis.compute_large_layout(self.G)
        elif num_nodes >= 100:
            positions = self.network_analysis.compute_medium_layout(self.G)
        else:
            positions = self.network_analysis.compute_small_layout(self.G)
        self.update_progress.emit(50)
        self.positions_ready.emit(self.G, positions)
   

class PlotWorker(QThread):
    plot_ready = pyqtSignal(object)
    update_progress = pyqtSignal(int)

    def __init__(self, G: nx.Graph, positions):
        super().__init__()
        self.G = G
        self.positions = positions

    def run(self):
        self.update_progress.emit(60) 
        nodes = list(self.G.nodes())
        edges = list(self.G.edges())
        weights = nx.get_edge_attributes(self.G, 'w')
        if not weights:
            weights = {(u, v): 1 for u, v in edges}


        # Calculate node degrees or weights
        degrees = dict(self.G.degree(nodes))  # This returns a dictionary of node degrees

        # Normalize the sizes based on degree
        min_size = 10
        max_size = 45

        min_degree = min(degrees.values())
        max_degree = max(degrees.values())
        #linear interpolation formula
        node_sizes = [
            min_size + (max_size - min_size) * (degrees[node] - min_degree) / (max_degree - min_degree) if max_degree != min_degree else max_size
            for node in nodes
        ]


        node_positions = np.array([self.positions[node] for node in nodes])
        adj = np.array([[nodes.index(source), nodes.index(target)] for source, target in edges])

        graph_item = pg.GraphItem(
            pos=node_positions,
            adj=adj,
            size=node_sizes,
            symbol='o',
            pxMode=True,
            brush=pg.mkBrush('Purple'),
            hoverable=True,
            useCache=False,
            pen=pg.mkPen(color='black', width=1)
        )
        self.update_progress.emit(100)
        self.plot_ready.emit(graph_item)     