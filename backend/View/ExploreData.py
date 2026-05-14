from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, 
                            QLabel, QMessageBox, QStackedLayout)
from PyQt6 import QtWidgets

from Model.data_manager import DataManager
from Model.explore_logic import exploreData

import pandas as pd
import numpy as np
import pyqtgraph as pg
class ExploreData(QWidget):
    
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.i = 0
        self.data_manager = data_manager
        self.data_manager.data_loaded.connect(self.on_data_loaded) # no se habilitan las tablas una vez que los datos estan cargados 
        self.operation_to_function_map = {
            "Resumen estadístico": self.create_summary_tab,
            "Promedio": self.create_mean_tab,
            "Mediana": self.create_median_tab,
            "Varianza": self.create_variance_tab,
            "Covarianza": self.create_covariance_tab,
            "Correlación": self.create_correlation_tab,
            "Distribución": self.create_distribution_tab,
            "Desviación estándar": self.create_standard_deviation_tab,
            "Min y Max": self.create_min_max_tab,
            "Cantidad de valores únicos": self.create_unique_values_tab,
            "Cantidad de valores faltantes": self.create_missing_values_tab
        } 
        
        self.initUI()

    def initUI(self):
      """ Inicializa la interfaz de usuario."""
      self.columns_dropdown = QComboBox()
      self.operation_dropdown = QComboBox()
      self.stacked_Layout = QStackedLayout()
      self.figure = pg.PlotWidget()
      self.figure.setBackground('w')
      self.figure.hide()
      
      self.columns_dropdown.setPlaceholderText("Columnas")
      self.operation_dropdown.setPlaceholderText("Operaciones estadísticas")

      self.columns_dropdown.activated.connect(self.on_column_changed)
      
      self.operation_dropdown.activated.connect(self.on_operation_changed)

      self.layout = QVBoxLayout()
      self.layout.addWidget(self.columns_dropdown)
      self.layout.addWidget(self.operation_dropdown)
      self.layout.addLayout(self.stacked_Layout)
      self.layout.addWidget(self.figure)

      self.setLayout(self.layout)
    
    def create_tab(self):
        self.i += 1
        print(f"Llamada a create_tab #{self.i}") 
        """Crea pestaña."""
        tab = QWidget()
        layout = QVBoxLayout()
        table = QTableWidget()
        layout.addWidget(table)
        tab.setLayout(layout)
        self.stacked_Layout.addWidget(tab)
        
        print("Final de llamada #", self.i)
        return tab, table 

    def create_summary_tab(self, selected_column: str):
        """Crea la pestaña de resumen."""
        print("OYE PERO ESTOY EN CREATE SUMMARY TAB")
        self.summary_tab , self.summary_table = self.create_tab()
        self.fill_table_with_summary(self.summary_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.summary_tab)  

    def create_distribution_tab(self, selected_column: str):
        """Crea la pestaña de distribución."""
        self.distribution_tab, self.distribution_table = self.create_tab()
        self.fill_table_with_distribution(self.distribution_table, self.get_data(), selected_column)        
        #self.stacked_Layout.addWidget(self.distribution_tab)
        self.add_and_show_widget(self.distribution_tab)  

    def create_correlation_tab(self, selected_column: str):
        """Crea la pestaña de correlación."""
        self.correlation_tab, self.correlation_table = self.create_tab()
        self.fill_table_with_correlation(self.correlation_table, self.get_data(), selected_column)
        #self.stacked_Layout.addWidget(self.correlation_tab)
        self.add_and_show_widget(self.correlation_tab)  
    
    def create_mean_tab(self, selected_column: str):
        """Crea la pestaña de promedio."""
        self.mean_tab, self.mean_table = self.create_tab()
        print(f"Creo la pestaña y llamo a fill table mean y añado el widget al stack ")
        self.fill_table_with_mean(self.mean_table, self.get_data(), selected_column)
        #self.stacked_Layout.addWidget(self.mean_tab)
        self.add_and_show_widget(self.mean_tab)  
    
    def create_median_tab(self, selected_column: str):
        """Crea la pestaña de mediana."""
        self.median_tab, self.median_table = self.create_tab()
        self.fill_table_with_median(self.median_table, self.get_data(), selected_column)
        #self.stacked_Layout.addWidget(self.median_tab)
        self.add_and_show_widget(self.median_tab)  
    
    def create_variance_tab(self, selected_column: str):
        """Crea la pestaña de varianza."""
        self.variance_tab, self.variance_table = self.create_tab()
        self.fill_table_with_variance(self.variance_table, self.get_data(), selected_column)
        #self.stacked_Layout.addWidget(self.variance_tab)
        self.add_and_show_widget(self.variance_tab)  
    
    def create_covariance_tab(self, selected_column: str):
        """Crea la pestaña de covarianza."""
        self.covariance_tab, self.covariance_table = self.create_tab()
        self.fill_table_with_covariance(self.covariance_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.covariance_tab)
    
    def create_standard_deviation_tab(self, selected_column: str):
        """Crea la pestaña de desviación estándar."""
        self.standard_deviation_tab, self.standard_deviation_table = self.create_tab()
        self.fill_table_with_standard_deviation(self.standard_deviation_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.standard_deviation_tab)
        
    def create_min_max_tab(self, selected_column: str):
        """Crea la pestaña de min y max."""
        self.min_max_tab, self.min_max_table = self.create_tab()
        self.fill_table_with_min_max(self.min_max_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.min_max_tab)
        
    def create_unique_values_tab(self, selected_column: str):
        """Crea la pestaña de valores únicos."""
        self.unique_values_tab, self.unique_values_table = self.create_tab()
        self.fill_table_with_unique_values(self.unique_values_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.unique_values_tab)
        
    def create_missing_values_tab(self, selected_column: str):
        """Crea la pestaña de valores faltantes."""
        self.missing_values_tab, self.missing_values_table = self.create_tab()
        self.fill_table_with_missing_values(self.missing_values_table, self.get_data(), selected_column)
        self.add_and_show_widget(self.missing_values_tab)

    def on_operation_changed(self, index: int):
        """Manejador para el cambio de operación seleccionado en el `operation_dropdown`.
           Establece el índice actual del `QStackedWidget` al índice seleccionado en `operation_dropdown
        """
        self.figure.hide()
        self.stacked_Layout.setCurrentIndex(index)
        try:  
            selected_column = self.columns_dropdown.currentText()
            selected_operation = self.operation_dropdown.currentText()
           
            if selected_operation in self.operation_to_function_map:
                
                self.operation_to_function_map[selected_operation](selected_column)
            else:
                QMessageBox.critical(self, "Error", f"Operación no soportada") 
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando la operación {str(e)}") 
            
    def get_numeric_columns(self) -> list[str]:
        """Devuelve las columnas numéricas del DataFrame."""
        return self.data_manager.get_data().select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    def add_and_show_widget(self, widget: QWidget):
        self.stacked_Layout.addWidget(widget)
        self.stacked_Layout.setCurrentIndex(self.stacked_Layout.count() - 1)
    
    def on_column_changed(self, index: int) -> None:
        """Manejador para el cambio de columna seleccionada en el `columns_dropdown`"""	
        selected_column = self.columns_dropdown.currentText()
        print("(OnColumnChanged) Selected Column: ", selected_column)
        self.figure.clear()
        self.figure.hide()
        data = self.get_data().data
        numeric_columns = data.select_dtypes(include=np.number).columns

        self.stacked_Layout.setCurrentIndex(index)

        if self.get_data().isNumeric(selected_column) and len(data.columns) == len(numeric_columns):
            self.operation_dropdown.clear()
            self.operation_dropdown.addItems(["Resumen estadístico", "Promedio", "Mediana", "Varianza", "Covarianza", "Correlación", "Distribución", "Desviación estándar", "Min y Max", "Cantidad de valores únicos", "Cantidad de valores faltantes"])
        elif self.get_data().isNumeric(selected_column):
            self.operation_dropdown.clear()
            self.operation_dropdown.addItems(["Resumen estadístico", "Promedio", "Mediana", "Varianza","Desviación estándar", "Min y Max", "Cantidad de valores únicos", "Cantidad de valores faltantes"])     
        else:
            self.operation_dropdown.clear()
            self.operation_dropdown.addItems(["Distribución", "Cantidad de valores únicos", "Cantidad de valores faltantes"])
    
    def on_data_loaded(self) -> None:
        """Manejador para la señal de datos cargados.
            Setea la pila en el índice 0 y habilita las tablas.
            Carga los datos del combo box de columnas.
        """
        self.columns_dropdown.clear()
        self.columns_dropdown.addItems(self.data_manager.get_data().columns)
        #print(f' (OnDataLoaded) Columna seleccionada por default: {self.columns_dropdown.currentText()}')
        self.stacked_Layout.setCurrentIndex(0)
       
    def get_data(self) -> exploreData:
        column_data = self.data_manager.get_data()
      
        if column_data is None:
            QMessageBox.critical(self, "Error", "Columna vacia o no encontrada")
       
        data = column_data
        explore_data = exploreData()
        explore_data.set_data(data)
        return explore_data
                
    def fill_table_with_summary(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de resumen con los datos de explore_data."""
        
        summary_stats = explore_data.get_summary_statistics(selected_column)
        
        dfSummary = pd.DataFrame(summary_stats)
        # Configurar la tabla de resumen con los datos
        # Establecer número de filas y columnas
        table.setColumnCount(len(dfSummary.columns))
        table.setRowCount(len(dfSummary))
        
        # Establecer etiquetas de columna y fila
        
        table.setHorizontalHeaderLabels(dfSummary.columns)
        table.setVerticalHeaderLabels(dfSummary.index)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        for row in range(len(dfSummary)):
            for col in range(len(dfSummary.columns)):
                item = QTableWidgetItem(str(dfSummary.iloc[row, col]))
                table.setItem(row, col, item)
     
    def fill_table_with_distribution(self, table: QTableWidget, explore_data: exploreData, selected_column: str ):
        """Llena la tabla de distribución con los datos de explore_data."""
        distribution = explore_data.calculate_distribution(selected_column)
        #Configurar la tabla de distribución con los datos

        distribution_list_sorted = [(index, value) for index, value in distribution.items()]
        distribution_list_plotting = [(index, value) for index, value in distribution.items()]
        table.setRowCount(len(distribution_list_sorted))
        table.setColumnCount(2)

        table.setHorizontalHeaderLabels(["Valor", "Frecuencia"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        
        distribution_list_sorted.sort(reverse=True, key=lambda x: x[1])
       
        for row, (index, value) in enumerate(distribution_list_sorted):
            item_value = QTableWidgetItem(str(index))
            item_frequency = QTableWidgetItem(str(value))
            table.setItem(row, 0, item_value)
            table.setItem(row, 1, item_frequency)
        self.figure.clear()
        #
        self.plot_bar_graph(distribution_list_plotting)
        self.figure.show()

    def fill_table_with_correlation(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de correlación con los datos de explore_data."""
        correlation = explore_data.calculate_correlation(selected_column)
        
        # Configurar la tabla de correlación con los datos
        # Establecer número de filas y columnas
        table.setColumnCount(len(correlation.columns))
        table.setRowCount(len(correlation.index))
        
        # Establecer etiquetas de columna y fila
        table.setHorizontalHeaderLabels(correlation.columns.astype(str))
        table.setVerticalHeaderLabels(correlation.index.astype(str))
        
        # Llenar la tabla con datos de correlation
        for i, index in enumerate(correlation.index):
            for j, column in enumerate(correlation.columns):
                item = QTableWidgetItem(str(correlation.loc[index, column]))
                table.setItem(i, j, item)

    def fill_table_with_mean(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de promedio con los datos de explore_data."""
        
        mean = explore_data.calculate_mean(selected_column)
        # Configurar la tabla de promedio con los datos
        # Establecer número de filas
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([f"Promedio de columna {selected_column}"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(mean)))

    def fill_table_with_median(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de mediana con los datos de explore_data."""
        median = explore_data.calculate_median(selected_column)
        
        # Configurar la tabla de mediana con los datos
        # Establecer número de filas
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([f"Mediana de columna {selected_column}"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(median)))

    def fill_table_with_variance(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de varianza con los datos de explore_data."""
        variance = explore_data.calculate_variance(selected_column)
        
        
        # Configurar la tabla de varianza con los datos
        # Establecer número de filas
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([f"Varianza de columna {selected_column}"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(variance)))

    def fill_table_with_covariance(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de covarianza con los datos de explore_data. Solo para dataframes numericos"""
        covariance = explore_data.calculate_covariance()
        print(covariance)
        # Configurar la tabla de covarianza con los datos
        # Establecer número de filas y columnas
        table.setColumnCount(len(covariance.columns))
        table.setRowCount(len(covariance.index))
        
        # Establecer etiquetas de columna y fila
        table.setHorizontalHeaderLabels(covariance.columns.astype(str))
        table.setVerticalHeaderLabels(covariance.index.astype(str))
        
        # Llenar la tabla con datos de covariance
        for i, index in enumerate(covariance.index):
            for j, column in enumerate(covariance.columns):
                item = QTableWidgetItem(str(covariance.loc[index, column]))
                table.setItem(i, j, item)

    def fill_table_with_standard_deviation(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de desviación estándar con los datos de explore_data."""
        standard_deviation = explore_data.calculate_standard_deviation(selected_column)
        
        # Configurar la tabla de desviación estándar con los datos
        # Establecer número de filas
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([f"Desviación estándar de columna {selected_column}"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(standard_deviation)))

    def fill_table_with_min_max(self, table: QTableWidget, explore_data: exploreData, selected_column: str): 
        """Llena la tabla de min y max con los datos de explore_data."""
        
        min_max = explore_data.calculate_min_max(selected_column)
        
        # Configurar la tabla de min y max con los datos
        # Establecer número de filas
        table.setRowCount(len(min_max.index))
        table.setColumnCount(len(min_max.columns))
        
        table.setHorizontalHeaderLabels(["Valor"])
        table.setVerticalHeaderLabels(min_max.index.astype(str))
        # Llenar la tabla con datos de min_max
        print(min_max.shape)
        for row in range(len(min_max)):# no se ven los datos, solo se ver los headers.  
            value = min_max.iloc[row, 0]
            item = QTableWidgetItem(str(value))
            table.setItem(row, 0, item)
       
    def fill_table_with_unique_values(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de valores únicos con los datos de explore_data."""
        unique_values = explore_data.get_unique_values(selected_column)
        print(f"Cantidad de valores unicos: {unique_values}")
        # Configurar la tabla de valores únicos con los datos
        # Establecer número de filas
        table.setRowCount(1)
        
        # Llenar la tabla con datos de unique_values
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Cantidad de Valores únicos"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(unique_values)))

    def fill_table_with_missing_values(self, table: QTableWidget, explore_data: exploreData, selected_column: str):
        """Llena la tabla de valores faltantes con los datos de explore_data."""
        missing_values = explore_data.get_missing_values(selected_column)
        print(f'Instancias donde hay valores faltantes: {missing_values}')
        # Configurar la tabla de valores faltantes con los datos
        # Establecer número de filas
        table.setRowCount(1)
        
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Cantidad de Valores faltantes"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.setItem(0, 0, QTableWidgetItem(str(missing_values)))
        # Llenar la tabla con datos de missing_values
    
    
  
    
    def is_numeric(self, value):
        return isinstance(value, (float|int, float|int))
    
    def plot_bar_graph(self, distribution_list:list):
        
        if not all(self.is_numeric(val) for val, _ in distribution_list):
            categoric_values = [val for val, _ in distribution_list]
            categoric_indices = np.arange(len(categoric_values))
            frequencies = [float(freq) for _, freq in distribution_list]
            bg = pg.BarGraphItem(x=categoric_indices, height=frequencies, width=1, brush='b')
            self.figure.addItem(bg)
        else:
           numeric_values = [val for val, _ in distribution_list]
           frequencies = [float(freq) for _, freq in distribution_list] 
           bg = pg.BarGraphItem(x=numeric_values, height=frequencies, width=1, brush='b')
           self.figure.addItem(bg) 
        