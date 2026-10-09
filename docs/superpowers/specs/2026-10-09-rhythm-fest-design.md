# Rhythm Fest — Design Spec

**Date:** 2026-10-09
**Status:** Approved (user-reviewed in brainstorming session)
**Stack:** Python 3.12, pygame 2.6, tkinter (file dialog only), stdlib (`json`, `os`, `shutil`, `hashlib`, `hmac`, `base64`, `unittest`)

A 4-key rhythm game styled after Fortnite Festival: centered note highway, neon purple/cyan/yellow palette, no failure state, built-in level editor.

---

## 1. Visual Direction (approved)

- **Style:** Festival Neon — deep purple/black background (`#0b0616`), cyan (`#00e0ff`) and magenta/purple (`#7b2ff7`) neon, yellow (`#ffd400`) boost accents, skewed parallelogram panels, glow effects.
- **Notes:** Solid Capsule style — chunky rounded bars; normal notes cyan, boost notes glowing yellow, hold notes are a narrower ribbon. Judgment text pops in glowing white/cyan above the hit line.
- **Window:** starts **fullscreen at desktop native resolution**; the layout is authored against a 1280×720 design space and scaled proportionally (uniform scale factor, letterboxed) so it looks identical on any monitor.

## 2. Architecture (approved)

Layered scene architecture. Thin `Game` core owns the window, clock and `SceneManager`; each screen is a `Scene`; shared services are created once and injected.

```
Rythm_game/
├── main.py                  # boots Game()
├── stats.dat                # encrypted scores (runtime)
├── settings.json            # keybinds + settings (runtime)
├── music_levels/
│   ├── <level_name>.json    # chart data
│   └── music_<level_name>.mp3|.wav
├── tests/                   # stdlib unittest
└── game/
    ├── core/
    │   ├── app.py           # Game: window, clock, main loop, shutdown
    │   ├── scene_manager.py # stack + transitions
    │   ├── scene.py         # Scene base: handle_event/update/draw
    │   └── config.py        # Config: keybinds, settings.json load/save
    ├── services/
    │   ├── save_system.py   # SaveSystem: HMAC-signed stats.dat
    │   ├── levels.py        # LevelLibrary: scan/validate/load/create
    │   └── audio.py         # AudioEngine: load/play/position_ms/stop
    ├── engine/
    │   ├── note.py          # Note (tap/hold, boost flag, lane, times)
    │   └── rhythm.py        # RhythmEngine: judgment, score, combo, boost
    ├── scenes/
    │   ├── main_menu.py     # Play, Create, Settings, Exit
    │   ├── play.py          # gameplay screen
    │   ├── editor.py        # LevelEditor recording flow
    │   ├── settings.py      # rebind + trash buttons
    │   └── results.py       # end-of-round screen
    └── ui/
        ├── theme.py         # palette, fonts, glow helpers
        └── widgets.py       # Button, Label, TextField, HighwayView
```

- `Scene` interface: `handle_event(event)`, `update(dt, song_pos)`, `draw(surface)`.
- Services injected into scenes: `SaveSystem`, `Config`, `LevelLibrary`, `AudioEngine`.
- `RhythmEngine` is created per round by the Play scene; it never draws — it only consumes the music clock and input events.

## 3. Timing, Scoring & Boost (approved)

**Clock.** `AudioEngine.position_ms()` wraps `pygame.mixer.music.get_pos()` (returns ms since music start). Fallback: a monotonic anchor captured at play-start used while music returns `-2`/stale values. All note positions are computed per frame as `(note_time − song_time) × px_per_ms` — frame-rate independent, locked to the music. Fixed note travel time: **1.6 s**. An `audio_offset` field (ms) is reserved for future calibration.

**Judgment windows** (|song_pos − note_time|):

| Rating | Window | Points | Combo |
|---|---|---|---|
| Perfect | ≤ 45 ms | +100 | continues |
| Great | ≤ 90 ms | +75 | continues |
| Good | ≤ 140 ms | +50 | continues |
| Miss | > 140 ms late | +0 | resets to 0 |

Unhit notes auto-miss when they pass the hit line by more than 140 ms.

