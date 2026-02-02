import json
import os
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import requests
import sys

class KnowledgeDownloadPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Knowledge Download")
        self.showFullScreen()
        self.main_k_view()

    def main_k_view(self):
        main_k_view_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_k_view_layout)

        knowledge_downloads = QtWidgets.QListWidget()
        knowledge_downloads.addItems(["Recommended Knowledge", "Top 100 on Wikipedia", "Top million articles on wikipedia"])
        main_k_view_layout.addWidget(knowledge_downloads)
    
        recommended_book_size = "2.1 GB"
        top_100_book_size = "0.4 GB"
        top_million_book_size = "45.5 GB"
        # Raw sizes so that I can make the progress bar work.
        recommended_book_size_raw = 2100
        top_100_book_size_raw = 400
        top_million_book_size_raw = 45500

        stat = os.statvfs('/')
        free_space = stat.f_bavail * stat.f_frsize

        storage_usage_layout = QtWidgets.QVBoxLayout()
        storage_usage_label = QtWidgets.QLabel("Approx. download size")
        storage_drive_picker = QtWidgets.QComboBox()
        drives = [name for name in os.listdir("/media") if os.path.isdir(os.path.join("/media", name))]
        storage_drive_picker.addItems(["",] + drives)
        storage_usage_limit = QtWidgets.QProgressBar()
        storage_usage_limit.setValue(50)
        storage_usage_limit.setMaximum(int(free_space))  # Convert free_space to int 

        mark_downloaded_button = QtWidgets.QPushButton("Mark as downloaded")
        mark_downloaded_button.clicked.connect(self.mark_downloaded)
        storage_usage_layout.addWidget(mark_downloaded_button)

        storage_usage_layout.addWidget(storage_usage_label)
        storage_usage_layout.addWidget(storage_drive_picker)
        storage_usage_layout.addWidget(storage_usage_limit)
        
        main_k_view_layout.addLayout(storage_usage_layout)

    def mark_downloaded(self, *args, **kwargs):
        try:
            config_path = "config.json"
            config = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
            
            config["knowledge_downloaded"] = True
            
            with open(config_path, "w") as f:
                json.dump(config, f)
            
            self.close()

        except Exception as e:
            print(f"Error updating config: {e}")