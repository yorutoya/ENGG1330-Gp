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
    solved = [False, False, False]
    message = "Unlock the drawer to activate the terminals."
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
        put(screen, 5, "DRAWER  --->  POWER CIRCUIT  --->  SECURITY GATE")
        put(screen, 7, "Find the key in the drawer to activate the terminals.")
        put(screen, 8, "Progress: " + " ".join('[OK]' if v else '[--]' for v in solved))
        labels = ["02  Unlock the drawer for the key", "03  Energy snake / restore circuit",
                  "04  Pressure plate / open gate", "Reset expedition", "Quit"]
        for i, label in enumerate(labels):
            suffix = ""
            if i < 3:
                suffix = " [COMPLETE]" if solved[i] else (" [LOCKED]" if i > 0 and not solved[i - 1] else " [READY]")
            put(screen, 9 + i, ('> ' if selected == i else '  ') + label + suffix,
                curses.A_REVERSE if selected == i else 0)
        put(screen, 15, message)
        put(screen, 17, "UP/DOWN or W/S: select | ENTER: interact | Q: quit")
        put(screen, 19, "Complete each challenge to unlock the next terminal.")
        screen.refresh()
        key = screen.getch()
        if key in (ord('q'), ord('Q')):
            return
        if key in (curses.KEY_UP, ord('w')):
            selected = (selected - 1) % len(labels)
        elif key in (curses.KEY_DOWN, ord('s')):
            selected = (selected + 1) % len(labels)
        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 4:
                return
            if selected == 3:
                solved = [False, False, False]
                message = "Expedition reset. Unlock the drawer first."
            elif selected > 0 and not solved[selected - 1]:
                message = "Complete the previous challenge to unlock this terminal."
            else:
                screen.erase()
                try:
                    if selected == 0:
                        curses.echo()
                        try:
                            curses.curs_set(1)
                        except curses.error:
                            pass
                    result = (keyboard, circuit, gate)[selected](screen)
                finally:
                    curses.noecho()
                    try:
                        curses.curs_set(0)
                    except curses.error:
                        pass
                screen.timeout(-1)
                if result:
                    solved[selected] = True
                    messages = (
                        "Key acquired. The power circuit terminal is now online.",
                        "Power restored. The security gate terminal is now online.",
                        "Daylight! Evacuation complete. Reset to start again.",
                    )
                    message = messages[selected]
                    selected = selected + 1
                else:
                    message = "Returned to control. Your completed checkpoints are saved this session."


if __name__ == '__main__':
    curses.wrapper(main)
