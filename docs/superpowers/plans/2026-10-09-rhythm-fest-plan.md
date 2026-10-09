# Rhythm Fest — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-10-09-rhythm-fest-design.md`

Build order (each step leaves the app runnable):

1. **Foundation** — `game/core/`: `Scene` base, `SceneManager`, `Game` (fullscreen native window, 1280×720 base surface scaled with letterbox, mouse-coordinate conversion), `Config` (keybinds ↔ `settings.json`).
2. **Services** — `SaveSystem` (XOR-obfuscated + HMAC/SHA-256 `stats.dat`, atomic writes, tamper → `.bak` + defaults), `LevelLibrary` (scan/validate/create/sanitize), `AudioEngine` (`mixer.music.get_pos()` + monotonic fallback, end-of-song detection).
3. **Engine** — `Note`, `RhythmEngine` (injected clock; judgment windows 45/90/140 ms, combo, boost charge/activate/drain, sustain accrual, judgment event queue). Unit tests with fake clock.
4. **UI kit** — `theme.py` (Festival Neon palette, fonts, glow text, skewed panels), `widgets.py` (`Button`, `TextField`, `IconButton`), base-surface rendering helpers.
5. **Screens** — Main Menu → Play (list + gameplay) → Results → Settings → Create (setup + recording).
6. **Tests & demo content** — `tests/` (`unittest`: rhythm, save, levels), `tools/create_demo_level.py` generating a beep track + chart for smoke testing.
7. **Polish & verify** — run `python -m unittest`, smoke test every screen, commit.

Definition of done: all spec sections implemented, tests pass, game runs fullscreen and is playable end-to-end with the demo level.
