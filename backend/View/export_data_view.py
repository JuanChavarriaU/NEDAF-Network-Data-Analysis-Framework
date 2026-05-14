from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class ExportData(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        boton = QPushButton("Exportar Datos")
        layout.addWidget(boton)
        self.setLayout(layout)