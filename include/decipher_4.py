import curses
from include.effects import typewriter

MAP = [
    "#########",
    "#...#..E#",
    "#...D...#",
    "#..a#...#",
    "#########"
]
START = (2, 2)
BOX_START = (3, 2)
PLATE = (3, 3)
EXIT = (7, 1)

def can_move(position, door_open):
    x,y = position
    if not (0 <= y < len(MAP) and 0 <= x < len(MAP[y])):
        return False
    tile = MAP[y][x]
    return tile != "#" and (tile != "D" or door_open)

def move(player, box, directions):
    dx, dy = directions
    next_player = (player[0] + dx, player[1] + dy)
    door_open = box == PLATE
    if not can_move(next_player, door_open):
        return player, box
    if next_player == box:
        next_box = (box[0] + dx, box[1] + dy)
        if not can_move(next_box, door_open):
            return player, box
        box = next_box
    return next_player, box

def main(screen):
    screen.keypad(True)
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    player, box, won = START, BOX_START, False
    keys = {
        curses.KEY_UP: (0, -1), curses.KEY_DOWN: (0, 1), curses.KEY_LEFT: (-1, 0), curses.KEY_RIGHT: (1, 0),
        ord('w'): (0, -1), ord('s'): (-1, 0), ord('a'): (0, 1), ord('d'): (1, 0),
    }
    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        if height < 18 or width < 64:
            screen.addnstr(0, 0, "Resize to 64 x 18. Q: quit", max(0, width - 1))
            screen.refresh()
            if screen.getch() in (ord('q'), ord('Q')):
                return
            continue
        screen.addstr(1, 2, "Last Step: Open the gate to the ground")
        screen.addstr(3, 2, "Push B onto a, open D, then reach E.")
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
               if tile == "D" and box == PLATE:
                    tile = "/"
               if (x, y) == box:
                   tile = "*" if box == PLATE else "B"
               if (x, y) == player:
                   tile = "@"
               screen.addstr(y + 5, x * 2 + 2, tile)
        screen.addstr(11, 2, "@: you | B: box | a: plate | D: door | E: exit")
        screen.addstr(12, 2, "*: box on plate | /: open door")
        if won:
            screen.addstr(14, 2, "Escaped! R to play again | Q: quit")
        elif box == PLATE:
            screen.addstr(14, 2, "Door is opened. Walk through / and reach E")
        else:
            screen.addstr(14, 2, "Push the box from above. You cannot pull boxes.")
        screen.addstr(16, 2, "Arrows/WASD: move | R:restart | Q:quit")
        screen.refresh()
        key = screen.getch()
        if key in (ord('Q'), ord('q')):
            return
        if key in (ord('r'), ord('R')):
            player = START
            box = BOX_START
            won = False
            continue
        if key in keys and not won:
            player, box = move(player, box, keys[key])
            won = player == EXIT

def run_lock4():
    return curses.wrapper(main)

if __name__ == "__main__":
    escaped = run_lock4()
    typewriter("You escaped!" if escaped else "The exit is still locked.")



