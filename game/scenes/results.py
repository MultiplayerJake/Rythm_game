"""End-of-round results screen."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button


class ResultsScene(Scene):
    def __init__(self, game, level, summary: dict):
        super().__init__(game)
        self.level = level
        self.summary = summary
        self.is_new_high = game.save.record_score(level.name, summary["score"])

        cy = theme.BASE_H // 2 + 130
        w, h = 240, 58
        self.again = Button((theme.BASE_W // 2 - w - 14, cy, w, h), "AGAIN",
                            self._again, size=24, kind="primary", skew=14)
        self.menu = Button((theme.BASE_W // 2 + 14, cy, w, h), "MAIN MENU",
                           self._menu, size=24, skew=14)
        self.buttons = [self.again, self.menu]
        self.selected = 0

    def _again(self) -> None:
        from .play import PlayScene
        self.game.scenes.change(PlayScene(self.game, self.level))

    def _menu(self) -> None:
        from .main_menu import MainMenuScene
        self.game.scenes.change(MainMenuScene(self.game))

    def handle_event(self, event) -> None:
        for b in self.buttons:
            if b.handle_event(event):
                return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = 1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.buttons[self.selected].on_click()
            elif event.key == pygame.K_ESCAPE:
                self._menu()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface) -> None:
        s = self.summary
        theme.title_text(surface, "TRACK COMPLETE", theme.BASE_W // 2, 96, 44)
        theme.draw_text(surface, self.level.name, theme.BASE_W // 2, 154,
                        size=18, color=theme.DIM, align="center")

        theme.draw_text(surface, f"{s['score']:,}", theme.BASE_W // 2, 206,
                        size=76, color=theme.WHITE, align="center",
                        glow=theme.PURPLE)
        if self.is_new_high:
            theme.draw_text(surface, "NEW HIGH SCORE!", theme.BASE_W // 2, 300,
                            size=22, color=theme.YELLOW, align="center",
                            glow=theme.ORANGE)
        else:
            theme.draw_text(surface,
                            f"HIGH SCORE {self.game.save.high_score(self.level.name):,}",
                            theme.BASE_W // 2, 302, size=18,
                            color=theme.DIM, align="center")

        theme.draw_text(surface, f"MAX COMBO  {s['max_combo']}",
                        theme.BASE_W // 2, 348, size=26, color=theme.CYAN,
                        align="center")

        items = [("PERFECT", s["perfect"], theme.CYAN),
                 ("GREAT", s["great"], theme.YELLOW),
                 ("GOOD", s["good"], theme.GREEN),
                 ("MISS", s["miss"], theme.RED)]
        total_w = 4 * 170
        x0 = theme.BASE_W // 2 - total_w // 2
        for i, (label, count, color) in enumerate(items):
            x = x0 + i * 170 + 85
            box = pygame.Rect(x - 74, 402, 148, 74)
            theme.panel(surface, box, fill=theme.PANEL, border=theme.BORDER)
            theme.draw_text(surface, count, x, 412, size=30, color=color,
                            align="center")
            theme.draw_text(surface, label, x, 452, size=14, color=theme.DIM,
                            align="center")

        for i, b in enumerate(self.buttons):
            b.hovered = (i == self.selected)
            b.draw(surface)

        theme.draw_text(surface, "Enter = confirm  ·  Esc = main menu",
                        theme.BASE_W // 2, theme.BASE_H - 60, size=15,
                        color=theme.DIM, align="center")
