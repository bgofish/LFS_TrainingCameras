"""
LichtFeld Studio – Camera Training Toggle Plugin
"""
import lichtfeld as lf
from .panels.main_panel import MainPanel, on_load as _panel_on_load, on_unload as _panel_on_unload


def on_load() -> None:
    _panel_on_load()


def on_unload() -> None:
    _panel_on_unload()
