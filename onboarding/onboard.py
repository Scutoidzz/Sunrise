import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import sys
import os
import random
import platform
from .downloadrequired import download_embedding, download_sst
import threading
import json

class Onboarding(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("onboarding")
        self.touchscreen_enabled = False
        self.setup_main_layout()
        self.welcome_to_sunrise()

    def setup_main_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create a stacked widget to hold different screens
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

    def welcome_to_sunrise(self):
        welcome_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(welcome_widget)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)
        
        welcome_text = QtWidgets.QLabel("Welcome to Sunrise!")
        welcome_text.setObjectName("welcome_text")
        welcome_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        get_started_button = QtWidgets.QPushButton("Get started")
        get_started_button.setObjectName("get_started")
        get_started_button.setFixedSize(400, 120)
        get_started_button.clicked.connect(lambda: self.touch_option())
        
        layout.addWidget(welcome_text)
        layout.addWidget(get_started_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(welcome_widget)
        self.stacked_widget.setCurrentWidget(welcome_widget)
    def touch_option(self):
        touch_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(touch_widget)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)
        
        question = QtWidgets.QLabel("Do you have a touchscreen?")
        question.setObjectName("touchscreen_question")
        question.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        twobuttons = QtWidgets.QHBoxLayout()
        twobuttons.setSpacing(40)
        
        tyes = QtWidgets.QPushButton("Yes")
        tno = QtWidgets.QPushButton("No")
        tyes.setObjectName("touch_option")
        tno.setObjectName("touch_option")
        tyes.setFixedSize(300, 300)
        tno.setFixedSize(300, 300)
        tyes.clicked.connect(lambda: self.set_touchscreen(True))
        tno.clicked.connect(lambda: self.set_touchscreen(False))

        twobuttons.addWidget(tyes)
        twobuttons.addWidget(tno)

        layout.addWidget(question)
        layout.addLayout(twobuttons)
        layout.setAlignment(twobuttons, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Add to stacked widget and show
        self.stacked_widget.addWidget(touch_widget)
        self.stacked_widget.setCurrentWidget(touch_widget)
    
    def set_touchscreen(self, value):
        self.touchscreen_enabled = value
        self.voice_model_selector()
    
    def voice_model_selector(self):
        voice_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(voice_widget)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)
        
        question = QtWidgets.QLabel("Choose Voice Recognition Model")
        question.setObjectName("touchscreen_question")
        question.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        twobuttons = QtWidgets.QHBoxLayout()
        twobuttons.setSpacing(40)
        
        tiny_btn = QtWidgets.QPushButton("Tiny\n(~40MB)")
        small_btn = QtWidgets.QPushButton("Small\n(~120MB)")
        tiny_btn.setObjectName("touch_option")
        small_btn.setObjectName("touch_option")
        tiny_btn.setFixedSize(300, 300)
        small_btn.setFixedSize(300, 300)
        
        tiny_btn.clicked.connect(lambda: self.set_voice_model("tiny"))
        small_btn.clicked.connect(lambda: self.set_voice_model("small"))

        twobuttons.addWidget(tiny_btn)
        twobuttons.addWidget(small_btn)

        layout.addWidget(question)
        layout.addLayout(twobuttons)
        layout.setAlignment(twobuttons, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.stacked_widget.addWidget(voice_widget)
        self.stacked_widget.setCurrentWidget(voice_widget)

    def set_voice_model(self, model_size):
        self.voice_model_size = model_size
        self.low_ram_mode = model_size == "tiny"
        self.final_touches_screen()
    
    def final_touches_screen(self):
        final_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(final_widget)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)
        
        self.loading_label = QtWidgets.QLabel("Setting things up...")
        self.loading_label.setObjectName("loading_label")
        self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setObjectName("progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(40)
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
        # Add to stacked widget and show
        self.stacked_widget.addWidget(final_widget)
        self.stacked_widget.setCurrentWidget(final_widget)
        
        self.download_thread = threading.Thread(target=self.run_downloads, daemon=True)
        self.download_thread.start()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_download_status)
        self.timer.start(100)
        self.downloads_complete = False
    
    def run_downloads(self):
        try:
            self.update_status("Downloading embedding model...", 0)
            
            def embedding_progress(progress):
                mapped_progress = int(progress * 0.4)
                self.update_status(f"Downloading embedding model... {progress}%", mapped_progress)
            
            download_embedding(progress_callback=embedding_progress)
            
            self.update_status("Downloading voice recognition model...", 40)
            
            def sst_progress(progress):
                mapped_progress = 40 + int(progress * 0.5)
                self.update_status(f"Downloading voice model... {progress}%", mapped_progress)
            
            download_sst(model_size=getattr(self, 'voice_model_size', 'tiny'), progress_callback=sst_progress)
            
            self.update_status("Extracting files...", 95)
            self.update_status("Setup complete!", 100)
            self.downloads_complete = True
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 100)
            self.downloads_complete = True
    
    def update_status(self, message, progress):
        QtCore.QMetaObject.invokeMethod(
            self.loading_label,
            "setText",
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, message)
        )
        QtCore.QMetaObject.invokeMethod(
            self.progress_bar,
            "setValue",
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(int, progress)
        )
    
    def check_download_status(self):
        if self.downloads_complete:
            self.timer.stop()
            self.finish_onboarding()

    def have_internet():
        internetlayout = QVBoxLayout()
    
    def finish_onboarding(self):
        config = {
            "onboarding_complete": True,
            "touchscreen_enabled": self.touchscreen_enabled,
            "voice_model_size": getattr(self, 'voice_model_size', 'tiny'),
            "low_ram_mode": getattr(self, 'low_ram_mode', True),
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        QtWidgets.QMessageBox.information(self, "Setup Complete", "Welcome to Sunrise")
        self.onboarding_finished = True
        self.close()

    
    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Onboarding()
    window.showFullScreen()
    sys.exit(app.exec())    
    
