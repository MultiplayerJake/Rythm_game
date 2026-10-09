# AGENTS.md

Pygame 4-key rhythm game ("Rhythm Fest"). Python 3.12, pygame 2.6.1, no build system — plain scripts.

## Commands

```powershell
python main.py                       # play (must run from repo root)
python -m unittest discover -s tests # 24 tests, ~0.1s
python tools/create_demo_level.py    # (re)generate the Demo_Beat level
python -m pip install -r requirements.txt
```

- **pygame must be installed in the exact interpreter you run with.** It lives in
  user site-packages (`%APPDATA%\Roaming\Python\Python312\site-packages`).
  A `ModuleNotFoundError: No module named 'pygame'` means a different `python.exe`
  is running (Store Python, venv, other version) — reinstall there, don't chase code.
- No lint / typecheck / formatter is configured. `python -m py_compile` on changed
  files + the unittest run is the verification bar.

## Gotchas that bite

- **cwd-relative paths**: `music_levels/`, `stats.dat`, `settings.json` are all opened
  relative to the process cwd. Always launch from the repo root or files appear
  to vanish (and duplicate levels get created elsewhere).
- **Borderless windowed fullscreen, no windowed mode.** The screen is a NOFRAME
  window at native desktop size (chosen so file dialogs / alt-tab don't minimize
  the game). All rendering happens on a fixed
  1280x720 base surface (`theme.BASE_W/BASE_H`) that is smoothscaled + letterboxed
  onto the desktop resolution in `game/core/app.py`, which also converts mouse
  events back into design-space coords. Author every layout in 1280x720 space; never
  read `event.pos` raw.
- **Headless testing**: set `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`
  *before* importing pygame (smoke scripts must also set `PYTHONPATH` to the repo
  root — running a script from `%TEMP%` won't find the `game` package).
- Tampered/corrupt `stats.dat` is silently renamed `stats.dat.bak` and reset to
  defaults (intentional; `tests/test_save.py` covers it). `stats.dat`, `settings.json`
  and `.superpowers/` are gitignored — never commit them.

## Architecture

- `game/engine/` is **pygame-free on purpose** — `RhythmEngine(notes, clock)` takes an
  injected millisecond clock, which is what makes unit tests possible. Keep engine and
  `save_system.py` / `levels.py` free of pygame imports; only `audio.py`, scenes, core
  and ui import it.
- Scene stack: `game/core/scene_manager.py` holds a list; each `Scene(game)` in
  `game/scenes/` implements `handle_event/update/draw` and talks to services via
  `game` (`game.config`, `game.save`, `game.levels`, `game.audio`).
- Services are plain singletons owned by `Game` (`game/core/app.py`): `SaveSystem`
  (XOR+HMAC encrypted high scores), `LevelLibrary` (JSON charts), `AudioEngine`
  (song position via `mixer.music.get_pos()` + monotonic fallback).
- Level files: `music_levels/<name>.json` with
  `{"name", "audio", "end": ms|null (stop point, None = whole track), "notes":
  [{lane 0-3, time ms, end ms|None, boost bool}]}`; audio is
  `music_<name>.<ext>` in the same folder.

## Gameplay constants

Source of truth is `docs/superpowers/specs/2026-10-09-rhythm-fest-design.md`
(approved) — judgment windows (±45 Perfect / ±90 Great / ±140 Good), scoring,
boost rules (charge 0-100, +20/note, `Space`, 2x, drains 20/s), fixed 1.6s note
travel. Change behavior there first, then in code.

**Every shortcut is a rebindable action** (`game/core/config.py`:
`DEFAULT_KEYS` + `GROUPS`), persisted to `settings.json` and edited in the
scrollable Settings screen. Actions: `lane_0..3`, `boost`, `editor_stop`,
`editor_undo`, `menu_up/down/left/right`, `confirm`, `cancel`. Scenes must
read shortcuts via `game.config.key(action)` / `label(action)` — never
hardcode `K_ESCAPE`/`K_SPACE` etc. Legacy `{"lane_keys": [...],
"editor_stop": ...}` files are migrated on load.
