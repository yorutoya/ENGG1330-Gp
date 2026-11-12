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
| Docker verification | Verified in the supplied course container (`2026-v03`, Python 3.13 / Debian Bookworm) |

The container details come from the supplied `project_docker/dockerfile` and `project_docker/compose.yaml`. The base image is pinned to `sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e`. Local checks used Python 3.15.0. The project team has also verified execution in the supplied Docker course environment.

## Requirements and Running the Game

- Python 3 with the `curses` module available. Verified environments are CPython 3.15.0 on macOS and Python 3.13 in the supplied Docker course container.
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

The game folder should be placed inside the provided course container's `project/` folder such that the entry point is `project_docker/project/ENGG1330-Gp1/main.py`. Keep the `include/` folder adjacent to `main.py`.

With the course container up and running, open a terminal in the `project_docker/` folder and type the following commands:

```sh
docker compose build game
docker compose run --rm game python /workspace/ENGG1330-Gp1/main.py
```

## Purpose and Rules

The goal is to escape the facility before the emergency cells are depleted. The starting amount of emergency cells per expedition is **three**. Clues found throughout the adventure can be viewed in the notebook with **Tab**.

### Rooms and Progression

1. **Mirror Console:** decode the mirror alphabet message and enter the full English command. This action enables emergency lighting and gives the encoder offset.
2. **Locked Drawer:** decode the password using the offset from the previous room and obtain encrypted badge stamps, circuit colors in an order, and access to the remaining two rooms.
3. **Energy Circuit (optional):** guide the energy snake and collect six nodes using the obtained three-color order, repeating twice. Do not collide with walls, the snake's body, and incorrect-color nodes. Every move consumes the charge from the energy snake. This room restores mains power and reveals the terminal sequence on the gate.
4. **Security Interlock:** push crates onto the matching pressure plates and compute the three terminal codes from the badges and the offset, entering them in the right order. Crates can only be pushed, not pulled. In the case where room 3 was skipped, the backup battery powers only the `a` plate: push box `A` on it. The `b` plate stays inactive under this condition. Otherwise, both plates are required: box `A` must be placed on `a` and box `B` on `b`. If the battery was enabled, the terminal sequence can be computed by converting the circuit colors from the drawer to numbers (`A=1`, `C=2`, `V=3`) and then reversing the resulting order.

Press **H** in the security room to get three help screens: crate manipulation instructions, instructions for terminal codes computation, and radio usage/activation. The terminal input screen provides the relevant badge stamp, offset, and terminal order. Tab opens BADGE CLUES; F1 gives progressive decoding hints. Badge A is an encrypted label from the drawer; box A is a movable object on the map.

At the gate, the rescue radio (`O`) and the shared radio/alarm feed (`F`) can also be used. The former requires mains power and two plates, while the latter allows communication. Passing the gate completes the route selection, which locks the unused rooms.

### Recovering Badge Values

The A/C/V badges reuse both earlier ciphers. Each expedition has different
stamped numbers, while the decoding rules stay the same:

1. Decode each number like the drawer password: subtract the console offset,
   wrap into 1–26, and convert to letters using A=1 through Z=26.
2. Mirror those letters using the console alphabet: A ↔ Z, B ↔ Y, and so on.
3. Add the mirrored letters' A1Z26 values to get that badge's value.
4. Use that value in the appropriate terminal formula. The badge value and
   terminal code are different numbers.

For example, with offset 7, a sample stamp `7 - 6` decodes to Z Y, mirrors
to A B, and gives a badge value of 1+2=3. This illustrates the rule; it is
not a fixed answer to the current expedition. Notes preserve all stamps
and instructions, and viewing hints does not cost cells.

New checkpoints preserve these clues. Older checkpoints with issued plain
badge numbers retain those numbers and show them in ACCESS NOTES.

### Cells, Conditions, and Rewards

- Wrong answers on any of the console and drawer decoding challenges, circuit failures, incorrect terminal codes/order on gate verification, and failed final challenges will cause loss of one cell.
- Abandoning or resetting the circuit completion attempt after making some movement costs one cell. Resetting the gate action sequence does not refund lost cells.
- Hints and the notebook do not consume cells. With zero cells, the expedition ends.
- Conditions may vary between the expeditions. The normal circuit budget is applied under **STABLE**, **POWER LEAK** reduces it by 80 charges, and **INTERFERENCE** changes the terminal sequence of the powered gate.
- Finishing the drawer and the circuit allows choosing the reward: **Spare cell** restores one cell, up to five; **Capacitor** adds 120 charge per circuit attempt; **Surge fuse** absorbs the next cell loss. Exiting the reward selection screen causes loss of the reward. Starting a new expedition clears the rewards screen.
- Starting a new expedition clears the rooms, resources, and clues but saves the checkpoint and the collection.

### Endings

Ending is unlocked after passing the respective final challenge.

| Ending | Route condition | Final challenge |
| --- | --- | --- |
| DAWN | Mains power restored and transmission made through the rescue radio | Alignment and transmission through three coupled antennas |
| SILENT EXIT | Mains power restored and no transmission | Escape via a corridor with scanner sweeps avoidance |
| LAST LIGHT | Skipping the circuit and escaping via the battery-powered route | Power budget allocation for the light, bridge motor, and lift |

Collect all three endings across expeditions to unlock a secret transmission in the archive.

