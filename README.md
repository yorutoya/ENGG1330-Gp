# UNDERGROUND

A single-player terminal escape game for the ENGG1330 group project. Explore an underground facility, recover clues, restore its systems, and complete an escape challenge. Your actions determine which of three endings you reach.

## Project Details

| Item | Details |
| --- | --- |
| Course | ENGG1330 |
| Group | 3 |
| Members' names | Cao Zhiheng, Ren Zhuoran, Ho Shu To |
| Subclass | L |
| Course container version | `2026-v03` (`COURSE_ENVIRONMENT_VERSION`) |
| Course container image | `engg1330-project:2026-v03` |
| Container base | `python:3.13-slim-bookworm` (Python 3.13 / Debian Bookworm), pinned by SHA-256 digest |
| Local verification environment | CPython 3.15.0 on macOS |

The container details come from the supplied `project_docker/dockerfile` and `project_docker/compose.yaml`. The base image is pinned to `sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e`. Local checks used Python 3.15.0; execution inside the course container has not yet been verified.

## Requirements and Running the Game

- Python 3 with the `curses` module available. The current local environment uses CPython 3.15.0; other Python versions have not been verified here.
- An interactive terminal with at least **80 columns by 24 rows** and support for curses colors and keyboard input.
- A writable project directory for checkpoints and ending records.

The active game uses Python's standard library only. No third-party Python packages or external assets are required in the verified environment.

Open a terminal in the extracted project folder, which contains `main.py` and `include/`, then run exactly:

```sh
python3 main.py
```

Use a real terminal, such as the terminal tab in an IDE, rather than a plain output console. To check the interpreter and curses import before starting:

```sh
python3 --version
python3 -c "import curses; print('curses import OK')"
```

### Running in the Course Container

Place the game folder inside the supplied container's `project/` directory so that the entry point is `project_docker/project/ENGG1330-Gp1/main.py`. Keep the `include/` directory beside `main.py`.

With Docker running, open a terminal in `project_docker/` and run:

```sh
docker compose build game
docker compose run --rm game python /workspace/ENGG1330-Gp1/main.py
```

The explicit command overrides the container's default `tic_tac_toe.py` example. Compose mounts `project/` at `/workspace`, enables an interactive terminal, and sets `TERM=xterm-256color`. Keep the actual terminal at least 80 × 24. Save files are written into the mounted game folder and remain after the container exits.

To inspect the running environment's configured version and Python version:

```sh
docker compose run --rm game printenv COURSE_ENVIRONMENT_VERSION
docker compose run --rm game python --version
```

## Purpose and Rules

The objective is to escape the facility before your emergency cells run out. Each expedition starts with **three cells**. Recovered clues are available in the notebook with **Tab**.

### Rooms and Progression

1. **Mirror Console:** decode a mirror-alphabet message and enter the full English command. This restores emergency lighting and reveals an encoder offset.
2. **Locked Drawer:** use the offset to decode a numeric password. The drawer provides badge numbers, a circuit color order, and access to both remaining rooms.
3. **Energy Circuit (optional):** steer an energy snake and collect six nodes in the recovered three-color order, repeated twice. Avoid walls, the snake's body, and wrong-color nodes. Each movement consumes charge. Completing this room restores mains power and reveals the gate's terminal sequence.
4. **Security Interlock:** push crates onto matching pressure plates, calculate the three terminal codes from your badges and offset, and verify them in the required order. Crates can be pushed but not pulled. Mains power requires both matching plates; battery mode requires only plate `a`. In battery mode, convert the drawer's colors to numbers (`A=1`, `C=2`, `V=3`) and reverse their order for the terminal sequence.

At the gate, you can also operate the rescue radio (`O`) or disconnect the shared alarm/radio feed (`F`). The radio requires mains power and both plates. Passing through the gate commits the escape route and makes unfinished rooms unavailable.

### Cells, Conditions, and Rewards

- Incorrect console or drawer answers, failed circuit attempts, invalid gate credentials/order during verification, and exit-challenge failures can cost one cell.
- Abandoning or restarting a circuit attempt after movement also costs one cell. Undoing gate actions does not refund spent cells.
- Hints and the notebook are free. At zero cells, the expedition ends.
- Expeditions vary by seed. **STABLE** uses the normal circuit budget; **POWER LEAK** reduces it by 80 charge; **INTERFERENCE** changes the powered gate's terminal sequence.
- Completing the drawer and the circuit offers a choice of salvage modules. **Spare cell** restores one cell, up to five; **Capacitor** adds 120 charge per circuit attempt; **Surge fuse** absorbs the next cell loss. Leaving the reward screen forfeits that reward.
- Starting a new expedition resets clues, rooms, and resources while keeping the saved checkpoint and ending collection.

### Endings

An ending is awarded only after completing its final challenge.

| Ending | Route condition | Final challenge |
| --- | --- | --- |
| DAWN | Restore mains power and transmit through the rescue radio | Align three coupled antennas and transmit |
| SILENT EXIT | Restore mains power and leave without a rescue transmission | Cross a corridor while avoiding scanner sweeps |
| LAST LIGHT | Bypass the circuit and escape on battery power | Allocate limited battery charge to the light, bridge motor, and lift |

Collect all three endings across expeditions to unlock the hidden transmission in the archive.

## Controls

Controls also appear at the bottom of each game screen.

