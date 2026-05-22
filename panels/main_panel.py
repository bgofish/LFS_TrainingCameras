"""
Camera Training Toggle – Main Panel
"""
import re
import io
import sys
import json
import os
from collections import Counter
import lichtfeld as lf

def _get_dataset_dir() -> str:
    """Return the currently loaded dataset path, or a safe fallback."""
    try:
        return lf.dataset_params().data_path
    except Exception:
        fallback = os.path.join(os.path.expanduser("~"), ".lichtfeld", "plugins", "Cameras")
        lf.log.info(f"[camera_toggle] Could not get dataset path, using fallback: {fallback}")
        return fallback

def _get_state_file() -> str:
    return os.path.join(_get_dataset_dir(), "camera_states.json")


def _open_dataset_folder() -> None:
    """Open the current dataset folder in the native file-manager (cross-platform)."""
    import subprocess, platform
    folder = _get_dataset_dir()
    os.makedirs(folder, exist_ok=True)
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(folder)                # noqa: S606
        elif system == "Darwin":
            subprocess.Popen(["open", folder])
        else:                                   # Linux / other POSIX
            subprocess.Popen(["xdg-open", folder])
    except Exception as e:
        lf.log.info(f"[camera_toggle] Could not open folder: {e}")


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
        state_file = _get_state_file()
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        data = {name: enabled for name, enabled in states}
        with open(state_file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        lf.log.info(f"[camera_toggle] Could not save state: {e}")


def _load_state() -> dict[str, bool] | None:
    try:
        state_file = _get_state_file()
        if os.path.exists(state_file):
            with open(state_file) as f:
                return json.load(f)
    except Exception as e:
        lf.log.info(f"[camera_toggle] Could not load state: {e}")
    return None


def _apply_state(saved: dict[str, bool]) -> None:
    for name, enabled in saved.items():
        lf.set_camera_training_enabled(name, enabled)


def _detect_repeating_patterns(names: list[str]) -> list[str]:
    if not names:
        return []

    fragments = []
    for name in names:
        base = os.path.splitext(name)[0]
        tokens = re.split(r'[_.\-\s]+', base)
        for token in tokens:
            if token and not token.isdigit() and len(token) >= 2:
                fragments.append(token)

    counts = Counter(fragments)
    repeating_patterns = [word for word, count in counts.items() if count > 1]
    return sorted(repeating_patterns, key=lambda x: (-len(x), x))


class MainPanel(lf.ui.Panel):
    id    = "camera_toggle.main_panel"
    label = "Cameras"
    space = lf.ui.PanelSpace.MAIN_PANEL_TAB
    order = 25

    def __init__(self):
        super().__init__()
        self._active_pattern = "All"
        self._every_n        = 2
        self._range_start    = 0
        self._range_end      = 0
        self._range_inited   = False
        
        self._cached_states = []
        self._needs_refresh = True
        self._frustum_scale = lf.get_render_settings().camera_frustum_scale

    def draw(self, ui) -> None:
        if not lf.has_scene():
            ui.label("No scene loaded.")
            return

        if self._needs_refresh or not self._cached_states:
            self._cached_states = _get_camera_states()
            self._needs_refresh = False

        states = self._cached_states
        if not states:
            ui.label("No cameras found in scene.")
            if ui.button("Force Sync Scene"):
                self._needs_refresh = True
            return

        enabled_count  = sum(1 for _, e in states if e)
        disabled_count = len(states) - enabled_count

        if not self._range_inited:
            self._range_end    = max(0, len(states) - 1)
            self._range_inited = True

        # ── summary ──────────────────────────────────────────────────────────
        ui.label(f"{len(states)} cameras  |  {enabled_count} on  {disabled_count} off")
        
        if ui.button("🔄 Sync/Refresh List"):
            self._needs_refresh = True

        ui.separator()

        # ── frustum scale slider ──────────────────────────────────────────────
        ui.label(f"Frustum Scale: {self._frustum_scale:.2f}")
        if ui.button("◀◀"):
            self._frustum_scale = max(0.01, round(self._frustum_scale - 0.10, 2))
            lf.get_render_settings().camera_frustum_scale = self._frustum_scale
        ui.same_line()
        if ui.button("◀"):
            self._frustum_scale = max(0.01, round(self._frustum_scale - 0.01, 2))
            lf.get_render_settings().camera_frustum_scale = self._frustum_scale
        ui.same_line()
        if ui.button("▶"):
            self._frustum_scale = min(10.0, round(self._frustum_scale + 0.01, 2))
            lf.get_render_settings().camera_frustum_scale = self._frustum_scale
        ui.same_line()
        if ui.button("▶▶"):
            self._frustum_scale = min(10.0, round(self._frustum_scale + 0.10, 2))
            lf.get_render_settings().camera_frustum_scale = self._frustum_scale
        ui.same_line()
        if ui.button("Reset##fscale"):
            self._frustum_scale = 0.25
            lf.get_render_settings().camera_frustum_scale = self._frustum_scale

        ui.separator()

        # ── smart pattern matching grid ───────────────────────────────────────
        ui.label(f"Active Text Filter: [{self._active_pattern}]")
        
        camera_names = [n for n, _ in states]
        detected_patterns = _detect_repeating_patterns(camera_names)
        
        if ui.button("Show All"):
            self._active_pattern = "All"
            self._range_inited = False
            
        for pattern in detected_patterns[:12]:
            ui.same_line()
            if ui.button(pattern):
                self._active_pattern = pattern
                self._range_start = 0  
                self._range_inited = False  
                
        ui.separator()

        shown = []
        for name, enabled in states:
            if self._active_pattern == "All" or self._active_pattern.lower() in name.lower():
                shown.append((name, enabled))

        max_shown_index = max(0, len(shown) - 1)
        if self._range_end > max_shown_index or not self._range_inited:
            self._range_end = max_shown_index
            self._range_inited = True

        # ── bulk actions ──────────────────────────────────────────────────────
        action_label_suffix = f" ({self._active_pattern})" if self._active_pattern != "All" else " all"
        
        if ui.button(f"Enable{action_label_suffix}"):
            shown_names = {n for n, _ in shown}
            new_states = []
            for name, enabled in states:
                if name in shown_names:
                    lf.set_camera_training_enabled(name, True)
                    new_states.append((name, True))
                else:
                    new_states.append((name, enabled))
            self._cached_states = new_states

        ui.same_line()
        if ui.button(f"Disable{action_label_suffix}"):
            shown_names = {n for n, _ in shown}
            new_states = []
            for name, enabled in states:
                if name in shown_names:
                    lf.set_camera_training_enabled(name, False)
                    new_states.append((name, False))
                else:
                    new_states.append((name, enabled))
            self._cached_states = new_states

        ui.separator()

        # ── every-N toggle ────────────────────────────────────────────────────
        ui.label(f"Keep every Nth frame only:  N = {self._every_n}")
        if ui.button("N −"):
            self._every_n = max(2, self._every_n - 1)
        ui.same_line()
        if ui.button("N +"):
            self._every_n = min(50, self._every_n + 1)
            
        if ui.button(f"Apply: keep every {self._every_n} frame sequence"):
            shown_names = {n for n, _ in shown}
            new_states = []
            shown_idx = 0
            for name, enabled in states:
                if name in shown_names:
                    is_kept = (shown_idx % self._every_n == 0)
                    lf.set_camera_training_enabled(name, is_kept)
                    new_states.append((name, is_kept))
                    shown_idx += 1
                else:
                    new_states.append((name, enabled))
            self._cached_states = new_states

        ui.separator()

        # ── range disable ─────────────────────────────────────────────────────
        ui.label(f"Disable frame range:  From = {self._range_start}  |  To = {self._range_end}")
        
        if ui.button("From −10"):
            self._range_start = max(0, self._range_start - 10)
        ui.same_line()
        if ui.button("From −"):
            self._range_start = max(0, self._range_start - 1)
        ui.same_line()
        if ui.button("From +"):
            self._range_start = min(max_shown_index, self._range_start + 1)
        ui.same_line()
        if ui.button("From +10"):
            self._range_start = min(max_shown_index, self._range_start + 10)

        if ui.button("To −10"):
            self._range_end = max(0, self._range_end - 10)
        ui.same_line()
        if ui.button("To −"):
            self._range_end = max(0, self._range_end - 1)
        ui.same_line()
        if ui.button("To +"):
            self._range_end = min(max_shown_index, self._range_end + 1)
        ui.same_line()
        if ui.button("To +10"):
            self._range_end = min(max_shown_index, self._range_end + 10)

        if ui.button("Disable range"):
            lo = min(self._range_start, self._range_end)
            hi = max(self._range_start, self._range_end)
            shown_names = [n for n, _ in shown]
            target_names = set(shown_names[lo:hi+1])
            
            new_states = []
            for name, enabled in states:
                if name in target_names:
                    lf.set_camera_training_enabled(name, False)
                    new_states.append((name, False))
                else:
                    new_states.append((name, enabled))
            self._cached_states = new_states
            
        ui.same_line()
        if ui.button("Enable range"):
            lo = min(self._range_start, self._range_end)
            hi = max(self._range_start, self._range_end)
            shown_names = [n for n, _ in shown]
            target_names = set(shown_names[lo:hi+1])
            
            new_states = []
            for name, enabled in states:
                if name in target_names:
                    lf.set_camera_training_enabled(name, True)
                    new_states.append((name, True))
                else:
                    new_states.append((name, enabled))
            self._cached_states = new_states

        ui.separator()

        # ── save / load / open-folder buttons ────────────────────────────────
        if ui.button("Save state"):
            _save_state(states)
        ui.same_line()
        if ui.button("Load & apply saved state"):
            saved = _load_state()
            if saved:
                _apply_state(saved)
                # Update the cache directly from saved data so the UI reflects
                # the applied state immediately without a scene re-query that
                # could race against Lichtfeld flushing the changes.
                self._cached_states = [
                    (name, saved[name]) if name in saved else (name, enabled)
                    for name, enabled in self._cached_states
                ]
                lf.log.info(f"[camera_toggle] Loaded and applied {len(saved)} camera states.")
            else:
                lf.log.info("[camera_toggle] No saved state found.")
        ui.same_line()
        if ui.button("📂 Open dataset folder"):
            _open_dataset_folder()

        ui.separator()

        # ── per-camera list display ───────────────────────────────────────────
        ui.label(f"Showing {len(shown)} of {len(states)}")
        ui.separator()

        for name, enabled in shown:
            label = f"[ON]  {name}" if enabled else f"[OFF] {name}"
            if ui.button(label):
                next_state = not enabled
                lf.set_camera_training_enabled(name, next_state)
                
                new_states = []
                for n, e in states:
                    if n == name:
                        new_states.append((n, next_state))
                    else:
                        new_states.append((n, e))
                self._cached_states = new_states


# ── global lifecycle integration hooks ────────────────────────────────────────

def on_load() -> None:
    lf.register_class(MainPanel)
    lf.log.info("[camera_toggle] Panel class structure registered safely.")
    saved = _load_state()
    if saved:
        _apply_state(saved)


def on_unload() -> None:
    lf.unregister_class(MainPanel)
