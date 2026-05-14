from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
from Model import chatbot
# from ViewModel import LLMBackend

class LLMInsights(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conversation_history = []

    def initUI(self):

        layout = QVBoxLayout()

        #text area for conversation history
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Envía una consulta al Asistente NEDAF")
        self.send_button = QPushButton("Send ▶️")
        
        self.send_button.clicked.connect(self.on_send_clicked) 


        layout.addWidget(self.text_area)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

    def on_send_clicked(self):
        query = self.input_field.text()

        self.text_area.append(f"You: {query} \n")

        self.process_query(query)
        
        self.input_field.clear()
        

    def process_query(self, query):
        # Implement your LLM logic here
        response = chatbot.answer(query)
        
        self.text_area.append(f"NEDAF Assistant: {response}\n")    