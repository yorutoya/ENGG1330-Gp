import curses

WIDTH = 30
HEIGHT = 16
TARGET = 8
TIME_LIMIT = 45
MOVE_INTERVAL = 0.16

def make_food(snake):
    available = [
        (y, x)
        for y in range(1, HEIGHT - 1)
        for x in range(1, WIDTH - 1)
        if (y, x) not in snake
    ]
    return available[(len(snake) * 37) % len(available)]

def play_round(screen):
    snake = [(8, 10), (8, 9), (8, 8)]
    direction = (0, 1)
    food = make_food(snake)
    score = 0
    ticks = 0

    controls = {
        curses.KEY_UP: (-1, 0),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
        curses.KEY_RIGHT: (0, 1),
        ord("w"): (-1, 0),
        ord("s"): (1, 0),
        ord("a"): (0, -1),
        ord("d"): (0, 1),
    }

    screen.timeout(160)

    while True:
        remaining = max(0, TIME_LIMIT - ticks * MOVE_INTERVAL)
        rows, cols = screen.getmaxyx()
        if rows < HEIGHT + 4 or cols < 55:
            screen.erase()
            screen.addnstr(0, 0, "Resize to 55 x 20. Q: back", max(0, cols - 1))
            screen.refresh()
            if screen.getch() in (ord("q"), ord("Q")):
                return False, "Quit"
            continue
        screen.erase()
        screen.addstr(
            0, 0,
            f"LOCK 3 | Score: {score}/{TARGET} | Energy: {remaining:04.1f}"
        )
        screen.addstr(1, 0, "Press ARROWS or WASD to move | Q to quit")
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if y in (0, HEIGHT - 1) or x in (0, WIDTH - 1):
                    screen.addch(y + 3, x, "#")

        screen.addch(food[0] + 3, food[1] ,"*")
        for index, (y, x) in enumerate(snake):
            screen.addch(y + 3, x, "@" if index == 0 else "o")
        screen.refresh()
        if score >= TARGET:
            return True, "Circuit restored!"
        if remaining <= 0:
            return False, "Time is up!"
        proposed = direction
        key = screen.getch()
        if key in (ord("q"), ord("Q")):
            return False, "Quit"
        if key in controls:
            candidate = controls[key]
            if candidate != (-direction[0], -direction[1]):
                proposed = candidate
        # A fixed curses delay keeps movement independent of key repeat.
        if key != -1:
            curses.napms(160)
            curses.flushinp()
        ticks += 1
        direction = proposed

        head_y, head_x = snake[0]
        new_head = (head_y + direction[0], head_x + direction[1])
        y,x = new_head
        eating = new_head == food
        if not (1 <= y < HEIGHT - 1 and 1 <= x < WIDTH - 1):
            return False, "You hit a wall!"
        body = snake if eating else snake[:-1]
        if new_head in body:
            return False, "You hit yourself!"
        snake.insert(0, new_head)
        if eating:
            score += 1
            if score < TARGET:
                food = make_food(snake)
        else:
            snake.pop()

def main(screen):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.keypad(True)
    rows, cols = screen.getmaxyx()
    if rows < HEIGHT + 4 or cols < 55:
        screen.addstr(0, 0, "Resize terminal to at least 55 columns x 20 rows")
        screen.refresh()
        screen.getch()
        return False
    screen.addstr(0, 0, "LOCK 3: Collect 8 points before energy runs out.")
    screen.addstr(2, 0, "Use arrows or WASD. Avoid walls and your body.")
    screen.addstr(4, 0, "Press any key to start.")
    screen.refresh()
    screen.getch()
    while True:
        won, message = play_round(screen)
        if message == "Quit":
            return False
        screen.timeout(-1)
        screen.erase()
        screen.addstr(0, 0, message)
        if won:
            screen.addstr(2, 0, "Circuit restored! Press any key to continue.")
            screen.refresh()
            screen.getch()
            return True
        screen.addstr(2, 0, "R: restart Lock 3 | Q: quit")
        screen.refresh()
        while True:
            key = screen.getch()
            if key in (ord("r"), ord("R")):
                break
            if key in (ord("q"), ord("Q")):
                return False

def run_lock3():
    return curses.wrapper(main)

if __name__ == "__main__":
    run_lock3()
