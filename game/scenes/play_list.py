"""Play screen: level list with saved high scores."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button

ROW_X, ROW_W, ROW_H, ROW_GAP = 300, 680, 56, 10
ROW_Y0 = 168

# display-only difficulty rating derived from note density
_DIFF_BANDS = ((2.5, "EASY", theme.GREEN),
               (4.0, "NORMAL", theme.CYAN),
               (6.0, "HARD", theme.YELLOW),
               (float("inf"), "EXPERT", theme.MAGENTA))


def difficulty(info):
    notes = info.notes or []
    if not notes:
        return "EASY", theme.GREEN
    dur = info.end or max((n.get("end") or n.get("time")) for n in notes)
    nps = len(notes) / max(dur / 1000.0, 1.0)
    for limit, name, color in _DIFF_BANDS:
        if nps < limit:
            return name, color
    return "EXPERT", theme.MAGENTA


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
        theme.title_text(surface, "SELECT TRACK", theme.BASE_W // 2, 54,
                         size=44, glow=theme.MAGENTA)
        theme.draw_text(surface, "— CHOOSE YOUR ARENA —",
                        theme.BASE_W // 2, 110, size=15,
                        color=theme.LAVENDER, align="center")

        if not self.levels:
            theme.draw_text(surface, "No levels yet.",
                            theme.BASE_W // 2, 280, size=26,
                            color=theme.TEXT, align="center")
            theme.draw_text(surface, "Use CREATE in the main menu to add a song.",
                            theme.BASE_W // 2, 320, size=18,
                            color=theme.DIM, align="center")
            self.back.draw(surface)
            return

        import math
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 400.0)
        for i, info in enumerate(self.levels):
            rect = self._row_rect(i)
            active = i == self.selected
            valid = info.valid
            accent = theme.CYAN if valid else theme.RED

            if active and valid:
                theme.alpha_rect(surface, rect.inflate(14, 10), theme.MAGENTA,
                                 int(45 + 40 * pulse), radius=12)
            fill = theme.PANEL_LIGHT if (active and valid) else theme.PANEL
            border = (theme.CYAN if valid else theme.BORDER) if active \
                else theme.BORDER
            theme.panel(surface, rect, fill=fill, border=border, radius=8,
                        glow=accent if active else None)
            # left accent bar
            theme.alpha_rect(surface, pygame.Rect(rect.x + 4, rect.y + 6, 5,
                                                  rect.h - 12),
                             accent, 255, radius=3)

            name_color = theme.WHITE if valid else theme.DIM
            theme.draw_text(surface, info.name, rect.x + 22, rect.y + 15,
                            size=22, color=name_color,
                            glow=theme.VIOLET if active and valid else None)
            if not valid:
                theme.draw_text(surface, f"BROKEN: {info.error}",
                                rect.x + 220, rect.y + 20, size=14,
                                color=theme.RED)
                continue

            # difficulty badge + high score
            label, color = difficulty(info)
            badge = pygame.Rect(rect.right - 262, rect.y + 13, 96, 30)
            theme.panel(surface, badge, fill=(18, 12, 40), border=color,
                        radius=8)
            theme.draw_text(surface, label, badge.centerx, badge.y + 6,
                            size=15, color=color, align="center")

            high = self.game.save.high_score(info.name)
            if high:
                theme.draw_text(surface, "HIGH SCORE", rect.right - 18,
                                rect.y + 7, size=13, color=theme.LAVENDER,
                                align="right")
                theme.draw_text(surface, f"{high:,}", rect.right - 18,
                                rect.y + 23, size=21, color=theme.YELLOW,
                                align="right")

            if active:
                theme.draw_text(surface, "▶", rect.x - 40, rect.y + 14,
                                size=22, color=theme.WHITE, align="center",
                                glow=theme.CYAN)

        theme.draw_text(surface,
                        f"{self.game.config.label('confirm')} = play  ·  "
                        f"{self.game.config.label('cancel')} = back  ·  "
                        f"{len(self.levels)} level(s)",
                        theme.BASE_W // 2, theme.BASE_H - 150, size=16,
                        color=theme.DIM, align="center")
        self.back.draw(surface)
