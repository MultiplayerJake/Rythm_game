"""Play screen: level list with saved high scores."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button

ROW_X, ROW_W, ROW_H, ROW_GAP = 300, 680, 56, 10
ROW_Y0 = 168


class PlayListScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.levels = game.levels.scan()
        self.selected = 0
        self.back = Button((ROW_X, theme.BASE_H - 92, 160, 46), "BACK",
                           self._back, size=20)

    def _back(self) -> None:
        from .main_menu import MainMenuScene
        self.game.scenes.change(MainMenuScene(self.game))

    def _launch(self, info) -> None:
        if not info.valid:
            return
        from .play import PlayScene
        self.game.scenes.change(PlayScene(self.game, info))

    def handle_event(self, event) -> None:
        if self.back.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, info in enumerate(self.levels):
                rect = self._row_rect(i)
                if rect.collidepoint(event.pos):
                    self.selected = i
                    if info.valid:
                        self._launch(info)
                    return
        elif event.type == pygame.KEYDOWN:
            cfg = self.game.config
            if event.key == cfg.key("cancel"):
                self._back()
            elif event.key == cfg.key("menu_up"):
                self.selected = max(0, self.selected - 1)
            elif event.key == cfg.key("menu_down"):
                self.selected = min(max(len(self.levels) - 1, 0), self.selected + 1)
            elif (event.key == cfg.key("confirm")
                  or event.key == pygame.K_KP_ENTER):
                if self.levels:
                    self._launch(self.levels[self.selected])

    @staticmethod
    def _row_rect(i: int) -> pygame.Rect:
        return pygame.Rect(ROW_X, ROW_Y0 + i * (ROW_H + ROW_GAP), ROW_W, ROW_H)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface) -> None:
        theme.title_text(surface, "SELECT TRACK", theme.BASE_W // 2, 62, size=40)

        if not self.levels:
            theme.draw_text(surface, "No levels yet.",
                            theme.BASE_W // 2, 280, size=26,
                            color=theme.TEXT, align="center")
            theme.draw_text(surface, "Use CREATE in the main menu to add a song.",
                            theme.BASE_W // 2, 320, size=18,
                            color=theme.DIM, align="center")
            self.back.draw(surface)
            return

        for i, info in enumerate(self.levels):
            rect = self._row_rect(i)
            active = i == self.selected
            border = theme.CYAN if active else theme.BORDER
            fill = theme.PANEL_LIGHT if active else theme.PANEL
            if not info.valid:
                border = theme.BORDER
                fill = theme.PANEL
            theme.panel(surface, rect, fill=fill, border=border, radius=6)

            name_color = theme.WHITE if info.valid else theme.DIM
            theme.draw_text(surface, info.name, rect.x + 18, rect.y + 15,
                            size=22, color=name_color)
            if not info.valid:
                theme.draw_text(surface, f"BROKEN: {info.error}",
                                rect.x + 200, rect.y + 19, size=14,
                                color=theme.RED)
                continue

            high = self.game.save.high_score(info.name)
            theme.draw_text(surface, f"HI {high:,}", rect.right - 18,
                            rect.y + 17, size=20, color=theme.YELLOW,
                            align="right")

        cfg = self.game.config
        theme.draw_text(surface,
                        f"{cfg.label('confirm')} = play  ·  "
                        f"{cfg.label('cancel')} = back  ·  "
                        f"{len(self.levels)} level(s)",
                        theme.BASE_W // 2, theme.BASE_H - 150, size=16,
                        color=theme.DIM, align="center")
        self.back.draw(surface)
