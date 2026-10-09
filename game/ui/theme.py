"""Festival Neon theme: palette, fonts and drawing helpers.

All drawing happens on the 1280x720 design surface.
"""

from __future__ import annotations

import pygame

BASE_W, BASE_H = 1280, 720

# palette
BG = (11, 6, 22)
PANEL = (20, 13, 40)
PANEL_LIGHT = (28, 18, 54)
BORDER = (58, 42, 102)
BORDER_BRIGHT = (163, 79, 191)   # highway outline
CYAN = (0, 224, 255)
PURPLE = (123, 47, 247)
YELLOW = (255, 212, 0)
ORANGE = (255, 138, 0)
MAGENTA = (255, 94, 199)
WHITE = (255, 255, 255)
TEXT = (207, 198, 245)
DIM = (107, 95, 158)
GREEN = (123, 255, 123)
RED = (255, 94, 123)

RATING_COLORS = {
    "perfect": CYAN,
    "great": YELLOW,
    "good": GREEN,
    "miss": RED,
}

_FONT_CACHE: dict = {}


def font(size: int, bold: bool = True) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        f = pygame.font.SysFont("segoeui", size, bold=bold)
        if f is None:
            f = pygame.font.Font(None, size)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]


def draw_text(surface, text, x, y, size=24, color=WHITE, align="left",
              glow=None, bold=True):
    """Render ``text`` with optional outer glow. Returns the text rect."""
    f = font(size, bold)
    s = str(text)
    img = f.render(s, True, color)
    rect = img.get_rect()
    if align == "center":
        rect.centerx = x
    elif align == "right":
        rect.right = x
    rect.y = y
    if glow:
        g = f.render(s, True, glow)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                       (-2, -2), (2, 2), (-2, 2), (2, -2)):
            surface.blit(g, (rect.x + dx, rect.y + dy))
    surface.blit(img, rect)
    return rect


def glow_rect(surface, rect, color, radius=8, blur=True):
    """Rounded rectangle with a soft neon halo."""
    if blur:
        halo = pygame.Surface((rect.w + 24, rect.h + 24), pygame.SRCALPHA)
        pygame.draw.rect(halo, (*color, 60),
                         halo.get_rect().inflate(-8, -8), border_radius=radius + 4)
        surface.blit(halo, (rect.x - 12, rect.y - 12))
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def panel(surface, rect, fill=PANEL, border=BORDER, radius=10, width=2):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border and width:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)


def title_text(surface, text, x, y, size=40):
    return draw_text(surface, text, x, y, size=size, color=WHITE,
                     align="center", glow=PURPLE)
