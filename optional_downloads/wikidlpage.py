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

        self.knowledge_downloads = QtWidgets.QListWidget()
        self.knowledge_downloads.addItems(["Recommended Knowledge", "Top 100 on Wikipedia", "Top million articles on wikipedia"])
        self.knowledge_downloads.currentItemChanged.connect(self.on_item_selected)
        main_k_view_layout.addWidget(self.knowledge_downloads)
    
        self.book_sizes = {
            "Recommended Knowledge": ("2.1 GB", 2100000000),
            "Top 100 on Wikipedia": ("0.4 GB", 400000000),
            "Top million articles on wikipedia": ("45.5 GB", 45500000000)
        }

        self.stat = os.statvfs('/')
        self.free_space = self.stat.f_bavail * self.stat.f_frsize

        storage_usage_layout = QtWidgets.QVBoxLayout()
        self.storage_usage_label = QtWidgets.QLabel("Approx. download size: Select a book")
        self.storage_drive_picker = QtWidgets.QComboBox()
        self.refresh_drives()
        self.storage_drive_picker.currentTextChanged.connect(self.on_drive_changed)
        self.storage_usage_limit = QtWidgets.QProgressBar()
        self.storage_usage_limit.setMaximum(100)
        self.storage_usage_limit.setValue(0) 

        mark_downloaded_button = QtWidgets.QPushButton("Mark as downloaded")
        mark_downloaded_button.clicked.connect(self.mark_downloaded)
        storage_usage_layout.addWidget(mark_downloaded_button)
        storage_usage_layout.addWidget(self.storage_usage_label)
        storage_usage_layout.addWidget(self.storage_drive_picker)
        storage_usage_layout.addWidget(self.storage_usage_limit)
        
        main_k_view_layout.addLayout(storage_usage_layout)

    def refresh_drives(self):
        self.storage_drive_picker.clear()
        drives = []
        
        search_paths = ["/media", "/mnt", "/run/media"]
        for base_path in search_paths:
            if os.path.exists(base_path):
                for name in os.listdir(base_path):
                    path = os.path.join(base_path, name)
                    if os.path.isdir(path):
                        if name.startswith("."):
                            continue
                        try:
                            stat = os.statvfs(path)
                            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                            if stat.f_blocks > 0:
                                drives.append((name, path, free_gb))
                        except:
                            pass
                        for subname in os.listdir(path):
                            subpath = os.path.join(path, subname)
                            if os.path.isdir(subpath):
                                try:
                                    stat = os.statvfs(subpath)
                                    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                                    if stat.f_blocks > 0:
                                        drives.append((f"{name}/{subname}", subpath, free_gb))
                                except:
                                    pass
        try:
            root_stat = os.statvfs('/')
            root_free_gb = (root_stat.f_bavail * root_stat.f_frsize) / (1024**3)
            drives.append(("System (/)", "/", root_free_gb))
        except:
            pass
        
        seen_paths = set()
        unique_drives = []
        for name, path, free_gb in sorted(drives, key=lambda x: x[2], reverse=True):
            if path not in seen_paths:
                seen_paths.add(path)
                unique_drives.append((name, path, free_gb))
        
        for name, path, free_gb in unique_drives:
            self.storage_drive_picker.addItem(f"{name} ({free_gb:.1f} GB free)", path)
        
        if self.storage_drive_picker.count() == 0:
            self.storage_drive_picker.addItem("No drives found", "/")

    def on_drive_changed(self, text):
        path = self.storage_drive_picker.currentData()
        if path:
            try:
                stat = os.statvfs(path)
                self.free_space = stat.f_bavail * stat.f_frsize
                self.storage_usage_label.setText("Approx. download size: Select a book")
                self.storage_usage_limit.setValue(0)
            except:
                pass

    def on_item_selected(self, current, previous):
        if current is None:
            self.storage_usage_label.setText("Approx. download size: Select a book")
            self.storage_usage_limit.setValue(0)
            return
        
        book_name = current.text()
        size_str, size_bytes = self.book_sizes.get(book_name, ("Unknown", 0))
        
        self.storage_usage_label.setText(f"Approx. download size: {size_str}")
        percent_of_free = min(int((size_bytes / self.free_space) * 100), 100) if self.free_space > 0 else 0
        self.storage_usage_limit.setValue(percent_of_free)

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