**Sustains.** Head judged normally on key press. While the key is held and `song_pos` lies within the hold span (from head − 140 ms to tail + 140 ms), points accrue at **100 pts/sec** (× boost multiplier). Releasing early stops accrual with no penalty and no combo break; holding past the tail ends accrual cleanly. Each sustain is scored exactly once (no double-counting with the head judgment).

**Boost.** Hitting a boost note adds **+20 charge** (0–100). Pressing the Boost key (`Space` default) with charge ≥ 10 activates boost: all point gains are **doubled**, and charge drains smoothly at **20/sec** (full meter ≈ 5 s). The meter only drains while active.

**No failure state.** No health/energy bar; a round always runs to the end of the song.

## 4. Screens (approved)

**Main Menu** — order: `Play`, `Create`, `Settings`, `Exit`.

**Play** — scans `music_levels/*.json`, lists valid levels with saved high score from `stats.dat` (`0` if unplayed). Broken entries (missing/invalid JSON or missing audio) are greyed out and unselectable. Enter launches gameplay.

**Create (Level Editor)**
1. `tkinter.filedialog.askopenfilename` for `.mp3`/`.wav` (root hidden, destroyed after). On tkinter failure: in-game fallback — type the full audio path.
2. In-game text field for the level name (sanitized for the filesystem; existing name → auto-suffix `_2`, never overwrite).
3. Audio is copied to `music_levels/music_<name>.<ext>`; `<name>.json` chart file is created.
4. **Recording:** song plays once. Default keys `D F J K` place notes in lanes 1–4.
   - Quick tap → single note. Key down → key up (>120 ms) → sustain note spanning those timestamps.
   - Holding `Ctrl` while pressing/holding marks the note as a yellow **boost note**.
   - `Backspace` = remove last placed note, Editor-Stop key (default `Space`) = stop & save, `Esc` = cancel (nothing saved).
   - Notes recorded with timestamps from the same music clock used for playback.

**Settings** — four lane keybinds + Editor-Stop key. Click a keybind button → "press any key" captures the new key; a trash button next to each clears/unbinds it (a lane with no key simply can't be hit). Reference line: `Esc` = main menu, `Space` = boost. Boost and Editor-Stop are independent bindings that both default to `Space` (they never fire in the same screen).

**Results** — final score, max combo, breakdown (Perfect/Great/Good/Miss), "NEW HIGH SCORE!" flag; saves to `stats.dat`. Buttons: **Again** (restart same song immediately) and **Main Menu**.

## 5. Save Security (approved)

`./stats.dat` — JSON + HMAC/SHA-256 with obfuscation (stdlib only):

1. Payload: compact JSON `{"highscores": {level: score}, "totals": {...}}`.
2. Obfuscate: XOR with keystream `sha256(secret_salt + counter)` blocks (unreadable binary).
3. Sign: `HMAC-SHA256(key, obfuscated_payload)`.
4. Store `base64(payload || mac)`; atomic write via temp file + `os.replace`.
5. Verification failure → move file to `stats.dat.bak`, load defaults, print one console warning.

Keybinds/settings live in plain `settings.json` (not score data).

## 6. Error Handling (approved)

- Invalid level JSON / missing audio → greyed-out broken entry in Play, never a crash.
- Corrupt `stats.dat` → backed up, defaults used.
- Level name sanitized; collisions auto-suffixed.
- Mixer/audio-device init failure → clear message, clean shutdown.
- Song end (music position stops advancing / `mixer.music.get_busy()` false after min duration) → Results screen.
- All scene transitions go through `SceneManager`, so screens are never stacked or leaked.

## 7. Testing (approved)

- `tests/test_rhythm.py` — `RhythmEngine` with an injected fake clock: judgment windows, combo reset, sustain accrual, boost charge/activation/drain, multiplier.
- `tests/test_save.py` — round-trip, tamper detection (flip a byte → rejected), missing-file defaults.
- `tests/test_levels.py` — validation of good/bad level JSON, name sanitization.
- Run: `python -m unittest` (stdlib only). Manual smoke test of every screen.
