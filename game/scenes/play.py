"""Gameplay screen: highway, input, HUD, boost meter, round end."""

from __future__ import annotations

import pygame

from ..core.scene import Scene
from ..engine.rhythm import RhythmEngine
from ..ui import theme
from ..ui.highway import HW, HIT_Y, HighwayView, key_labels

POPUP_LIFE = 0.55
END_LINGER = 1.6


class PlayScene(Scene):
    def __init__(self, game, level):
        super().__init__(game)
        self.level = level
        self.engine = RhythmEngine(level.notes, game.audio.position_ms)
        self.highway = HighwayView()
        self.popups = []          # [text, color, life]
        self.error = None
        self._end_timer = 0.0

        try:
            game.audio.play(level.audio_path)
        except pygame.error as exc:
            self.error = f"Could not play audio: {exc}"

    # ------------------------------------------------------------- input
    def _lane_map(self) -> dict:
        mapping = {}
        for i in range(4):
            key = self.game.config.lane_key(i)
            if key is not None:
                mapping[key] = i
        return mapping

    def handle_event(self, event) -> None:
        if self.error:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._to_list()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._to_list()
                return
            lanes = self._lane_map()
            if event.key in lanes:
                self.engine.press_lane(lanes[event.key])
            elif event.key == pygame.K_SPACE:
                self.engine.press_boost()
        elif event.type == pygame.KEYUP:
            lanes = self._lane_map()
            if event.key in lanes:
                self.engine.release_lane(lanes[event.key])

    def _to_list(self) -> None:
        self.game.audio.stop()
        from .play_list import PlayListScene
        self.game.scenes.change(PlayListScene(self.game))

    # ------------------------------------------------------------ update
    def update(self, dt: float) -> None:
        if self.error:
            self._end_timer += dt
            if self._end_timer > 3.0:
                self._to_list()
            return

        self.engine.update(dt)

        for judgment in self.engine.pop_judgments():
            color = theme.RATING_COLORS[judgment.rating]
            text = judgment.rating.upper()
            if judgment.rating != "miss" and judgment.offset is not None:
                ms = abs(judgment.offset)
                text = f"{text}  {ms:.0f}ms"
            self.popups.append([text, color, POPUP_LIFE])

        for popup in self.popups:
            popup[2] -= dt
        self.popups = [p for p in self.popups if p[2] > 0]

        if self.game.audio.finished:
            self._end_timer += dt
            if self._end_timer >= END_LINGER:
                self._finish()

    def _finish(self) -> None:
        summary = self.engine.summary()
        from .results import ResultsScene
        self.game.scenes.change(ResultsScene(self.game, self.level, summary))

    # -------------------------------------------------------------- draw
    def draw(self, surface) -> None:
        if self.error:
            theme.title_text(surface, "AUDIO ERROR", theme.BASE_W // 2, 240, 36)
            theme.draw_text(surface, self.error, theme.BASE_W // 2, 320, 18,
                            color=theme.RED, align="center")
            return

        song_pos = self.game.audio.position_ms()
        cfg = self.game.config
        self.highway.draw(surface, song_pos, self.engine.notes,
                          lane_down=self.engine.lane_states,
                          labels=key_labels(cfg))

        self._draw_hud(surface)
        self._draw_boost(surface)
        self._draw_popups(surface)

        theme.draw_text(surface, self.level.name, HW.centerx, 18, size=18,
                        color=theme.DIM, align="center")
        theme.draw_text(surface, "Esc = quit to menu", theme.BASE_W - 24, 18,
                        size=14, color=theme.DIM, align="right")

    def _draw_hud(self, surface) -> None:
        box = pygame.Rect(180, HIT_Y - 34, 175, 68)
        theme.panel(surface, box, fill=theme.PANEL, border=theme.BORDER)
        e = self.engine
        theme.draw_text(surface, f"{e.score_display:,}", box.x + 12, box.y + 8,
                        size=26, color=theme.WHITE)
        theme.draw_text(surface, f"x{e.combo}", box.right - 12, box.y + 8,
                        size=26, color=theme.CYAN, align="right")
        theme.draw_text(surface, "SCORE", box.x + 14, box.y + 44, size=12,
                        color=theme.DIM)
        theme.draw_text(surface, "COMBO", box.right - 14, box.y + 44, size=12,
                        color=theme.DIM, align="right")

    def _draw_boost(self, surface) -> None:
        bar = pygame.Rect(440, 566, 400, 26)
        theme.panel(surface, bar, fill=theme.PANEL, border=theme.BORDER,
                    radius=13, width=2)
        frac = self.engine.boost_charge / 100.0
        if frac > 0:
            fill_rect = pygame.Rect(bar.x + 3, bar.y + 3,
                                    int((bar.w - 6) * frac), bar.h - 6)
            color = theme.ORANGE if self.engine.boost_active else theme.YELLOW
            pygame.draw.rect(surface, color, fill_rect, border_radius=10)
        label_color = theme.YELLOW if self.engine.boost_active else theme.DIM
        theme.draw_text(surface,
                        "BOOST" + ("  ON  2x" if self.engine.boost_active else ""),
                        bar.centerx, bar.bottom + 8, size=15, color=label_color,
                        align="center")
        theme.draw_text(surface, "SPACE", bar.x - 16, bar.y + 4, size=14,
                        color=theme.DIM, align="right")

    def _draw_popups(self, surface) -> None:
        if not self.popups:
            return
        text, color, life = max(self.popups, key=lambda p: p[2])
        alpha = int(255 * min(1.0, life / POPUP_LIFE * 1.6))
        f = theme.font(34)
        img = f.render(text, True, color)
        img.set_alpha(alpha)
        rect = img.get_rect(midbottom=(HW.centerx, HIT_Y - 130))
        halo = f.render(text, True, theme.WHITE)
        halo.set_alpha(alpha // 3)
        surface.blit(halo, rect.move(0, 0))
        surface.blit(img, rect)
