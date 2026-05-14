import stat
import logging
from PyQt6.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QAbstractItemModel, Qt, QModelIndex
#import paramiko

logger = logging.getLogger("nedaf.file_explorer")
class FileExplorerWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a layout
        layout = QVBoxLayout()
        
        # Create a file system model
        self.model = QFileSystemModel()
        self.model.setRootPath("/")

        # Create a tree view and set the model
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index("/"))

        # Connect double-click event to a custom slot
        self.tree_view.doubleClicked.connect(self.itemDoubleClicked)

        # Add the tree view to the layout
        layout.addWidget(self.tree_view)

        # Set the layout for the widget
        self.setLayout(layout)


    def itemDoubleClicked(self, index):
        # Get the file path of the item that was double-clicked
        file_path = self.model.filePath(index)
        logger.debug(f"Double-clicked file: {file_path}")
        # Here you can implement actions like opening files or navigating into directories

class SSHFileSystemModel(QWidget): #problemas al sobreescribir el file explorer 
    def __init__(self):
        super().__init__()   
        
       
        #NECESITAMOS LOGRAR QUE SE ACTUALIZE LA VISTA EN IMPORTDATA.PY teoricamente el treeview se ve, sin embargo no se coloca la vista en el tab 
    def RemoteFileExplorer(self, host, user, password):
        
        self.layout = QVBoxLayout()
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=host, username=user, password=password) 
        
        self.stfp = self.ssh.open_sftp()
        
        self.stfp.chdir('/home/'+user)
        directory_contents = self.stfp.listdir_attr('.')
        self.tree = QTreeView(self)
        self.file_model = RemoteFileSystemModel()
        self.tree.setModel(self.file_model)
        self.file_model.setDirectoryContents(directory_contents)
        
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)
        

class RemoteFileSystemModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootItem = None
        self.directory_contents = []

    def setDirectoryContents(self, directory_contents):
        self.beginResetModel()
        self.directory_contents = directory_contents
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.directory_contents)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            fileInfo = self.directory_contents[index.row()]
            return fileInfo.filename

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        if row < len(self.directory_contents):
            return self.createIndex(row, column, self.directory_contents[row])

        return QModelIndex()

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable