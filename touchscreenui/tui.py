import json
import os
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
from voice.listen import VoiceRecognizer
from optional_downloads.wikidlpage import KnowledgeDownloadPage
from PyQt6.QtGui import QPixmap, QImage
from starry.knowledge import KiwixEngine
from starry.intent import IntentRouter
from starry import actions
import glob

class ResponseCard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("response_card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("response_title")
        self.title_label.setWordWrap(True)
        
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.hide()
        
        self.body_label = QtWidgets.QLabel()
        self.body_label.setObjectName("response_body")
        self.body_label.setWordWrap(True)


        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(180, 60)
        self.close_button.clicked.connect(self.hide)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.body_label)
        layout.addStretch()
        layout.addWidget(self.close_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setStyleSheet("""
            QWidget#response_card {
                background-color: rgba(30, 30, 50, 0.95);
                border-radius: 24px;
            }
        """)
    
    def set_response(self, title, summary, image_bytes=None):
        self.title_label.setText(title)
        self.body_label.setText(summary)
        
        if image_bytes:
            image = QImage.fromData(image_bytes)
            pixmap = QPixmap.fromImage(image)
            scaled = pixmap.scaled(300, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled)
            self.image_label.show()
        else:
            self.image_label.hide()

class KeyboardDialog(QtWidgets.QDialog):
    submitted = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("keyboard_dialog")
        self.setWindowTitle("Keyboard")
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        self.input = QtWidgets.QLineEdit()
        self.input.setObjectName("keyboard_input")
        self.input.setPlaceholderText("Type your question")
        self.input.returnPressed.connect(self._submit)
        layout.addWidget(self.input)

        keys_layout = QtWidgets.QGridLayout()
        keys_layout.setHorizontalSpacing(8)
        keys_layout.setVerticalSpacing(8)
        layout.addLayout(keys_layout)

        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row_index, row in enumerate(rows):
            col_offset = 0 if row_index < 2 else 1
            for col_index, key in enumerate(row):
                button = QtWidgets.QPushButton(key)
                button.setObjectName("keyboard_key")
                button.setFixedSize(64, 64)
                button.clicked.connect(lambda _, k=key: self._handle_key(k))
                keys_layout.addWidget(button, row_index, col_index + col_offset)

        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(12)
        layout.addLayout(action_row)

        space_button = QtWidgets.QPushButton("Space")
        space_button.setObjectName("keyboard_action")
        space_button.setFixedHeight(60)
        space_button.clicked.connect(lambda: self._handle_key(" "))

        back_button = QtWidgets.QPushButton("Back")
        back_button.setObjectName("keyboard_action")
        back_button.setFixedHeight(60)
        back_button.clicked.connect(self.input.backspace)

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.setObjectName("keyboard_action")
        clear_button.setFixedHeight(60)
        clear_button.clicked.connect(self.input.clear)

        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.setObjectName("keyboard_action")
        cancel_button.setFixedHeight(60)
        cancel_button.clicked.connect(self.reject)

        enter_button = QtWidgets.QPushButton("Enter")
        enter_button.setObjectName("keyboard_primary")
        enter_button.setFixedHeight(60)
        enter_button.clicked.connect(self._submit)

        action_row.addWidget(space_button, stretch=2)
        action_row.addWidget(back_button)
        action_row.addWidget(clear_button)
        action_row.addWidget(cancel_button)
        action_row.addWidget(enter_button)

        self.input.setFocus()

    def _handle_key(self, key):
        if key == " ":
            self.input.insert(" ")
        else:
            self.input.insert(key.lower())

    def _submit(self):
        text = self.input.text().strip()
        if text:
            self.submitted.emit(text)
        self.accept()

class TouchScreenUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("touchscreen_ui")
        
        self.knowledge_engine = None
        self.response_card = None
        self._init_knowledge_engine()

        self.intent_router = IntentRouter()
        self.intent_handlers = {
            "LIGHT_ON": actions.turn_on_light,
            "LIGHT_OFF": actions.turn_off_light,
        }
        
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
        
        back_wallpaper = QtWidgets.QLabel()
        back_wallpaper.setPixmap(QtGui.QPixmap("wallpapers/earth/dark/01.jpg"))
        back_wallpaper.setScaledContents(True)
        back_layout.addWidget(back_wallpaper)
        
        front_widget = QtWidgets.QWidget()
        front_layout = QtWidgets.QVBoxLayout(front_widget)
        front_layout.setContentsMargins(60, 60, 60, 60)
        front_layout.setSpacing(30)
        
        self.front_time = QtWidgets.QLabel("00:00")
        self.front_time.setObjectName("clock_display")
        self.front_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.front_time.setContentsMargins(20, 0, 0, 20)

        if not knowledge_downloaded:
            knowledge_card = self.create_card("Knowledge Download", "Download knowledge to ask questions", "knowledge_icon")
            knowledge_card.clicked.connect(self.open_knowledge_download)
            front_layout.addWidget(knowledge_card, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.input_preview = QtWidgets.QLabel("")
        self.input_preview.setObjectName("input_preview")
        self.input_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.input_preview.setWordWrap(True)
        self.input_preview.hide()

        front_layout.addStretch()
        front_layout.addWidget(self.input_preview, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        front_layout.addWidget(self.front_time, alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(16)

        voice_button = QtWidgets.QPushButton("Voice")
        voice_button.setObjectName("voice_button")
        voice_button.setFixedSize(200, 80)
        voice_button.clicked.connect(self.toggle_listening)

        keyboard_button = QtWidgets.QPushButton("Keyboard")
        keyboard_button.setObjectName("keyboard_button")
        keyboard_button.setFixedSize(200, 80)
        keyboard_button.clicked.connect(self.open_keyboard)

        button_row.addStretch()
        button_row.addWidget(voice_button)
        button_row.addWidget(keyboard_button)
        button_row.addStretch()
        front_layout.addLayout(button_row)
        
        grid.addWidget(back_widget, 0, 0)
        grid.addWidget(front_widget, 0, 0)
        
        self.is_listening = False
        self.listening_glow = None
        self.glow_animation = None
        
        self.voice_recognizer = VoiceRecognizer(lazy_load=True, unload_on_stop=True)
        self.result_timer = QtCore.QTimer()
        self.result_timer.timeout.connect(self.process_voice_results)
        
        self.last_processed_text = ""
        
        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000) 
        self.update_clock() 

        self.swipe_gesture = QtWidgets.QSwipeGesture(self)
        self.grabGesture(QtCore.Qt.GestureType.SwipeGesture)
        
    def event(self, event):
        if event.type() == QtCore.QEvent.Type.Gesture:
            return self.handle_gesture(event)
        return super().event(event)
    
    def handle_gesture(self, event):
        gesture = event.gesture(QtCore.Qt.GestureType.SwipeGesture)
        if gesture:
            swipe = gesture
            if swipe.state() == QtCore.Qt.GestureState.GestureFinished:
                # Handle swipe gestures for future features
                if swipe.horizontalDirection() == QtWidgets.QSwipeGesture.Direction.Left:
                    print("Swipe left detected")
                elif swipe.horizontalDirection() == QtWidgets.QSwipeGesture.Direction.Right:
                    print("Swipe right detected")
                elif swipe.verticalDirection() == QtWidgets.QSwipeGesture.Direction.Up:
                    print("Swipe up detected")
                elif swipe.verticalDirection() == QtWidgets.QSwipeGesture.Direction.Down:
                    print("Swipe down detected")
            return True
        return False

    def update_clock(self):
        current_time = QtCore.QTime.currentTime()
        # TODO: Get AM and PM in here
        time_string = current_time.toString("HH:mm")
        self.front_time.setText(time_string)


    def open_knowledge_download(self):
        self.download_page = KnowledgeDownloadPage()
        self.download_page.showFullScreen()

    def open_keyboard(self):
        dialog = KeyboardDialog(self)
        dialog.submitted.connect(self.handle_text_query)
        dialog.exec()

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        print("I'm listening")
        self.is_listening = True
        if self.input_preview.isVisible():
            self.input_preview.hide()
        
        self.listening_glow = QtWidgets.QFrame()
        self.listening_glow.setObjectName("listening_glow")
        self.listening_glow.setFixedHeight(60)
        
        glow_layout = QtWidgets.QVBoxLayout(self.listening_glow)
        glow_layout.setContentsMargins(0, 0, 0, 8)
        glow_layout.setSpacing(0)

        self.transcription_box = QtWidgets.QFrame(self.listening_glow)
        self.transcription_box.setObjectName("transcription_box")
        self.transcription_box.setFixedHeight(44)
        self.transcription_box.setStyleSheet(
            "QFrame#transcription_box { background-color: rgba(20, 20, 30, 180); border-radius: 14px; }"
        )
        box_layout = QtWidgets.QHBoxLayout(self.transcription_box)
        box_layout.setContentsMargins(16, 6, 16, 6)

        self.transcription_label = QtWidgets.QLabel("")
        self.transcription_label.setObjectName("transcription")
        self.transcription_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.transcription_label.setWordWrap(True)
        self.transcription_label.setStyleSheet("color: #f0f6ff; font-size: 18px;")
        box_layout.addWidget(self.transcription_label)

        glow_layout.addWidget(
            self.transcription_box,
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop,
        )
        
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
        self.result_timer.start(100) 
    
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
        
    def _init_knowledge_engine(self):
        """Find and load the first available ZIM file."""
        zim_patterns = [
            "knowledge_data/*.zim",
            "../knowledge_data/*.zim",
            "optional_downloads/knowledge_data/*.zim"
        ]
        
        for pattern in zim_patterns:
            zim_files = glob.glob(pattern)
            if zim_files:
                zim_path = zim_files[0]
                print(f"Found ZIM file: {zim_path}")
                self.knowledge_engine = KiwixEngine(zim_path)
                break
        
        if not self.knowledge_engine:
            print("No ZIM file found. Knowledge search will be unavailable.")

    def _extract_search_query(self, text):
        """Extract search query from voice text."""
        text_lower = text.lower()
        
        # Pattern: "who is X", "what is X", "tell me about X"
        prefixes = [
            "who is ", "who was ", "what is ", "what was ",
            "tell me about ", "tell me who ", "tell me what ",
            "who's ", "what's ", "define ", "explain "
        ]
        
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                return text[len(prefix):].strip()
        
        # If no prefix matched, return the whole text (might be a direct query)
        return text.strip()

    def show_knowledge_result(self, result):
        """Display the knowledge search result."""
        if not self.response_card:
            self.response_card = ResponseCard()
            self.response_card.setFixedSize(600, 700)
            
            # Position in center of screen
            screen_geo = QtWidgets.QApplication.primaryScreen().geometry()
            x = (screen_geo.width() - 600) // 2
            y = (screen_geo.height() - 700) // 2
            self.response_card.move(x, y)
            
            # Make it a popup that can be clicked to close
            self.response_card.setWindowFlags(QtCore.Qt.WindowType.Popup)
        
        self.response_card.set_response(
            result.get("title", "Unknown"),
            result.get("summary", ""),
            result.get("image")
        )
        self.response_card.show()
        
        # Auto-close after 45 seconds (giving more time to read on tablet)
        QtCore.QTimer.singleShot(45000, self.response_card.hide)

    def process_voice_results(self):
        results = self.voice_recognizer.get_results()
        if results:
            last_text = results[-1] if results else ""
            if last_text and self.transcription_label:
                self.transcription_label.setText(last_text)
            self._handle_query_text(last_text, show_preview=False)

    def handle_text_query(self, text):
        self._handle_query_text(text, show_preview=True)

    def _handle_intent(self, text):
        if not text or not self.intent_router:
            return False
        result = self.intent_router.handle(text, self.intent_handlers)
        if not result:
            return False

        message = result.get("result") or f"{result['intent']} ({result['score']:.2f})"
        self.input_preview.setText(message)
        self.input_preview.show()
        print(f"Intent matched: {result['intent']} ({result['score']:.2f}) via {result['method']}")

        if self.is_listening:
            self.stop_listening()
        return True

    def _handle_query_text(self, text, show_preview=False):
        if not text:
            return
        if show_preview:
            self.input_preview.setText(text)
            self.input_preview.show()

        if text == self.last_processed_text:
            return
        self.last_processed_text = text

        if self._handle_intent(text):
            return

        # Check if we should perform a knowledge search
        # Extract query and search
        query = self._extract_search_query(text)
        if query and self.knowledge_engine:
            print(f"Searching for: {query}")
            result = self.knowledge_engine.search(query)
            if result:
                print(f"Found: {result['title']}")
                self.show_knowledge_result(result)
                self.stop_listening()
            else:
                print(f"No results for: {query}")


    def thinking_animation(self):
        print("Thinking")


    def create_card(self, name, content, icon):
        button = QtWidgets.QPushButton()
        button.setObjectName("info_card")
        button.setFixedSize(400, 180)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        button.setGraphicsEffect(shadow)
        
        card_layout = QtWidgets.QVBoxLayout(button)
        card_layout.setContentsMargins(30, 24, 30, 24)
        card_layout.setSpacing(12)
        
        title_label = QtWidgets.QLabel(name)
        title_label.setStyleSheet("color: #1a1a2e; font-size: 24px; font-weight: bold;")
        
        content_label = QtWidgets.QLabel(content)
        content_label.setStyleSheet("color: #555; font-size: 18px;")
        content_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(content_label)
        card_layout.addStretch()
        
        return button
