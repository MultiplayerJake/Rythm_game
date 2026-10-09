"""Reusable UI widgets for the Festival Neon theme."""

from __future__ import annotations

import pygame

from . import theme


class Button:
    """Clickable button. ``kind`` is 'normal' or 'primary'; ``skew`` adds the
    Fortnite-style parallelogram slant (0 = straight)."""

    def __init__(self, rect, label, on_click=None, size=22, kind="normal",
                 skew=0, enabled=True):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.size = size
        self.kind = kind
        self.skew = skew
        self.enabled = enabled
        self.hovered = False

    def _poly(self):
        s = self.skew
        r = self.rect
        if s:
            return [(r.x + s, r.y), (r.right, r.y),
                    (r.right - s, r.bottom), (r.x, r.bottom)]
        return None

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface, hover=None, selected=False):
        """``hover`` forces the hover highlight (mouse hover drives it
        otherwise); ``selected`` only brightens the fill.

        The cyan border appears *only* while hovered - idle and merely
        keyboard-selected buttons are borderless."""
        hovered = self.hovered if hover is None else hover
        primary = self.kind == "primary"
        border = theme.CYAN if hovered else None
        fill = theme.PANEL_LIGHT if (hovered or primary or selected) else theme.PANEL
        if not self.enabled:
            border, fill = theme.BORDER, theme.PANEL

        poly = self._poly()
        if poly:
            pygame.draw.polygon(surface, fill, poly)
            if border:
                pygame.draw.polygon(surface, border, poly, 2)
        else:
            theme.panel(surface, self.rect, fill=fill, border=border)

        color = theme.WHITE if self.enabled else theme.DIM
        img = theme.font(self.size).render(self.label, True, color)
        surface.blit(img, img.get_rect(center=self.rect.center))


class IconButton:
    """Small icon button (trash bin) drawn from primitives."""

    def __init__(self, rect, on_click=None, label="DELETE"):
        self.rect = pygame.Rect(rect)
        self.on_click = on_click
        self.label = label
        self.hovered = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface):
        color = theme.MAGENTA if self.hovered else theme.DIM
        theme.panel(surface, self.rect, fill=theme.PANEL,
                    border=color, radius=6, width=2)
        # trash can: lid + body + lines
        r = self.rect
        cx, top = r.centerx, r.centery - 6
        pygame.draw.rect(surface, color, (cx - 7, top - 5, 14, 4), border_radius=1)
        pygame.draw.line(surface, color, (cx - 4, top - 7), (cx + 4, top - 7), 2)
        pygame.draw.rect(surface, color, (cx - 6, top, 12, 13), 2, border_radius=2)
        for dx in (-2, 2):
            pygame.draw.line(surface, color, (cx + dx, top + 3),
                             (cx + dx, top + 10), 1)


class TextField:
    """Single-line text input with placeholder and blinking caret."""

    def __init__(self, rect, placeholder="", text="", size=22, max_len=64):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.text = text
        self.size = size
        self.max_len = max_len
        self.active = False
        self._blink = 0.0

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inside = self.rect.collidepoint(event.pos)
            if inside:
                self.active = True
                return True
            self.active = False
            return False
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return True
            if event.unicode and event.unicode.isprintable() and len(self.text) < self.max_len:
                self.text += event.unicode
                return True
        return False

    def update(self, dt: float) -> None:
        if self.active:
            self._blink = (self._blink + dt) % 1.0

    def draw(self, surface):
        border = theme.CYAN if self.active else theme.BORDER
        theme.panel(surface, self.rect, fill=theme.PANEL, border=border)
        f = theme.font(self.size, bold=False)
        value = self.text or self.placeholder
        color = theme.WHITE if self.text else theme.DIM
        img = f.render(value, True, color)
        clip = self.rect.inflate(-16, -8)
        surface.set_clip(clip)
        surface.blit(img, (clip.x, clip.centery - img.get_height() // 2))
        if self.active and self._blink < 0.5:
            cx = clip.x + img.get_width() + 2
            pygame.draw.line(surface, theme.CYAN, (cx, clip.y + 4),
                             (cx, clip.bottom - 4), 2)
        surface.set_clip(None)
