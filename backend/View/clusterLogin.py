#clase realizada para conectarse al cluster a nivel de aplicacion 
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from View.import_data_view import ImportData
class ClusterLogin(QDialog):
   
    def __init__(self):
        super().__init__()
        self.initUI()
       
    def initUI(self):
        self.setGeometry(100,100,300,240)
        #Nombre de ventana
        self.setWindowTitle("Cluster Login")
        #instancia de QVBox
        layout = QVBoxLayout()
         #Label y campo de entrada host 
        label_host = QLabel("Host:")
        self.input_host = QLineEdit()
        layout.addWidget(label_host)
        layout.addWidget(self.input_host)

        #label y campo para el usuario
        label_user = QLabel("Usuario:")
        layout.addWidget(label_user)
        self.input_user = QLineEdit()
        layout.addWidget(self.input_user)

        #label y campo para contraseña
        label_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(label_password)
        layout.addWidget(self.input_password)

        #boton  de conexion 
        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.clicked.connect(self.connect_cluster)  
        #boton de cancelar
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        layout.addWidget(self.btn_connect)
        layout.addWidget(self.btn_cancel)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags()|Qt.WindowType.WindowStaysOnTopHint| Qt.WindowType.Dialog)


    def connect_cluster(self):
        import paramiko as pk
        host = self.input_host.text()
        user = self.input_user.text()
        password = self.input_password.text()
        self.input_password.clear()
        
        try:
            ssh_client = pk.SSHClient()
            ssh_client.set_missing_host_key_policy(pk.AutoAddPolicy())
            ssh_client.connect(hostname=host, username=user, password=password, timeout=10)
            self.accept()
            QMessageBox.information(self, "Exito", "Conexión SSH establecida satisfactoriamente!")

            # TODO: This needs refactoring - ImportData requires data_manager argument
            # For now, connection is validated but file explorer integration is disabled
            # Will be fixed in Phase 3 architectural refactoring
            # importData = ImportData()
            # importData.FileExplorer(host, user, password)

            ssh_client.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")    

    
              
   