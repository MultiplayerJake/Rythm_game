"""Settings: key rebinding (4 lanes + editor stop) with trash buttons."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button, IconButton

ROW_Y0, ROW_H, ROW_GAP = 172, 52, 18


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.waiting = None   # None | 0..3 | "editor_stop"
        self.rows = []        # (label, key_button, trash_button)

        y = ROW_Y0
        for i in range(4):
            self._add_row(f"LANE {i + 1}", y,
                          on_key=lambda idx=i: self._start_wait(idx),
                          on_trash=lambda idx=i: self._clear_lane(idx),
                          key_rect=(556, y, 168, ROW_H),
                          trash_rect=(736, y, ROW_H, ROW_H))
            y += ROW_H + ROW_GAP
        self._add_row("EDITOR STOP", y,
                      on_key=lambda: self._start_wait("editor_stop"),
                      on_trash=lambda: self._clear_stop(),
                      key_rect=(556, y, 168, ROW_H),
                      trash_rect=(736, y, ROW_H, ROW_H))

        self.back = Button((theme.BASE_W // 2 - 80, theme.BASE_H - 112, 160, 46),
                           "BACK", self._back, size=20)

    def _add_row(self, label, y, on_key, on_trash, key_rect, trash_rect):
        kb = Button(key_rect, "", on_key, size=22)
        tb = IconButton(trash_rect, on_trash)
        self.rows.append((label, kb, tb))

    # ------------------------------------------------------------- actions
    def _start_wait(self, target) -> None:
        self.waiting = target

    def _clear_lane(self, index: int) -> None:
        self.game.config.clear_lane(index)

    def _clear_stop(self) -> None:
        self.game.config.clear_editor_stop()

    def _back(self) -> None:
        from .main_menu import MainMenuScene
        self.game.scenes.change(MainMenuScene(self.game))

    # -------------------------------------------------------------- events
    def handle_event(self, event) -> None:
        if self.waiting is not None:
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    if self.waiting == "editor_stop":
                        self.game.config.set_editor_stop(event.key)
                    else:
                        self.game.config.set_lane_key(self.waiting, event.key)
                self.waiting = None
            return

        for _label, kb, tb in self.rows:
            if kb.handle_event(event) or tb.handle_event(event):
                return
        if self.back.handle_event(event):
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()

    def update(self, dt: float) -> None:
        pass

    def _key_label(self, index) -> str:
        if self.waiting == index:
            return "PRESS A KEY..."
        if index == "editor_stop":
            return self.game.config.editor_stop_name
        name = self.game.config.lane_keys[index]
        return name.upper() if name else "UNBOUND"

    def draw(self, surface) -> None:
        theme.title_text(surface, "SETTINGS", theme.BASE_W // 2, 64, 40)

        for i, (label, kb, tb) in enumerate(self.rows):
            index = i if i < 4 else "editor_stop"
            theme.draw_text(surface, label, 530, ROW_Y0 + i * (ROW_H + ROW_GAP) + 15,
                            size=22, color=theme.TEXT, align="right")
            kb.label = self._key_label(index)
            if self.waiting == index:
                kb.enabled = True
                pygame.draw.rect(surface, theme.YELLOW, kb.rect, 2,
                                 border_radius=8)
            kb.draw(surface)
            tb.draw(surface)

        hint = ("Click a key, then press any key to rebind  ·  "
                "trash clears a binding")
        theme.draw_text(surface, hint, theme.BASE_W // 2, 540, size=16,
                        color=theme.DIM, align="center")
        theme.draw_text(surface,
                        "Esc = main menu  ·  Space = boost during a song  ·  "
                        "Editor stop ends recording",
                        theme.BASE_W // 2, 570, size=16,
                        color=theme.DIM, align="center")
        self.back.draw(surface)
