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
        app.exec()
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
            
            if config.get("touchscreen_enabled", False):
                from touchscreenui.tui import TouchScreenUI
                window = TouchScreenUI()
                window.showFullScreen()
            else:
                from voiceonlyui.vui import VoiceOnlyUI
                window = VoiceOnlyUI()
                window.showFullScreen()
        sys.exit(app.exec())
    else:
        print(f"Config found at {config_path}")
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Config: {config}")
        
        if config.get("touchscreen_enabled", False):
            print("Launching th e Touchscreen")
            from touchscreenui.tui import TouchScreenUI
            window = TouchScreenUI()
            print("Showing TouchScreenUI fullscreen...")
            window.showFullScreen()
        else:
            print("Loading VoiceOnlyUI...")
            from voiceonlyui.vui import VoiceOnlyUI
            window = VoiceOnlyUI()
            print("Showing VoiceOnlyUI fullscreen...")
            window.showFullScreen()
    
    print("Starting app.exec()...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