## Controls

The controls are shown at the bottom of every game screen.

| Screen | Keys |
| --- | --- |
| Facility map | Arrow keys: selecting; `1` – `4`: selecting a room; Enter: opening |
| Map utilities | `P`: saving the progress; `L`: loading the progress; `N`: starting a new expedition; `V`: archive; `Q`/Esc: quit |
| Text puzzles | Typing an answer; Enter: submitting; Backspace: editing; F1: hint; Esc: returning |
| Energy circuit | Arrow keys: steering; Space: pausing/unpausing; `R`: retrying; `Q`/Esc: returning |
| Security interlock | Arrow keys: moving/pushing; `E`: using nearby device; `U`: undoing; `R`: resetting the room; `H`: help; `Q`/Esc: returning |
| Signal relay | `1`/`2`/`3`: turning antennas; Enter: transmitting |
| Scanner corridor | Arrow keys/WASD: moving; Space: waiting |
| Emergency shaft | `1`/`2`/`3`: connecting power; Space: aligning bridge; Left/Right: walking; Enter: launching lift |
| Notebook | Tab: opening from gameplay screens |

Press **Q** or Esc to return from the final challenge. The current progress is preserved.

## Saving and Loading

Press **P on the map** to write a checkpoint to the `progress.sav` file in the project root. Press **L** on the map and confirm with **Y** to read the checkpoint. Saving again overwrites the current checkpoint, and the automatic expedition saving on game exit is not implemented yet.

The checkpoint contains the current rooms progress, collected resources, clues, and final challenge progress. Unfinished circuits and security rooms reset but retain the overall progress when reopened; individual moves are not checkpointed.

The completion of the endings is tracked separately in the `endings.sav` file. Reading the checkpoint or starting a new expedition does not delete this collection. The files are created during the gameplay and are not necessary for game launch.

## Tests

### Checks Performed

The following checks were performed locally on CPython 3.15.0 while writing this README:

- Syntax compilation of `main.py` and all Python files in the `include/` folder:

  ```sh
  python3 -m compileall -q main.py include
  ```

- Ad hoc logic smoke checks for mirror decoding and command normalization, drawer decoding and answer validation, initial room accessibility, distinctness of the gate codes, all three ending conditions, fuse consumption and cell loss, checkpoint roundtrip, rejection of the invalid checkpoint, and successful execution of emergency shaft actions.

The local logic checks did not create save files. Separately, the project team has verified execution in the supplied Docker course container. There is currently no committed automated test suite.

### Manual Playtest Checklist

The following checklist records expected gameplay behavior and can be reused for regression testing after changes:

| Test | Expected behavior |
| --- | --- |
| Launch and resizing | Map shown at 80 × 24 or greater; smaller terminal reports a message about reszing |
| Prerequisites of rooms | Drawer requires the console; circuit and gate require the drawer |
| Answers and resources | Correct answers unlock clues; wrong answers reduce cells unless absorbed by fuse |
| Circuit | Correct nodes move the progress; collisions, wrong colors, and empty charge fail the attempt |
| Gate | Plate requirements, terminal codes/order, undo, and reset behave as expected |
| Ending routes | Each route leads to the final challenge and unlocks the ending upon success |
| Saving/loading | Save from the map, quit, launch again, and load to recover the checkpoint |
| Invalid checkpoint | Report an invalid checkpoint without replacing the current expedition |
| Archive | Unlock the transmission with three distinct endings and keep the collection after restarting |

## Known Limitations

- Room designs and basic rules stay the same between expeditions. Codes, nodes position and conditions vary, but repeated play can make the puzzles easier.
- Exiting from unfinished circuits and security rooms reset the progress of those rooms. Individual snake moves, crate positions, and terminal check progress are not checkpointed. Final challenges preserve their state.
- One manual checkpoint is available, from the map screen. Saving replaces the previous checkpoint, and there is no automatic saving on quitting.
- Exiting the security room selects the route. To try a different ending, start a new expedition or reload a previous checkpoint.

## Contributions

| Member name | Main responsibilities | Specific work completed | Related files or deliverables |
| --- | --- | --- | --- |
| Cao Zhiheng | Adapt Single Programs to the project and Construct the Interface | Design Decipher 3, 4 and the endings. Developed most game structure. | archive.py, decipher_3.py, decipher_4.py, expedition.py, finale.py, interface.py, savegame.py, CURSES_REFERENCE.md, main.py, README.md |
| Ren Zhuoran | Decipher 2 | Designed Decipher 2 and provided the prototype | decipher_2.py |
| Ho Shu To | Decipher 1 | Designed Decipher 1 and provided the prototype | decipher_1.py |

### Shared Work

- **Planning and game design:** Cao Zhiheng, Ren Zhuoran, Ho Shu To.
- **Integration and testing:** Cao Zhiheng, Ren Zhuoran, Ho Shu To.
- **1-minute Trailer:** Ho Shu To.
- **5-minute Demo:** Ren Zhuoran.

## Sources and License

- [CURSES_REFERENCE.md](CURSES_REFERENCE.md) contains the project's curses reference and links to the official Python documentation used for that reference.
- [ai_use.md](ai_use.md) records the group's declared use of generative AI. Keep it up to date for the final submission.
- The source code is distributed under the [MIT License](LICENSE).

