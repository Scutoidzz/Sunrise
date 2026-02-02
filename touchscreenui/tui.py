import json
import os
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
from voice.listen import VoiceRecognizer
from optional_downloads.wikidlpage import KnowledgeDownloadPage

class TouchScreenUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Read config
        config_path = "config.json"
        knowledge_downloaded = False
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    knowledge_downloaded = config.get("knowledge_downloaded", False)
            except:
                pass
        
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

        # Only add the knowledge card if not downloaded
        if not knowledge_downloaded:
            knowledge_card = self.create_card("Knowledge Download", "Download essential knowledge for offline use", "knowledge_icon")
            knowledge_card.clicked.connect(self.open_knowledge_download)
            front_layout.addWidget(knowledge_card)

        front_layout.addStretch()
        front_layout.addWidget(front_time, alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        
        voice_button = QtWidgets.QPushButton("Voice")
        voice_button.setFixedSize(120, 50)
        voice_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 150, 255, 0.8);
                color: white;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 200, 0.9);
            }
        """)
        voice_button.clicked.connect(self.toggle_listening)
        front_layout.addWidget(voice_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        grid.addWidget(back_widget, 0, 0)
        grid.addWidget(front_widget, 0, 0)
        
        self.is_listening = False
        self.listening_glow = None
        self.glow_animation = None
        
        self.voice_recognizer = VoiceRecognizer()
        self.result_timer = QtCore.QTimer()
        self.result_timer.timeout.connect(self.process_voice_results)


    def open_knowledge_download(self):
        self.download_page = KnowledgeDownloadPage()
        self.download_page.showFullScreen()

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        print("I'm listening")
        self.is_listening = True
        
        self.listening_glow = QtWidgets.QFrame()
        self.listening_glow.setFixedHeight(60)
        self.listening_glow.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255, 255, 0),
                    stop:0.7 rgba(255, 255, 255, 20),
                    stop:0.9 rgba(255, 255, 255, 60),
                    stop:1 rgba(255, 255, 255, 100));
                border: none;
            }
        """)
        
        # Add transcription label on top of glow
        glow_layout = QtWidgets.QVBoxLayout(self.listening_glow)
        glow_layout.setContentsMargins(0, 0, 0, 0)
        self.transcription_label = QtWidgets.QLabel("")
        self.transcription_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.transcription_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
        """)
        glow_layout.addWidget(self.transcription_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QtGui.QColor(0, 150, 255, 200)) 
        shadow.setOffset(0, -10)
        self.listening_glow.setGraphicsEffect(shadow)
        
        self.glow_animation = QtCore.QPropertyAnimation(shadow, b"blurRadius")
        self.glow_animation.setDuration(1200)  
        self.glow_animation.setStartValue(20)
        self.glow_animation.setEndValue(60)
        self.glow_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
        self.glow_animation.setLoopCount(-1) 
        self.glow_animation.start()
        
        self.layout().addWidget(self.listening_glow, 1, 0, QtCore.Qt.AlignmentFlag.AlignBottom)
        
        self.voice_recognizer.start_listening()
        self.result_timer.start(100)  # Check every 100ms
    
    def stop_listening(self):
        print("Listening stopped")
        self.is_listening = False
        
        if self.glow_animation:
            self.glow_animation.stop()
        if self.listening_glow:
            self.listening_glow.setParent(None)
            self.listening_glow.deleteLater()
            self.listening_glow = None
        
        self.voice_recognizer.stop_listening()
        self.result_timer.stop()
        
    def process_voice_results(self):
        results = self.voice_recognizer.get_results()
        if results:
            print("Recognized:", results)
            # Display transcription on top of the glow
            last_text = results[-1] if results else ""
            if last_text and self.transcription_label:
                self.transcription_label.setText(last_text)


    def thinking_animation(self):
        print("Thinking")


    def create_card(self, name, content, icon):
        button = QtWidgets.QPushButton()
        button.setObjectName("info_card")
        button.setFixedSize(320, 140)
        button.setStyleSheet("""
            QPushButton#info_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(240, 245, 255, 0.95));
                border-radius: 16px;
                border: 1px solid rgba(200, 220, 255, 0.3);
            }
        """)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        button.setGraphicsEffect(shadow)
        
        card_layout = QtWidgets.QVBoxLayout(button)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(8)
        
        title_label = QtWidgets.QLabel(name)
        title_label.setStyleSheet("color: #1a1a2e; font-size: 18px; font-weight: bold;")
        
        content_label = QtWidgets.QLabel(content)
        content_label.setStyleSheet("color: #555; font-size: 14px;")
        content_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(content_label)
        card_layout.addStretch()
        
        return button
