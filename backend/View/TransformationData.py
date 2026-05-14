from PyQt6.QtWidgets import( QWidget, QVBoxLayout, QPushButton,
 QWidget, QCheckBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)

<<<<<<<< HEAD:View/transform_data_view.py
from Model.transformation_logic import TransformationData
from ViewModel.data_manager import DataManager
========
from Model.transformationData import TransformationData
from Model.DataManager import DataManager
>>>>>>>> 5880c45 (Organizing Architechture in Model-View. Files were moved and place into their corresponding folders. and the refactoring was made.):View/TransformationData.py

class TransformationDataWindow(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        self.data_manager.data_loaded.connect(lambda: self.enable_ui_elements(True))#no se habilita el boton una vez que se manda la señal de que los datos estan cargados
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        #checkboxes para las transformaciones
       # self.checkbox_duplicates = QCheckBox("Eliminar duplicados")
        self.checkbox_missing = QCheckBox("Eliminar valores faltantes")
        self.checkbox_normalize = QCheckBox("Normalizar")
        self.data_table = QTableWidget()
        self.data_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # read only

       # layout.addWidget(self.checkbox_duplicates)
       

        #self.status_label = QLabel("Cargando datos...")
        
        #boton para aplicar transformaciones
        self.apply_button = QPushButton("Aplicar transformaciones")
        self.apply_button.clicked.connect(self.apply_transformations)
        self.enable_ui_elements(option=False)
        #viz data area
        #self.data_view = QTextEdit()
        #self.data_view.setReadOnly(True)
        
        layout.addWidget(self.checkbox_missing)
        layout.addWidget(self.checkbox_normalize)
        layout.addWidget(self.apply_button)
        #layout.addWidget(self.data_view)
        layout.addWidget(self.data_table)

        self.setLayout(layout)


    def enable_ui_elements(self, option: bool):
        """Habilitar elementos de la interfaz cuando se cargue el DataFrame."""
        # Cambiar mensaje de estado
        #self.status_label.setText("Datos cargados")
        # Habilitar botón de aplicar transformaciones
        self.apply_button.setEnabled(option)


    def apply_transformations(self):
        data = self.data_manager.get_data()
        self.transformation_data = TransformationData(data)
        tranformations = []
        #if self.checkbox_duplicates.isChecked():
        #        self.transformation_data.delete_duplicates()
        #       tranformations.append("Duplicados eliminados")
        if self.checkbox_missing.isChecked():
                self.transformation_data.cut_missing_values()
                tranformations.append("Valores faltantes eliminados")
        if self.checkbox_normalize.isChecked():
                self.transformation_data.normalize_data()
                tranformations.append("Datos normalizados")
        #transformation data, if we operate the dataframe, show it modified and updated with the set_data method of the data manager class  
        #simulacion de aplicar las transformaciones y actualizar vista de datos
        #transformed_data = "Datos transformados:\n\n" + "\n".join(tranformations)
        #self.data_view.setPlainText(transformed_data)
        QMessageBox.information(self, "Exito", f"Los datos se han transformado existosamente.")
        self.data_manager.set_data(self.transformation_data.get_data())
        self.fill_data_table(self.transformation_data.get_data())

    def fill_data_table(self, df):
       #vista previa del df
      preview_data = df.head(100).values
      #config # of rows and columns
      self.data_table.setRowCount(len(preview_data))
      self.data_table.setColumnCount(len(preview_data[0]))
      #fill table
      for row in range(len(preview_data)):
          for column in range (len(preview_data[0])):
              item = QTableWidgetItem(str(preview_data[row][column]))
              self.data_table.setItem(row, column, item)