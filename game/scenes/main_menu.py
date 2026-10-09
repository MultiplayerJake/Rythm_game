"""Main menu: Play, Create, Settings, Exit."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button


class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        cx, w, h, skew = theme.BASE_W // 2, 300, 58, 16
        specs = [
            ("PLAY", "primary", lambda: self._go("play")),
            ("CREATE", "normal", lambda: self._go("create")),
            ("SETTINGS", "normal", lambda: self._go("settings")),
            ("EXIT", "normal", lambda: self.game.quit()),
        ]
        self.buttons = []
        y = 236
        for label, kind, cb in specs:
            self.buttons.append(
                Button((cx - w // 2, y, w, h), label, cb, size=26,
                       kind=kind, skew=skew))
            y += h + 22
        self.selected = 0

    def _go(self, target: str) -> None:
        if target == "play":
            from .play_list import PlayListScene
            self.game.scenes.change(PlayListScene(self.game))
        elif target == "create":
            from .editor import EditorScene
            self.game.scenes.change(EditorScene(self.game))
        elif target == "settings":
            from .settings import SettingsScene
            self.game.scenes.change(SettingsScene(self.game))

    def handle_event(self, event) -> None:
        for b in self.buttons:
            if b.handle_event(event):
                return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.buttons[self.selected].on_click()
            elif event.key == pygame.K_ESCAPE:
                self.game.quit()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface) -> None:
        # gradient-ish title band
        band = pygame.Rect(theme.BASE_W // 2 - 230, 96, 460, 62)
        poly = [(band.x + 16, band.y), (band.right, band.y),
                (band.right - 16, band.bottom), (band.x, band.bottom)]
        pygame.draw.polygon(surface, theme.PURPLE, poly)
        pygame.draw.polygon(surface, theme.CYAN, poly, 2)
        theme.draw_text(surface, "RHYTHM FEST", band.centerx, band.y + 14,
                        size=34, color=theme.WHITE, align="center",
                        glow=theme.BG)

        theme.draw_text(surface, "4-KEY RHYTHM GAME", theme.BASE_W // 2, 172,
                        size=15, color=theme.DIM, align="center")

        for i, b in enumerate(self.buttons):
            if i == self.selected:
                b.hovered = True
            b.draw(surface)
            if i == self.selected:
                theme.draw_text(surface, ">", b.rect.x - 26, b.rect.y + 14,
                                size=24, color=theme.CYAN, align="center")

        theme.draw_text(surface, "Arrows / Enter or click  ·  Esc quits",
                        theme.BASE_W // 2, theme.BASE_H - 44, size=15,
                        color=theme.DIM, align="center")
