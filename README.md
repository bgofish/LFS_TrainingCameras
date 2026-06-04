# Cameras Plugin for Lichtfeld Studio

A panel plugin for managing camera training visibility in Lichtfeld Studio. Adds a **Cameras** tab to the main panel with tools for bulk toggling, pattern filtering, frame-range control, and persistent state saved directly into your dataset folder.

<img width="1709" height="945" alt="image" src="https://github.com/user-attachments/assets/9e6218b7-20d1-413c-b2c1-e9f91ff43620" />

Updates:

0.1.3  fixed Syncing from the scene for 'manually' diabled cameras


# Panel Sections

### Summary
Shows the total camera count with how many are currently enabled or disabled.

**Sync (Refresh List)** — re-queries the scene. Use this if cameras have been added, removed, or renamed outside the plugin.

**Save state:** saves a json file with current camera state 

**Load & Apply Save state:** reads a json file & updates current camera state

**Open Folder:** opens a file explorer at the Dataset Folder - where the Json file is saved

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
