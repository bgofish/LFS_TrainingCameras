"""
Camera Training Toggle – Main Panel
Features:
  - Search/filter by name
  - Enable/Disable all
  - Frame range toggle (disable every Nth frame, or a start-end range)
  - Disabled cameras shown differently
  - Persist state to JSON alongside the plugin
"""
import re
import io
import sys
import json
import os
import lichtfeld as lf

# Path for persisting camera state
_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "camera_states.json")


# ── scene helpers ─────────────────────────────────────────────────────────────

def _get_camera_states() -> list[tuple[str, bool]]:
    old = sys.stdout
    sys.stdout = buf = io.StringIO()
    lf.list_scene()
    sys.stdout = old
    raw = buf.getvalue()
    return [
        (m.group(2), m.group(1) == '+')
        for m in re.finditer(r'\[(\S+)\s*\]\s+([\w.]+)\s+\(CAMERA,', raw)
    ]


def _save_state(states: list[tuple[str, bool]]) -> None:
    try:
        data = {name: enabled for name, enabled in states}
        with open(_STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        lf.log.warning(f"[camera_toggle] Could not save state: {e}")


def _load_state() -> dict[str, bool] | None:
    try:
        if os.path.exists(_STATE_FILE):
            with open(_STATE_FILE) as f:
                return json.load(f)
    except Exception as e:
        lf.log.warning(f"[camera_toggle] Could not load state: {e}")
    return None


def _apply_state(saved: dict[str, bool]) -> None:
    for name, enabled in saved.items():
        lf.set_camera_training_enabled(name, enabled)


# ── panel ─────────────────────────────────────────────────────────────────────

class MainPanel(lf.ui.Panel):
    id    = "camera_toggle.main_panel"
    label = "Cameras"
    space = lf.ui.PanelSpace.MAIN_PANEL_TAB
    order = 25

    def __init__(self):
        self._filter       = ""
        self._every_n      = 2
        self._range_start  = 0
        self._range_end    = 0
        self._range_inited = False

    def draw(self, ui) -> None:
        if not lf.has_scene():
            ui.label("No scene loaded.")
            return

        states = _get_camera_states()

        if not states:
            ui.label("No cameras found in scene.")
            return

        enabled_count  = sum(1 for _, e in states if e)
        disabled_count = len(states) - enabled_count
        max_index      = len(states) - 1

        if not self._range_inited:
            self._range_end    = max_index
            self._range_inited = True

        # ── summary ──────────────────────────────────────────────────────────
        ui.label(f"{len(states)} cameras  |  {enabled_count} on  {disabled_count} off")
        ui.separator()

        # ── bulk actions ──────────────────────────────────────────────────────
        if ui.button("Enable all"):
            for name, _ in states:
                lf.set_camera_training_enabled(name, True)

        if ui.button("Disable all"):
            for name, _ in states:
                lf.set_camera_training_enabled(name, False)

        ui.separator()

        # ── every-N toggle (button-based stepper) ─────────────────────────────
        ui.label("Keep every Nth frame only:")
        ui.label(f"  N = {self._every_n}")
        if ui.button("N  −"):
            self._every_n = max(2, self._every_n - 1)
        if ui.button("N  +"):
            self._every_n = min(50, self._every_n + 1)
        if ui.button(f"Apply: keep every {self._every_n}nd frame"):
            for i, (name, _) in enumerate(states):
                lf.set_camera_training_enabled(name, i % self._every_n == 0)

        ui.separator()

        # ── range disable (button-based steppers) ─────────────────────────────
        ui.label("Disable frame range (by index):")
        ui.label(f"  From = {self._range_start}  |  To = {self._range_end}")
        if ui.button("From −"):
            self._range_start = max(0, self._range_start - 1)
        if ui.button("From +"):
            self._range_start = min(max_index, self._range_start + 1)
        if ui.button("To  −"):
            self._range_end = max(0, self._range_end - 1)
        if ui.button("To  +"):
            self._range_end = min(max_index, self._range_end + 1)

        if ui.button("Disable range"):
            lo = min(self._range_start, self._range_end)
            hi = max(self._range_start, self._range_end)
            for i, (name, _) in enumerate(states):
                if lo <= i <= hi:
                    lf.set_camera_training_enabled(name, False)

        if ui.button("Enable range"):
            lo = min(self._range_start, self._range_end)
            hi = max(self._range_start, self._range_end)
            for i, (name, _) in enumerate(states):
                if lo <= i <= hi:
                    lf.set_camera_training_enabled(name, True)

        ui.separator()

        # ── persist ───────────────────────────────────────────────────────────
        if ui.button("Save state"):
            _save_state(states)
            lf.log.info("[camera_toggle] State saved.")

        if ui.button("Load & apply saved state"):
            saved = _load_state()
            if saved:
                _apply_state(saved)
                lf.log.info(f"[camera_toggle] Loaded and applied {len(saved)} camera states.")
            else:
                lf.log.warning("[camera_toggle] No saved state found.")

        ui.separator()

        # ── filter + per-camera list ──────────────────────────────────────────
        ui.label("Filter:")
        self._filter = ui.string_field("Filter", self._filter)

        filt = self._filter.lower()
        shown = [(n, e) for n, e in states if filt in n.lower()]
        ui.label(f"Showing {len(shown)} of {len(states)}")
        ui.separator()

        for name, enabled in shown:
            label = f"[ON]  {name}" if enabled else f"[OFF] {name}"
            if ui.button(label):
                lf.set_camera_training_enabled(name, not enabled)


def on_load() -> None:
    lf.register_class(MainPanel)
    lf.log.info("[camera_toggle] Plugin loaded.")
    saved = _load_state()
    if saved:
        _apply_state(saved)
        lf.log.info(f"[camera_toggle] Auto-applied saved state for {len(saved)} cameras.")


def on_unload() -> None:
    lf.unregister_class(MainPanel)
