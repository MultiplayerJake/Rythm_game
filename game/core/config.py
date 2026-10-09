"""Player configuration: lane keybinds + editor stop key.

Stored in ``settings.json`` (plain JSON - keybinds are not score data).
Keybinds are stored as pygame key *names* (e.g. "d", "space") so the file
stays readable and portable. ``None`` means unbound.
"""

from __future__ import annotations

import json
import os

import pygame

SETTINGS_PATH = "settings.json"

DEFAULT_LANE_KEYS = ["d", "f", "j", "k"]
DEFAULT_EDITOR_STOP = "space"


class Config:
    def __init__(self, path: str = SETTINGS_PATH):
        self.path = path
        self.lane_keys = list(DEFAULT_LANE_KEYS)   # 4 entries, name or None
        self.editor_stop = DEFAULT_EDITOR_STOP      # name or None
        self.load()

    # ------------------------------------------------------------------ io
    def load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            lanes = data.get("lane_keys")
            if isinstance(lanes, list) and len(lanes) == 4:
                self.lane_keys = [self._valid(v) for v in lanes]
            stop = data.get("editor_stop")
            if isinstance(stop, str) or stop is None:
                self.editor_stop = self._valid(stop)
        except (OSError, ValueError):
            self.lane_keys = list(DEFAULT_LANE_KEYS)
            self.editor_stop = DEFAULT_EDITOR_STOP

    def save(self) -> None:
        payload = {"lane_keys": self.lane_keys, "editor_stop": self.editor_stop}
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
        except OSError as exc:
            print(f"[config] could not save settings: {exc}")

    @staticmethod
    def _valid(name):
        if not isinstance(name, str) or not name:
            return None
        try:
            pygame.key.key_code(name)
        except (ValueError, KeyError):
            return None
        return name

    # ------------------------------------------------------------- access
    def lane_key(self, index: int):
        """pygame key constant for a lane, or None if unbound."""
        name = self.lane_keys[index]
        if name is None:
            return None
        try:
            return pygame.key.key_code(name)
        except (ValueError, KeyError):
            return None

    def editor_stop_key(self):
        name = self.editor_stop
        if name is None:
            return None
        try:
            return pygame.key.key_code(name)
        except (ValueError, KeyError):
            return None

    @staticmethod
    def key_name(key) -> str:
        try:
            return pygame.key.name(key)
        except (ValueError, TypeError):
            return "?"

    # ------------------------------------------------------------- mutators
    def set_lane_key(self, index: int, key) -> None:
        self.lane_keys[index] = self.key_name(key)
        self.save()

    def clear_lane(self, index: int) -> None:
        self.lane_keys[index] = None
        self.save()

    def set_editor_stop(self, key) -> None:
        self.editor_stop = self.key_name(key)
        self.save()

    def clear_editor_stop(self) -> None:
        self.editor_stop = None
        self.save()

    @property
    def editor_stop_name(self) -> str:
        return self.editor_stop.upper() if self.editor_stop else "UNBOUND"
