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

## ▶ Download & play

**No Python or installation required** — a ready-to-play build is included in the repo.

1. Download the project (grab the **`dist/`** folder, or clone the whole repo).
2. Open **`dist/`** and double-click **`Rhythm Fest.exe`**.
3. Keep the exe next to the bundled **`music_levels/`** folder — the game loads its songs from there.

> **First run on Windows?** The exe is unsigned, so SmartScreen may show *"Windows protected
> your computer."* Click **More info → Run anyway**.

That's it — pick a song from **Play** and start hitting notes.

---

## 🎮 Controls

The four lanes sit under your right and left hand; everything else is one key away.

| Action | Default key |
|---|---|
| Lanes 1–4 | `D` `F` `J` `K` |
| **Boost** (double points) | `Space` |
| Confirm / select | `Enter` |
| Back / to main menu | `Esc` |

In the editor: hold **`Ctrl`** for a boost note, **`Space`** to stop & save, **`Backspace`** to undo.

**Every key is remappable** in-game via **Settings**. Full reference (gameplay, editor, and menu keys):
➡ **[docs/CONTROLS.md](docs/CONTROLS.md)**

---

## 🛠 Level editor

Turn any `.mp3`/`.wav` into a playable chart. **Main Menu → Create**, pick your audio, name
the level, then tap the lane keys along to the song — a quick tap makes a note, holding a
key makes a hold note. Press **Space** to save and it shows up in **Play**.

Step-by-step guide (importing, recording, boost notes, saving):
➡ **[docs/LEVEL_EDITOR.md](docs/LEVEL_EDITOR.md)**

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
---

# For developers

Everything below is for running, testing, or building from source. (Players can stop reading here.)

## Run from source

```powershell
python -m pip install -r requirements.txt
python main.py          # must run from the repo root
```

> **Run from the repo root.** The game opens `music_levels/`, `stats.dat` and
> `settings.json` relative to the current working directory — launching from elsewhere
> makes files appear to vanish.

## Requirements

- **Python 3.12**
- **pygame 2.6.1** (`requirements.txt`)

pygame must be installed for the *same* interpreter you run with (it lives in user
site-packages). A `ModuleNotFoundError: No module named 'pygame'` means a different
`python.exe` is running — reinstall there.

## Tests & tooling

```powershell
python -m unittest discover -s tests         # 33 tests, ~0.1s
python tools/create_demo_level.py            # (re)generate the Demo_Beat level
```

There is no lint/typecheck/CI configured — the verification bar is
`python -m py_compile <changed files>` plus the unittest run.

## Building the .exe

Rebuild the bundled `dist/` (adds `pyinstaller` via `requirements-dev.txt`):

```powershell
python -m pip install -r requirements-dev.txt
powershell -File tools\package.ps1           # -> dist\Rhythm Fest.exe
```

## Project layout

```
Rythm_game/
├── main.py                  # boots Game()
├── dist/                    # ready-to-play build (exe + bundled music_levels/)
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

## Credits

Built with [pygame](https://www.pygame.org/). Sample charts in `music_levels/` belong to
their respective artists.
