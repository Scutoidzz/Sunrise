import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    
    config_path = "config.json"
    
    if not os.path.exists(config_path):
        from onboarding.onboard import Onboarding
        window = Onboarding()
        window.showFullScreen()
    else:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        if config.get("touchscreen_enabled", False):
            from touchscreenui.tui import TouchScreenUI
            window = TouchScreenUI()
        else:
            from voiceonlyui.vui import VoiceOnlyUI
            window = VoiceOnlyUI()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
