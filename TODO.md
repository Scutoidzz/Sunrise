# 🌅 Sunrise: The 12-Hour Marathon (Midnight to Noon)

## 🕑 Sprint 1: The Foundation (12:00 AM - 02:30 AM)
**Goal:** A working storage backend that accurately tracks disk usage.
- [ ] **Create File:** `storage_manager.py` in the root directory.
- [ ] **Class Setup:** Define `StorageManager` class with `SAFE_LIMIT_MB = 450`.
- [ ] **Logic:** Implement `get_directory_size(path)` using `os.scandir` (faster than `os.walk`).
    - [ ] *Constraint:* Ensure it skips `.git` and `__pycache__`.
- [ ] **Logic:** Implement `get_oldest_files(limit=10)` helper.
    - [ ] Returns list of `(filepath, access_time)` tuples sorted by age.
- [ ] **Integration:** Import `StorageManager` in `main.py`.
- [ ] **Startup Check:** In `main.py`, run `storage.check_health()` before launching UI.
    - [ ] If > 450MB, print a warning to console.
- [ ] **Git:** Commit "Sprint 1: Storage Backend Complete"

## 📺 Sprint 2: Visual Feedback (02:30 AM - 04:30 AM)
**Goal:** The UI shows the user (you) exactly how much space is left.
- [ ] **VUI Update:** Open `voiceonlyui/vui.py`.
- [ ] **Widget:** Add `self.storage_label = QLabel("Storage: Checking...")` to `initUI`.
- [ ] **Styling:** Set font size to 10px, color gray (unobtrusive).
- [ ] **Threading:** Create a `QTimer` that fires every 60 seconds.
    - [ ] Connect timer to a method `update_storage_display()`.
    - [ ] *Note:* Call `storage.get_project_size()` inside this method.
- [ ] **TUI Update:** Open `touchscreenui/tui.py`.
- [ ] **Widget:** Add a small progress bar `QProgressBar` for storage.
- [ ] **Git:** Commit "Sprint 2: Real-time UI Monitoring"

## 🧹 Sprint 3: The Janitor (04:30 AM - 07:00 AM)
**Goal:** The system automatically deletes old junk when it gets full.
- [ ] **Folder Setup:** Ensure `logs/` and `voice/temp/` directories exist.
- [ ] **Purge Logic:** Implement `auto_purge()` in `StorageManager`.
    - [ ] *Step 1:* Check if size > `SAFE_LIMIT_MB`.
    - [ ] *Step 2:* If yes, delete oldest `.log` files first.
    - [ ] *Step 3:* If still full, delete oldest `.wav` files in `voice/temp/`.
    - [ ] *Safety:* NEVER delete `config.json` or `.py` files.
- [ ] **Trigger:** Call `auto_purge()` every time a new recording finishes.
- [ ] **Git:** Commit "Sprint 3: Auto-Purge Logic Implemented"

## 🧠 Sprint 4: Brain Optimization (07:00 AM - 09:30 AM)
**Goal:** Fit the AI models into the remaining space.
- [ ] **Sherpa Check:** Verify `sherpa-onnx` model file sizes.
- [ ] **Config:** Add `use_small_models: true` to `config.json`.
- [ ] **Logic:** If `use_small_models` is true, force 16kHz recording rate.
- [ ] **Constraint:** Modify `starry/sl.py` (if used for Starry logic) to respect storage limits.
- [ ] **Git:** Commit "Sprint 4: Model Optimization"

## 🛡️ Sprint 5: Stress Test & Polish (09:30 AM - 12:00 PM)
**Goal:** Break it, fix it, ship it.
- [ ] **Stress Test:** Create a script `fill_disk.py` that generates dummy 10MB files.
    - [ ] Verify `auto_purge` kicks in and deletes them.
- [ ] **Performance:** Check CPU usage on the Celeron during a purge.
- [ ] **Cleanup:** Remove `fill_disk.py`.
- [ ] **Documentation:** Add a `STORAGE.md` explaining the purge policy.
- [ ] **Final Commit:** "Marathon Complete: 12 Hours, 500MB Limit Enforced."

## ☕ Survival Checklist
- [ ] **02:00 AM:** Stretch & Water.
- [ ] **04:00 AM:** Snack (Glucose for brain).
- [ ] **06:00 AM:** 20-minute eye rest (away from screen).
- [ ] **08:00 AM:** Coffee/Tea.
- [ ] **10:00 AM:** Victory Lap (Music).