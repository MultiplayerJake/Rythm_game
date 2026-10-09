"""Settings: rebind any shortcut, with a scrollable list.

Every shortcut in the game is an action defined in
``game/core/config.py`` (``DEFAULT_KEYS`` / ``GROUPS``); this screen
lists them all, grouped, and scrolls when they do not fit on one screen.
"""

from __future__ import annotations

import pygame

from ..core.config import GROUPS, LABELS
from ..core.scene import Scene
from ..ui import theme
from ..ui.widgets import Button, IconButton

VIEW = pygame.Rect(180, 110, 920, 420)
ROW_H, ROW_GAP = 44, 8
HEAD_H, HEAD_GAP = 30, 6
KEY_W = 150
SCROLL_STEP = 56


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.waiting = None        # action name waiting for a key, else None
        self.focus = 0             # index into self.actions
        self.hover = None          # action name under the mouse
        self.scroll = 0.0
        self._layout()

        self.back = Button((theme.BASE_W // 2 - 80, theme.BASE_H - 102, 160, 46),
                           "BACK", self._back, size=20)

    # ------------------------------------------------------------- layout
    def _layout(self) -> None:
        """Build content-space rows: group headers + one row per action."""
        self.entries = []          # {"kind", "title"/"action", "y", "h"}
        self.actions = []          # bindable action names, display order
        y = 0
        for title, actions in GROUPS:
            self.entries.append({"kind": "head", "title": title,
                                 "y": y, "h": HEAD_H})
            y += HEAD_H + HEAD_GAP
            for action in actions:
                self.entries.append({"kind": "row", "action": action,
                                     "y": y, "h": ROW_H})
                self.actions.append(action)
                y += ROW_H + ROW_GAP
            y += 10
        self.content_h = y

    def _max_scroll(self) -> float:
        return max(0.0, self.content_h - VIEW.h)

    def _clamp(self) -> None:
        self.scroll = max(0.0, min(self.scroll, self._max_scroll()))

    def _scroll_into_view(self, entry) -> None:
        top = entry["y"] - self.scroll
        bottom = top + entry["h"]
        if top < 0:
            self.scroll = entry["y"]
        elif bottom > VIEW.h:
            self.scroll = entry["y"] + entry["h"] - VIEW.h
        self._clamp()

    def _screen_rect(self, entry) -> pygame.Rect:
        return pygame.Rect(VIEW.x, VIEW.y + entry["y"] - self.scroll,
                           VIEW.w - 18, entry["h"])

    # ------------------------------------------------------------- actions
    def _start_wait(self, action: str) -> None:
        self.waiting = action

    def _back(self) -> None:
        from .main_menu import MainMenuScene
        self.game.scenes.change(MainMenuScene(self.game))

    # -------------------------------------------------------------- events
    def handle_event(self, event) -> None:
        cfg = self.game.config

        if self.waiting is not None:
            if event.type == pygame.KEYDOWN:
                cfg.set_key(self.waiting, event.key)
                self.waiting = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # clicking anywhere else abandons the rebind
                self.waiting = None
                self.handle_event(event)
            return

        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * SCROLL_STEP
            self._clamp()
            return

        if event.type == pygame.MOUSEMOTION:
            self.hover = self._action_at(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back.handle_event(event):
                return
            action = self._action_at(event.pos)
            if action is None:
                return
            rect = self._row_rect(action)
            key_rect, trash_rect = self._controls(rect)
            if trash_rect.collidepoint(event.pos):
                cfg.clear_key(action)
            elif key_rect.collidepoint(event.pos):
                self._start_wait(action)
            else:
                self.focus = self.actions.index(action)
                self._start_wait(action)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == cfg.key("cancel"):
                self._back()
            elif event.key == cfg.key("menu_up"):
                self.focus = max(0, self.focus - 1)
                self._scroll_into_view(self._entry(self.actions[self.focus]))
            elif event.key == cfg.key("menu_down"):
                self.focus = min(len(self.actions) - 1, self.focus + 1)
                self._scroll_into_view(self._entry(self.actions[self.focus]))
            elif (event.key == cfg.key("confirm")
                  or event.key == pygame.K_KP_ENTER):
                self._start_wait(self.actions[self.focus])

    def _entry(self, action: str) -> dict:
        for entry in self.entries:
            if entry["kind"] == "row" and entry["action"] == action:
                return entry
        return self.entries[0]

    def _action_at(self, pos) -> str | None:
        for entry in self.entries:
            if entry["kind"] != "row":
                continue
            if self._screen_rect(entry).collidepoint(pos):
                return entry["action"]
        return None

    def _row_rect(self, action: str) -> pygame.Rect:
        return self._screen_rect(self._entry(action))

    @staticmethod
    def _controls(row: pygame.Rect):
        key = pygame.Rect(row.right - KEY_W - 52, row.y + 4, KEY_W, ROW_H - 8)
        trash = pygame.Rect(row.right - 44, row.y + 4, ROW_H - 8, ROW_H - 8)
        return key, trash

    # -------------------------------------------------------------- update
    def update(self, dt: float) -> None:
        pass

    # ---------------------------------------------------------------- draw
    def draw(self, surface) -> None:
        theme.title_text(surface, "SETTINGS", theme.BASE_W // 2, 44, 38)

        cfg = self.game.config
        prev = surface.get_clip()
        surface.set_clip(VIEW)
        for entry in self.entries:
            y = VIEW.y + entry["y"] - self.scroll
            if y > VIEW.bottom or y + entry["h"] < VIEW.y:
                continue
            if entry["kind"] == "head":
                theme.draw_text(surface, entry["title"], VIEW.x + 4, y + 4,
                                size=16, color=theme.MAGENTA)
                pygame.draw.line(surface, theme.BORDER,
                                 (VIEW.x + 110, y + 14), (VIEW.right - 24, y + 14))
                continue
            self._draw_row(surface, entry, y, cfg)
        surface.set_clip(prev)

        self._draw_scrollbar(surface)
        self.back.draw(surface)

        if self.waiting:
            theme.draw_text(surface,
                            "Press any key to bind it  ·  click elsewhere "
                            "to cancel",
                            theme.BASE_W // 2, VIEW.bottom + 14, 16,
                            color=theme.YELLOW, align="center")
        else:
            theme.draw_text(surface,
                            "Click a shortcut, then press a key  ·  wheel / "
                            "arrow keys scroll  ·  trash clears",
                            theme.BASE_W // 2, VIEW.bottom + 14, 16,
                            color=theme.DIM, align="center")
        theme.draw_text(surface,
                        f"{cfg.label('cancel')} = main menu  ·  "
                        f"{cfg.label('boost')} = boost during a song",
                        theme.BASE_W // 2, VIEW.bottom + 40, 16,
                        color=theme.DIM, align="center")

    def _draw_row(self, surface, entry, y: int, cfg) -> None:
        action = entry["action"]
        row = pygame.Rect(VIEW.x, y, VIEW.w - 18, ROW_H)
        active = (action == self.focus_action()
                  or action == self.hover or action == self.waiting)
        fill = theme.PANEL_LIGHT if active else theme.PANEL
        border = theme.CYAN if action == self.waiting else theme.BORDER
        theme.panel(surface, row, fill=fill, border=border, radius=6)
        if action == self.focus_action():
            pygame.draw.rect(surface, theme.CYAN, row, 1, border_radius=6)

        theme.draw_text(surface, LABELS.get(action, action), row.x + 16,
                        row.y + 12, size=20, color=theme.TEXT)

        key_rect, trash_rect = self._controls(row)
        waiting = action == self.waiting
        key_fill = theme.PANEL_LIGHT if waiting else theme.PANEL
        theme.panel(surface, key_rect, fill=key_fill,
                    border=theme.YELLOW if waiting else theme.BORDER,
                    radius=6)
        theme.draw_text(surface,
                        "PRESS A KEY..." if waiting else cfg.label(action),
                        key_rect.centerx, key_rect.y + 12,
                        size=17, color=theme.YELLOW if waiting else theme.WHITE,
                        align="center")

        tb = IconButton(trash_rect, lambda: None)
        tb.hovered = self.hover == action
        tb.draw(surface)

    def focus_action(self) -> str:
        return self.actions[self.focus] if self.actions else ""

    def _draw_scrollbar(self, surface) -> None:
        if self._max_scroll() <= 0:
            return
        track = pygame.Rect(VIEW.right - 12, VIEW.y + 2, 8, VIEW.h - 4)
        pygame.draw.rect(surface, theme.BORDER, track, border_radius=4)
        thumb_h = max(28, int(track.h * VIEW.h / self.content_h))
        frac = self.scroll / self._max_scroll()
        thumb_y = track.y + int((track.h - thumb_h) * frac)
        pygame.draw.rect(surface, theme.MAGENTA,
                         pygame.Rect(track.x, thumb_y, track.w, thumb_h),
                         border_radius=4)
