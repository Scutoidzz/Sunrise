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
        self.touchscreen_enabled = False
        self.welcome_to_sunrise()

    def welcome_to_sunrise(self):
        layout = QtWidgets.QVBoxLayout()
        
        welcome_text = QtWidgets.QLabel("Welcome to Sunrise!")
        welcome_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        get_started_button = QtWidgets.QPushButton("Get started")
        get_started_button.setFixedSize(300,100)
        get_started_button.clicked.connect(lambda: self.touch_option())

        layout.addWidget(welcome_text)
        layout.addWidget(get_started_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
    def touch_option(self):
        self.clear_widgets()
        
        question = QtWidgets.QLabel("Do you have a touchscreen?")
        question.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        twobuttons = QtWidgets.QHBoxLayout()
        
        
        tyes = QtWidgets.QPushButton("Yes")
        tno = QtWidgets.QPushButton("No")
        tyes.clicked.connect(lambda: self.set_touchscreen(True, tyes.isChecked()))
        tno.clicked.connect(lambda: self.set_touchscreen(False, tno.isChecked()))

        twobuttons.addWidget(tyes)
        twobuttons.addWidget(tno)

        layout = self.layout()
        layout.addWidget(question)
        layout.addLayout(twobuttons)
        layout.setAlignment(twobuttons, QtCore.Qt.AlignmentFlag.AlignCenter)
    
    def set_touchscreen(self, value, is_checked):
        if is_checked:
            self.touchscreen_enabled = value
            self.final_touches_screen()
    
    def final_touches_screen(self):
        self.clear_widgets()
        
        self.loading_label = QtWidgets.QLabel("Setting things up...")
        self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        layout = self.layout()
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
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
            
            download_sst(progress_callback=sst_progress)
            
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
    
    def finish_onboarding(self):
        config = {
            "onboarding_complete": True,
            "has_touchscreen": self.touchscreen_enabled
        }
        with open(os.path.join("..", "config.json"), "w") as f:
            json.dump(config, f, indent=4)
        
        QtWidgets.QMessageBox.information(self, "Complete", "Setup complete!")
        self.close()
    

    def clear_widgets(self):
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_sub_layout(item.layout())
    
    def clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_sub_layout(item.layout())
    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Onboarding()
    window.showFullScreen()
    sys.exit(app.exec())    
    

