import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import logging

SHIP_READY_CHECKLIST = [
    "Define release scope and freeze features",
    "Confirm target OS versions and hardware support",
    "Finalize app name, icon, and branding",
    "Verify versioning scheme and bump version",
    "Create a release branch and tag strategy",
    "Run full unit test suite",
    "Run integration tests for onboarding flow",
    "Run end-to-end tests for primary user journeys",
    "Test fresh install on clean machine",
    "Test upgrade from previous version",
    "Verify app launches without network access",
    "Check startup time and splash/loading behavior",
    "Profile memory usage over long sessions",
    "Profile CPU usage during idle and heavy use",
    "Verify graceful handling of low disk space",
    "Validate config migrations from older formats",
    "Check settings persistence and recovery",
    "Confirm accessibility labels and keyboard navigation",
    "Check contrast ratios and font scaling",
    "Validate touch targets for touchscreen UI",
    "Verify voice-only UI flow end to end",
    "Verify error dialogs are clear and actionable",
    "Confirm logging level defaults are sane",
    "Ensure logs do not contain sensitive data",
    "Add crash reporting and test a crash path",
    "Set up analytics/telemetry opt-in flow",
    "Document data collection and retention",
    "Create privacy policy and link it in-app",
    "Create terms of service / EULA",
    "Review third-party licenses and attributions",
    "Check open-source license compatibility",
    "Run security scan on dependencies",
    "Pin dependency versions in requirements.txt",
    "Verify offline assets are bundled",
    "Validate asset paths on all platforms",
    "Verify application window sizing on all resolutions",
    "Test high-DPI scaling behavior",
    "Ensure graceful handling of missing optional assets",
    "Remove debug prints and dev-only flags",
    "Verify error telemetry is rate-limited",
    "Add a safe-mode/repair startup option",
    "Create a backup/restore flow for user data",
    "Confirm default config values are sensible",
    "Confirm onboarding can be skipped or retried",
    "Update README with install and run steps",
    "Create release notes and changelog",
    "Create user guide / help content",
    "Prepare support email or ticket system",
    "Set up status page or incident process",
    "Add automated build for all targets",
    "Package app (installer, DMG, MSI, or AppImage)",
    "Verify auto-update mechanism if used",
    "Test uninstaller and cleanup behavior",
    "Validate config file permissions",
    "Verify app can run without admin privileges",
    "Set up crash log collection and triage flow",
    "Add basic health checks on startup",
    "Perform localization review (if shipping multiple languages)",
    "Prepare screenshots and promo assets",
    "Set up monitoring for key errors post-launch",
    "Create rollback plan for bad release",
    "Define success metrics for the release",
    "Schedule release and coordinate announcements",
    "Do final smoke test on release build",
]

def main():
    app = QApplication(sys.argv)





    
    # Load stylesheet
    try:
        with open("styles.qss", "r") as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
    except FileNotFoundError:
            print("2+2=6")
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
                logging.info("Configuration complete")
                
                from touchscreenui.tui import TouchScreenUI
                window = TouchScreenUI()
                window.showNormal()
            else:
                logging.info("Configuration complete")
                from voiceonlyui.vui import VoiceOnlyUI
                window = VoiceOnlyUI()
                window.showNormal()  # Debug: use normal window
        sys.exit(app.exec())
    else:
        print(f"Config found at {config_path}")
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Config: {config}")
        
        if config.get("touchscreen_enabled", False):
            print("Launching the Touchscreen")
            from touchscreenui.tui import TouchScreenUI
            window = TouchScreenUI()
            print("Showing TouchScreenUI...")
            window.showNormal()
        else:
            print("Loading VoiceOnlyUI...")
            from voiceonlyui.vui import VoiceOnlyUI
            window = VoiceOnlyUI()
            print("Showing VoiceOnlyUI...")
            window.showNormal()
    
    print("Starting app.exec()...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
