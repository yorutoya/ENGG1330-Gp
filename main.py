"""One curses session connects all available escape-room challenges."""
import curses
from include.decipher_2 import main as keyboard
from include.decipher_3 import main as circuit
from include.decipher_4 import main as gate


def put(screen, y, text, style=0):
    rows, cols = screen.getmaxyx()
    if y < rows - 1 and cols > 4:
        screen.addnstr(y, 2, text, cols - 4, style)


def main(screen):
    screen.keypad(True)
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    selected = 0
    solved = [False, False]
    message = "Restore the circuit, then open the evacuation gate."
    while True:
        screen.timeout(-1)
        screen.erase()
        rows, cols = screen.getmaxyx()
        if rows < 22 or cols < 68:
            put(screen, 0, "Resize terminal to 68 x 22. Q: quit")
            screen.refresh()
            if screen.getch() in (ord('q'), ord('Q')):
                return
            continue
        put(screen, 1, "UNDERGROUND / EVACUATION CONTROL", curses.A_BOLD)
        put(screen, 3, "Alarm active. Two working terminals stand between you and daylight.")
        put(screen, 5, "POWER CIRCUIT  --->  SECURITY GATE  --->  SURFACE")
        put(screen, 6, "Progress: " + " ".join('[OK]' if v else '[--]' for v in solved))
        labels = ["03  Energy snake / restore circuit", "04  Pressure plate / open gate", "Reset expedition", "Quit"]
        for i, label in enumerate(labels):
            suffix = ""
            if i < 2:
                suffix = " [COMPLETE]" if solved[i] else (" [LOCKED]" if i == 1 and not solved[0] else " [READY]")
            put(screen, 9 + i, ('> ' if selected == i else '  ') + label + suffix,
                curses.A_REVERSE if selected == i else 0)
        put(screen, 15, message)
        put(screen, 17, "UP/DOWN or W/S: select | ENTER: interact | Q: quit")
        put(screen, 19, "Parts 1 and 2 are not supplied yet; this prototype starts at Part 3.")
        screen.refresh()
        key = screen.getch()
        if key in (ord('q'), ord('Q')):
            return
        if key in (curses.KEY_UP, ord('w')):
            selected = (selected - 1) % 4
        elif key in (curses.KEY_DOWN, ord('s')):
            selected = (selected + 1) % 4
        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 3:
                return
            if selected == 2:
                solved = [False, False]
                message = "Expedition reset. Restore the circuit first."
            elif selected == 1 and not solved[0]:
                message = "No power. Complete the energy circuit to unlock this terminal."
            else:
                screen.erase()
                result = (circuit if selected == 0 else gate)(screen)
                screen.timeout(-1)
                if result:
                    solved[selected] = True
                    message = "Daylight! Evacuation complete. Reset to start a new expedition." if all(solved) else "Power restored. The security gate terminal is now online."
                    selected = 1 if not all(solved) else 2
                else:
                    message = "Returned to control. Your completed checkpoints are saved this session."


if __name__ == '__main__':
    curses.wrapper(main)