| Screen | Keys |
| --- | --- |
| Facility map | Arrow keys: select; `1`–`4`: select a room; Enter: open |
| Map utilities | `P`: save; `L`: load; `N`: new expedition; `V`: archive; `Q`/Esc: quit |
| Text puzzles | Type an answer; Enter: submit; Backspace: edit; F1: hint; Esc: return |
| Energy circuit | Arrow keys: steer; Space: start/pause/resume; `R`: retry; `Q`/Esc: return |
| Security interlock | Arrow keys: move/push; `E`: use nearby device; `U`: undo; `R`: reset room; `H`: hint; `Q`/Esc: return |
| Signal relay | `1`/`2`/`3`: turn antennas; Enter: transmit |
| Scanner corridor | Arrow keys or WASD: move; Space: wait |
| Emergency shaft | `1`/`2`/`3`: connect power; Space: align bridge; Left/Right: walk; Enter: launch lift |
| Notebook | Tab: open from gameplay screens |

Use `Q` or Esc to return from an exit challenge. Its progress is retained within the current expedition.

## Saving and Loading

Press **P on the facility map** to write a checkpoint to `progress.sav` in the project root. Press **L** on the map and confirm with **Y** to restore it. Saving again replaces the single checkpoint; expedition progress is not automatically saved when quitting.

The checkpoint stores resources, completed rooms, recovered clues reconstructed from the seed, and final escape-challenge progress. An unfinished circuit or security room restarts when reopened; its individual moves are not checkpointed.

Completed endings are recorded separately in `endings.sav`. Loading a checkpoint or starting another expedition does not erase this collection. Both save files are created during play and are not required to launch the game.

## Tests

### Checks Performed

The following checks passed locally on CPython 3.15.0 while preparing this README:

- Syntax compilation of `main.py` and all Python files in `include/`:

  ```sh
  python3 -m compileall -q main.py include
  ```

- Ad hoc logic smoke checks for mirror encoding and command normalization, drawer encoding and answer validation, initial room access, distinct gate codes, all three ending conditions, fuse consumption and cell loss, checkpoint encode/decode round trips, rejection of an invalid checkpoint, and successful emergency-shaft action sequences. Seed-dependent checks covered seeds `0`, `1`, `2`, and `7999`.

These logic checks did not write save files. There is currently no committed automated test suite, and these checks do not establish that all interactive routes work in the course container.

### Manual Playtest Checklist

The following checks remain to be completed in the submission environment:

| Test | Expected behavior |
| --- | --- |
| Launch and resize | Map appears at 80 × 24 or larger; a smaller terminal displays a resize message |
| Room prerequisites | Drawer requires the console; circuit and gate require the drawer |
| Answers and resources | Correct answers unlock clues; wrong answers consume cells unless a fuse absorbs the loss |
| Circuit | Correct nodes advance progress; collisions, wrong colors, and exhausted charge fail the attempt |
| Gate | Plate requirements, terminal codes/order, undo, and reset behave as described |
| Ending routes | Each route leads to its corresponding final challenge and records the ending after success |
| Save/load | Save from the map, quit, relaunch, and load to recover the checkpoint |
| Invalid checkpoint | An unreadable or invalid checkpoint is reported without replacing the current expedition |
| Archive | Three distinct endings unlock the transmission and remain collected after restarting |

## Known Limitations

- The course container and a complete interactive playthrough have not been verified as part of the checks above.
- The interface uses a fixed 80 × 24 layout and requires an interactive curses-capable terminal. Native Windows support has not been verified.
- Only one manual checkpoint is supported. Save and archive files require write access to the project folder.
- Unfinished circuit and gate layouts are recreated on re-entry. Final challenge state is retained and can be checkpointed from the map.
- Initial seeds use Python's process-dependent string hash, so separate launches may generate different expeditions. Room layouts remain fixed apart from seeded puzzle details.
- `include/decipher_2_old.py` is a legacy implementation and is not used by the main game.

## Contributions

Replace the placeholders below with each member's actual work. Add or remove rows as needed. Include design, implementation, testing, debugging, documentation, or presentation work where applicable.

| Member name | Main responsibilities | Specific work completed | Related files or deliverables |
| --- | --- | --- | --- |
| Cao Zhiheng | Adapt Single Programs to the project and Construct the Interface | Design Decipher 3, 4 and the endings. Developed most game structure. | archive.py, decipher_3.py, decipher_4.py, expedition.py, finale.py, interface.py, savegame.py, CURSES_REFERENCE.md, main.py, README.md |
| Ren Zhuoran | Decipher 2 | Designed Decipher 2 and provided the prototype | decipher_2.py |
| Ho Shu To | Decipher 1 | Designed Decipher 1 and provided the prototype | decipher_1.py |

### Shared Work

- **Planning and game design:** Cao Zhiheng, Ren Zhuoran, Ho Shu To.
- **Integration and testing:** Cao Zhiheng.
- **Documentation and submission:** Code Zip and README: Cao Zhiheng.

## Sources and License

- [CURSES_REFERENCE.md](CURSES_REFERENCE.md) contains the project's curses reference and links to the official Python documentation used for that reference.
- [ai_use.md](ai_use.md) records the group's declared use of generative AI. Keep it up to date for the final submission.
- The source code is distributed under the [MIT License](LICENSE).

