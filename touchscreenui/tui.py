import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui

class TouchScreenUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sunrise")
        self.setStyleSheet("background-color: #1a1a2e;")
        
        front_layout = QtWidgets.QVBoxLayout(self)

        front_time = QtWidgets.QLabel("00:00 XM")
        front_time.setStyleSheet("color: white; font-size: 48px;")

        front_layout.addWidget(front_time, alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        front_layout.addWidget(self.create_card("Card 1", "Content 1", "Icon 1"))
        front_layout.addWidget(self.create_card("Card 2", "Content 2", "Icon 2"))
        front_layout.addStretch()





    def create_card(self, name, content, icon):
        card = QtWidgets.QFrame()
        card.setObjectName("info_card")
        card.setFixedSize(300, 160)
        card.setStyleSheet("""
            QFrame#info_card {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)

        return card

        

    




        


        



        
