# Rhythm Fest

A 4-key neon rhythm game built with **Python + pygame**, styled after *Fortnite Festival*.
Hit falling notes on a centered note highway, charge the **boost meter** for double
points, and chart your own songs with the built-in level editor. No fail state — a run
always plays to the end of the track.

---

## Gameplay

<!-- ▸▸ REPLACE THE COMMENTED BLOCK BELOW WITH YOUR VIDEO ◂◂
     Uncomment ONE of the two options and drop in your file/link.
     Until then it stays hidden, so the README renders cleanly. -->

<!--
### Option A — video file in the repo (e.g. docs/media/gameplay.mp4)

<video src="docs/media/gameplay.mp4" width="720" controls></video>

### Option B — YouTube / external link

[![Rhythm Fest gameplay](https://img.shields.io/badge/watch-gameplay_video-7b2ff7?style=for-the-square)](YOUR_VIDEO_URL_HERE)
![Rhythm Fest gameplay](docs/media/gameplay_thumbnail.png)
-->

*Gameplay video coming soon.*

---

## Features

- **Note highway** — fixed 1.6 s note travel, frame-rate independent, locked to the music clock.
- **Four judgment tiers** — Perfect / Great / Good / Miss with combo tracking.
- **Hold notes** — keep the key down to accrue points across the sustain.
- **Boost meter** — hit yellow boost notes to charge it, press **Space** to double all gains for ~5 s.
- **No fail state** — no health bar; play to the end and chase a high score.
- **Level editor** — import any `.mp3`/`.wav`, tap out a chart in real time, save and play it.
- **Encrypted high scores** — `stats.dat` is XOR-obfuscated + HMAC-signed; tampering is detected and reset safely.
- **Rebindable controls** — every shortcut is remappable from the in-game Settings screen.
- **Borderless fullscreen** — renders on a 1280×720 design surface, letterboxed to any monitor.

---

## Quick start (players)

**Easiest:** grab `dist\Rhythm Fest.exe` from a release (built with PyInstaller) and keep it
next to the `music_levels\` folder that ships beside it. Double-click to play.

**From source:**

```powershell
python -m pip install -r requirements.txt
python main.py          # must run from the repo root
```

> **Run from the repo root.** The game opens `music_levels/`, `stats.dat` and
> `settings.json` relative to the current working directory — launching from elsewhere
> makes files appear to vanish.

---

## Requirements

- **Python 3.12**
- **pygame 2.6.1** (`requirements.txt`)

pygame must be installed for the *same* interpreter you run with (it lives in user
site-packages). A `ModuleNotFoundError: No module named 'pygame'` means a different
`python.exe` is running — reinstall there.

---

## For developers

```powershell
python -m pip install -r requirements.txt    # runtime deps
python -m unittest discover -s tests         # 33 tests, ~0.1s
python tools/create_demo_level.py            # (re)generate the Demo_Beat level
```

To build the standalone exe (adds `pyinstaller` via `requirements-dev.txt`):

```powershell
python -m pip install -r requirements-dev.txt
powershell -File tools\package.ps1           # -> dist\Rhythm Fest.exe
```

There is no lint/typecheck/CI configured — the verification bar is
`python -m py_compile <changed files>` plus the unittest run.

### Project layout

```
Rythm_game/
├── main.py                  # boots Game()
├── game/
│   ├── core/                # app (window/loop), scene stack, config
│   ├── engine/              # pygame-free rhythm logic + Note model
│   ├── scenes/              # menu, play, editor, settings, results
│   ├── services/            # save_system, levels, audio
│   └── ui/                  # theme, widgets, highway rendering
├── music_levels/            # user charts (<name>.json + music_<name>.mp3)
├── tests/                   # stdlib unittest
└── tools/                   # demo level + packaging script
```

`game/engine/`, `game/services/save_system.py` and `game/services/levels.py` are kept
**pygame-free** (the engine takes an injected clock) so they can be unit-tested headlessly.

---

## Docs

- **[Controls](docs/CONTROLS.md)** — every keybind for gameplay, the editor, and menus.
- **[Level Editor](docs/LEVEL_EDITOR.md)** — how to chart your own songs step by step.

---

## Credits

Built with [pygame](https://www.pygame.org/). Sample charts in `music_levels/` belong to
their respective artists.
