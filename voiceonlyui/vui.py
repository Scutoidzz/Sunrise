from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import *
import sys
from voice.listen import VoiceRecognizer
import logging
from starry.intent import IntentRouter
from starry import actions

class VoiceOnlyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Only UI")
        self.setGeometry(100, 100, 800, 600)
        self.setObjectName("voice_only_ui")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)
        self.setLayout(layout)
        
        self.status_label = QLabel("Listening...")
        self.status_label.setObjectName("voice_status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.status_label)

        self.intent_router = IntentRouter()
        self.intent_handlers = {
            "LIGHT_ON": actions.turn_on_light,
            "LIGHT_OFF": actions.turn_off_light,
        }

        self.keyboard_button = QPushButton("Keyboard")
        self.keyboard_button.setObjectName("keyboard_button")
        self.keyboard_button.setFixedSize(220, 70)
        self.keyboard_button.clicked.connect(self.open_keyboard)
        layout.addWidget(self.keyboard_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        
        self.voice_recognizer = VoiceRecognizer(lazy_load=True, unload_on_stop=True)
        self.voice_recognizer.start_listening()
        
        self.result_timer = QTimer()
        self.result_timer.timeout.connect(self.process_voice_results)
        self.result_timer.start(100)  # Check every 100ms
        
        self.show()
        
    def open_keyboard(self):
        text, ok = QInputDialog.getText(self, "Keyboard Input", "Type your question:")
        if ok and text.strip():
            self._handle_text(text.strip(), source="Typed")

    def _handle_intent(self, text):
        if not text or not self.intent_router:
            return None
        result = self.intent_router.handle(text, self.intent_handlers)
        if not result:
            return None
        message = result.get("result") or f"{result['intent']} ({result['score']:.2f})"
        print(f"Intent matched: {result['intent']} ({result['score']:.2f}) via {result['method']}")
        return message

    def _handle_text(self, text, source="Heard"):
        action_message = self._handle_intent(text)
        if action_message:
            self.status_label.setText(f"{source}: {text} -> {action_message}")
        else:
            self.status_label.setText(f"{source}: {text}")

    def process_voice_results(self):
        results = self.voice_recognizer.get_results()
        if results:
            last_result = results[-1]
            self._handle_text(last_result, source="Heard")
