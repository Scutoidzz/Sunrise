import json
import os
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import requests
import sys
import threading
from optional_downloads.download_knowledge import kiwix_download

class DownloadCompleteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Complete")
        self.setObjectName("complete_dialog")
        self.showFullScreen()
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        complete_label = QtWidgets.QLabel("Download Complete!")
        complete_label.setObjectName("complete_message")
        complete_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        continue_button = QtWidgets.QPushButton("Continue")
        continue_button.setObjectName("continue_button")
        continue_button.setFixedSize(300, 100)
        continue_button.clicked.connect(self.accept)
        
        layout.addStretch()
        layout.addWidget(complete_label)
        layout.addSpacing(60)
        layout.addWidget(continue_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

class DownloadProgressDialog(QtWidgets.QDialog):
    def __init__(self, book_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading...")
        self.setObjectName("download_dialog")
        self.showFullScreen()
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QtWidgets.QLabel(f"Downloading {book_name}...")
        self.status_label.setObjectName("download_status")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setObjectName("download_progress")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(50)
        
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addSpacing(30)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
    
    def update_progress(self, percent):
        self.progress_bar.setValue(percent)
        if percent >= 100:
            self.status_label.setText("Download Complete!")


class KnowledgeDownloadPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("download_page")
        
        self.setWindowTitle("Knowledge Download")
        self.showFullScreen()
        self.main_k_view()

    def main_k_view(self):
        main_k_view_layout = QtWidgets.QHBoxLayout(self)
        main_k_view_layout.setContentsMargins(60, 60, 60, 60)
        main_k_view_layout.setSpacing(40)

        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setObjectName("back_button")
        self.back_button.setFixedSize(150, 60)
        self.back_button.clicked.connect(self.close)
        self.knowledge_downloads = QtWidgets.QListWidget()
        self.knowledge_downloads.setObjectName("download_list")
        self.knowledge_downloads.setFont(QtGui.QFont("Arial", 24))
        self.knowledge_downloads.addItems(["Recommended Knowledge", "Top 100 on Wikipedia", "Top million articles on wikipedia"])
        self.knowledge_downloads.currentItemChanged.connect(self.on_item_selected)
        main_k_view_layout.addWidget(self.back_button)
        main_k_view_layout.addWidget(self.knowledge_downloads)
    
        self.book_sizes = {
            "Recommended Knowledge": ("2.1 GB", 2100000000),
            "Top 100 on Wikipedia": ("0.4 GB", 400000000),
            "Top million articles on wikipedia": ("45.5 GB", 45500000000)
        }

        self.book_keys = {
            "Recommended Knowledge": "recommended",
            "Top 100 on Wikipedia": "100",
            "Top million articles on wikipedia": "1m"
        }

        self.stat = os.statvfs('/')
        self.free_space = self.stat.f_bavail * self.stat.f_frsize

        storage_usage_layout = QtWidgets.QVBoxLayout()
        self.storage_usage_label = QtWidgets.QLabel("Approx. download size: Select a book")
        self.storage_usage_label.setObjectName("storage_label")
        self.storage_drive_picker = QtWidgets.QComboBox()
        self.storage_drive_picker.setObjectName("drive_picker")
        self.storage_drive_picker.setFont(QtGui.QFont("Arial", 20))
        self.refresh_drives()
        self.storage_drive_picker.currentTextChanged.connect(self.on_drive_changed)
        self.storage_usage_limit = QtWidgets.QProgressBar()
        self.storage_usage_limit.setObjectName("storage_bar")
        self.storage_usage_limit.setMaximum(100)
        self.storage_usage_limit.setValue(0) 
        self.storage_usage_limit.setFixedHeight(40)

        self.start_downloading_button = QtWidgets.QPushButton("Download")
        self.start_downloading_button.setObjectName("download_button")
        self.start_downloading_button.setFixedSize(300, 100)
        self.start_downloading_button.clicked.connect(self.on_download_clicked)
        storage_usage_layout.addWidget(self.start_downloading_button)
        storage_usage_layout.addSpacing(30)
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

    def on_download_clicked(self):
        current_item = self.knowledge_downloads.currentItem()
        if not current_item:
            return
        
        book_name = current_item.text()
        book_key = self.book_keys.get(book_name)
        if not book_key:
            return
        
        self.start_downloading_button.setEnabled(False)
        
        # Create and show download progress dialog
        self.download_dialog = DownloadProgressDialog(book_name, self)
        self.download_dialog.show()
        
        def progress_callback(percent):
            # Use invokeMethod to safely update UI from background thread
            QtCore.QMetaObject.invokeMethod(
                self.download_dialog.progress_bar,
                "setValue",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(int, percent)
            )
        
        def download_thread():
            kiwix_download(book_key, progress_callback)
            # Show completion dialog on main thread
            QtCore.QMetaObject.invokeMethod(
                self,
                "show_completion_dialog",
                QtCore.Qt.ConnectionType.QueuedConnection
            )
        
        thread = threading.Thread(target=download_thread)
        thread.start()

    def show_completion_dialog(self):
        self.download_dialog.accept()
        self.start_downloading_button.setEnabled(True)
        
        completion_dialog = DownloadCompleteDialog(self)
        completion_dialog.exec()
        
        self.mark_downloaded()

    def mark_downloaded(self):
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