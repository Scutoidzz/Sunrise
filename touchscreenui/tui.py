import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui

class TouchScreenUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sunrise")

        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        
        back_widget = QtWidgets.QWidget()
        back_widget.setStyleSheet("background-color: #1a1a2e;")
        back_layout = QtWidgets.QVBoxLayout(back_widget)
        
        back_wallpaper = QtWidgets.QLabel("This isn't implemented yet")
        back_wallpaper.setStyleSheet("color: #444; font-size: 24px;")
        back_layout.addWidget(back_wallpaper)
        
        front_widget = QtWidgets.QWidget()
        front_layout = QtWidgets.QVBoxLayout(front_widget)
        front_layout.setContentsMargins(40, 40, 40, 40)
        
        front_time = QtWidgets.QLabel("00:00")
        front_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        front_time.setContentsMargins(0, 0, 0, 0)
        front_time.setStyleSheet("color: white; font-size: 48px;")

        front_layout.addWidget(self.create_card("Card 1", "Content 1", "Icon 1"))
        front_layout.addWidget(self.create_card("Card 2", "Content 2", "Icon 2"))
        front_layout.addStretch()
        front_layout.addWidget(front_time, alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)

        self.listening_animation()
        
        grid.addWidget(back_widget, 0, 0)
        grid.addWidget(front_widget, 0, 0)


    def listening_animation(self):
        print("Listening")
        self.listening_label = QtWidgets.QLabel("I'm listening...")
        
        self.listening_glow = QtWidgets.QFrame()
        self.listening_glow.setFixedHeight(20)
        self.listening_glow.setStyleSheet("background-color: transparent;")
        
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 150, 255, 150)) 
        shadow.setOffset(0)
        self.listening_glow.setGraphicsEffect(shadow)
        
        self.glow_animation = QtCore.QPropertyAnimation(shadow, b"blurRadius")
        self.glow_animation.setDuration(600)  
        self.glow_animation.setStartValue(10)
        self.glow_animation.setEndValue(30)
        self.glow_animation.setLoopCount(-1) 
        self.glow_animation.start()
        
        self.layout().addWidget(self.listening_glow, 0, 0, QtCore.Qt.AlignmentFlag.AlignBottom)


    def thinking_animation(self):
        print("Thinking")


    def create_card(self, name, content, icon):
        card = QtWidgets.QFrame()
        card.setObjectName("info_card")
        card.setFixedSize(300, 160)
        card.setStyleSheet("""
            QFrame#info_card {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                color: #000000;
            }
        """)

        return card
