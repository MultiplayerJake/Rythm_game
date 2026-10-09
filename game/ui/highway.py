"""HighwayView: shared 4-lane highway renderer (gameplay + editor)."""

from __future__ import annotations

import pygame

from . import theme

TRAVEL_MS = 1600.0            # fixed note travel time (top -> hit line)
HW = pygame.Rect(360, 60, 560, 420)
HIT_Y = HW.y + int(HW.h * 0.80)   # 396
LANE_PAD = 8
LANE_GAP = 5

_NOTE_H = 16
_RIBBON_W = 0.28
_CAPSULE_W = 0.66


def _get(note, key, default=None):
    if isinstance(note, dict):
        return note.get(key, default)
    return getattr(note, key, default)


class HighwayView:
    def lane_rects(self) -> list:
        inner_w = HW.w - 2 * LANE_PAD
        lw = (inner_w - 3 * LANE_GAP) / 4
        return [pygame.Rect(HW.x + LANE_PAD + i * (lw + LANE_GAP),
                            HW.y + 4, lw, HW.h - 8) for i in range(4)]

    @property
    def px_per_ms(self) -> float:
        return (HIT_Y - HW.y) / TRAVEL_MS

    def y_for(self, time_ms: float, song_pos: float) -> float:
        return HIT_Y - (time_ms - song_pos) * self.px_per_ms

    # -------------------------------------------------------------- draw
    def draw(self, surface, song_pos, notes, lane_down=None,
             labels=None, highlight_lane=None):
        theme.panel(surface, HW, fill=(16, 10, 32),
                    border=theme.BORDER_BRIGHT, radius=8, width=3)

        lanes = self.lane_rects()
        for i, lr in enumerate(lanes):
            fill = theme.PANEL if not (lane_down and lane_down[i]) else theme.PANEL_LIGHT
            pygame.draw.rect(surface, fill, lr, border_radius=5)
            if lane_down and lane_down[i]:
                pygame.draw.rect(surface, theme.CYAN, lr, 2, border_radius=5)

        prev = surface.get_clip()
        surface.set_clip(HW.inflate(0, 40))
        self._draw_notes(surface, song_pos, notes, lanes)
        surface.set_clip(prev)

        # hit line
        hl = pygame.Rect(HW.x + 2, HIT_Y - 3, HW.w - 4, 6)
        theme.glow_rect(surface, hl, theme.YELLOW, radius=3, blur=True)

        # receptors sit on the hit line
        for i, lr in enumerate(lanes):
            rec = pygame.Rect(lr.x + lr.w * (1 - _CAPSULE_W) / 2,
                              HIT_Y - _NOTE_H // 2,
                              lr.w * _CAPSULE_W, _NOTE_H)
            held = lane_down and lane_down[i]
            color = theme.CYAN if held else theme.BORDER
            pygame.draw.rect(surface, color, rec, 2, border_radius=8)

        # key labels under the highway
        if labels:
            for i, text in enumerate(labels):
                if not text:
                    continue
                cx = lanes[i].centerx
                active = lane_down and lane_down[i]
                theme.draw_text(surface, text, cx, HW.bottom + 8, size=44,
                                color=theme.WHITE if active else theme.TEXT,
                                align="center",
                                glow=theme.PURPLE if active else None)

    def _draw_notes(self, surface, song_pos, notes, lanes):
        for note in notes:
            t = _get(note, "time")
            if t is None:
                continue
            lane = int(_get(note, "lane", 0))
            if not 0 <= lane < 4:
                continue
            end = _get(note, "end")
            boost = bool(_get(note, "boost", False))
            status = _get(note, "status")

            y_head = self.y_for(t, song_pos)
            y_tail = self.y_for(end, song_pos) if end is not None else None

            # skip far-away future notes (cheap culling)
            if y_head < HW.y - 60 and (y_tail is None or y_tail < HW.y - 60):
                if t - song_pos > TRAVEL_MS + 400:
                    continue
            if y_head > HW.bottom + 80:
                continue

            lr = lanes[lane]
            cx = lr.centerx
            color = theme.YELLOW if boost else theme.CYAN

            if y_tail is not None and status not in ("hit", "missed"):
                top = min(y_head, y_tail)
                bottom = max(y_head, y_tail)
                rw = lr.w * _RIBBON_W
                ribbon = pygame.Rect(cx - rw / 2, top, rw, max(bottom - top, 2))
                pygame.draw.rect(surface, color, ribbon, border_radius=6)
                pygame.draw.rect(surface, theme.WHITE, ribbon, 1, border_radius=6)

            if status in ("hit", "missed"):
                continue

            w = lr.w * _CAPSULE_W
            cap = pygame.Rect(cx - w / 2, y_head - _NOTE_H / 2, w, _NOTE_H)
            theme.glow_rect(surface, cap, color, radius=8, blur=True)
            hi = cap.inflate(-6, -4)
            pygame.draw.rect(surface, theme.WHITE, hi, border_radius=6)


def key_labels(config) -> list:
    labels = []
    for i in range(4):
        name = config.lane_keys[i]
        labels.append(name.upper() if name else "-")
    return labels
