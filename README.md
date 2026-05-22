# Cameras Plugin for Lichtfeld Studio

A panel plugin for managing camera training visibility in Lichtfeld Studio. Adds a **Cameras** tab to the main panel with tools for bulk toggling, pattern filtering, frame-range control, and persistent state saved directly into your dataset folder.

<img width="1887" height="942" alt="image" src="https://github.com/user-attachments/assets/792164b0-c2e9-4587-ac36-81bae60cd77f" />

# Panel Sections

### Summary
Shows the total camera count with how many are currently enabled or disabled.

**🔄 Sync/Refresh List** — re-queries the scene. Use this if cameras have been added, removed, or renamed outside the plugin.

---

### Frustum Scale
Adjusts the visual display size of camera frustum cones in the viewport. Reads the current value from Lichtfeld on panel open.

| Button | Step |
|--------|------|
| ◀◀ / ▶▶ | ±0.10 |
| ◀ / ▶ | ±0.01 |
| Reset | 0.25 (API default) |

Range: 0.01 – 10.0

---

### Text Filter
Automatically detects repeating name fragments across your camera list (e.g. `cam`, `left`, `outdoor`) and presents them as one-click filter buttons. Up to 12 patterns are shown.

- **Show All** — clears the active filter
- Clicking a pattern button filters the camera list and all bulk actions to that subset

---

### Bulk Actions
Operates on the currently filtered set of cameras.

- **Enable (filter)** / **Disable (filter)** — sets all visible cameras on or off in one click

---

### Every N Frames
Keeps only every Nth camera in the filtered list enabled, disabling the rest. Useful for thinning dense frame sequences for training.

- **N − / N +** — adjust N (range 2–50)
- **Apply: keep every N frame sequence** — applies the pattern to the current filter

---

### Frame Range
Enables or disables a contiguous index range within the filtered camera list.

- **From / To** — index of the first and last camera in the range (within the filtered view)
- Step buttons: ±1 and ±10
- **Disable range** / **Enable range** — applies to cameras at indices From through To inclusive

---

### Save / Load / Open

| Button | Action |
|--------|--------|
| **Save state** | Writes current ON/OFF state for all cameras to `camera_states.json` in the dataset folder |
| **Load & apply saved state** | Reads `camera_states.json` and applies it; updates the UI immediately without a scene re-query |
| **📂 Open dataset folder** | Opens the dataset folder in your OS file manager  |

The save file path is resolved dynamically from `lf.dataset_params().data_path`, so it always lands next to your currently loaded dataset (e.g. `U:\LFS\DATASETS\Twins\camera_states.json`). Falls back to `~/.lichtfeld/plugins/Cameras/` if no dataset is loaded.

---

### Camera List
Shows every camera in the filtered set with its current state. Click any camera to toggle it individually.

```
[ON]  frame_0001
[OFF] frame_0002
[ON]  frame_0003
```

---

## State File Format

`camera_states.json` is a plain JSON object mapping camera names to booleans:

```json
{
  "frame_0001": true,
  "frame_0002": false,
  "frame_0003": true
}
```

The file is human-readable and can be edited manually or committed to version control alongside your dataset.

---

## API Surface Used

| Call | Purpose |
|------|---------|
| `lf.list_scene()` | Enumerate cameras and their training state |
| `lf.set_camera_training_enabled(name, bool)` | Toggle individual cameras |
| `lf.dataset_params().data_path` | Resolve the active dataset folder |
| `lf.get_render_settings().camera_frustum_scale` | Read/write frustum display size |
| `lf.has_scene()` | Guard against drawing with no scene loaded |

---

## Notes

- The camera list is cached between draws for performance. Use **🔄 Sync/Refresh List** if the scene changes externally.
- **Load & apply** updates the UI cache directly rather than triggering a scene re-query, avoiding a race condition where Lichtfeld hadn't flushed changes before the next draw.
- The plugin requires `plugin_api >= 1, < 2` and `lichtfeld >= 0.5.0`.
