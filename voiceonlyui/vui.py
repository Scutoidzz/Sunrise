from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import *
import sys

class VoiceOnlyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Only UI")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.status_label = QLabel("Listening...")
        self.status_label.setStyleSheet("font-size: 24px; color: white; background-color: #3a3a3a; padding: 15px; border-radius: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.show()
