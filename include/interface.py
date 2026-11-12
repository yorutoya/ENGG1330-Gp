# Shared UI helpers for bounded drawing, text input, the notebook and message screens.
"""Small shared curses helpers: layout, clue journal, and text input."""
import curses

# Use only the top-left 80x24 terminal area, with additional margins around body text.
MIN_ROWS, MIN_COLS = 24, 80
CONTENT_WIDTH = 70

# Both movement puzzles use the same arrow/WASD controls.
# Directions are (dx, dy): x increases to the right and y increases downward.
DIRECTIONS = {
    curses.KEY_UP: (0, -1), curses.KEY_DOWN: (0, 1),
    curses.KEY_LEFT: (-1, 0), curses.KEY_RIGHT: (1, 0),
    ord('w'): (0, -1), ord('s'): (0, 1),
    ord('a'): (-1, 0), ord('d'): (1, 0),
}


# Clip text to the viewport and avoid the last column to prevent wrapping or scrolling.
def text(screen, y, x, message, style=0, width=None):
    rows, cols = screen.getmaxyx()
    rows, cols = min(rows, MIN_ROWS), min(cols, MIN_COLS)
    if 0 <= y < rows and 0 <= x < cols - 1:
        limit = cols - x - 1
        if width is not None:
            limit = min(width, limit)
        if limit > 0:
            screen.addnstr(y, x, str(message), limit, style)


# Wrap English text at word boundaries, splitting words that exceed the available width.
def wrap(message, width):
    """Word-wrap ASCII text without importing another library."""
    result = []
    remaining = str(message)
    while len(remaining) > width:
        split = remaining.rfind(' ', 0, width + 1)
        if split <= 0:
            split = width
        result.append(remaining[:split])
        remaining = remaining[split:].lstrip()
    result.append(remaining)
    return result


# Wrap each message and combine the lines for input and notification screens.
def wrap_lines(messages, width):
    lines = []
    for message in messages:
        lines.extend(wrap(message, width))
    return lines


# Draw body text at column 5 with a maximum width of 70 characters.
def line(screen, y, message, style=0):
    text(screen, y, 5, message, style, CONTENT_WIDTH)


# Draw the shared frame; return False when the terminal is too small so callers can pause play.
def frame(screen, title, clues, controls):
    rows, cols = screen.getmaxyx()
    for y in range(min(rows, MIN_ROWS)):
        text(screen, y, 0, ' ' * (MIN_COLS - 1))
    if rows < MIN_ROWS or cols < MIN_COLS:
        for y, message in enumerate(wrap('Paused. Resize to 80 x 24. Q/Esc: back.', max(1, cols - 1))):
            text(screen, y, 0, message)
        screen.refresh()
        return False
    text(screen, 0, 5, 'UNDERGROUND', curses.color_pair(1) | curses.A_BOLD)
    if 'cells' in clues:
        status = f'Cells {clues["cells"]}'
        if clues.get('fuse'):
            status += ' + fuse'
        text(screen, 0, 59, status, curses.color_pair(2))
    line(screen, 2, title, curses.A_BOLD)
    text(screen, 22, 5, controls, curses.A_DIM, width=73)
    return True


# Show notebook pages in a separate input loop so navigation does not affect the puzzle.
def show_notes(screen, clues):
    """An on-demand notebook. Closing it returns to the unchanged room."""
    page = 0
    titles = ('JOURNAL + EXPEDITION [1/3]', 'ACCESS NOTES [2/3]',
              'BADGE CLUES [3/3]')
    screen.timeout(-1)
    while True:
        ready = frame(screen, titles[page], clues,
                      'Tab / arrows: page    Enter / Esc: return')
        if ready:
            if page == 0:
                # Two open columns, separated by whitespace rather than borders.
                accent = curses.color_pair(1)
                text(screen, 5, 5, '01   MIRROR CONSOLE', accent)
                offset = f'Cipher offset: +{clues["shift"]}' if 'shift' in clues else 'No record yet.'
                text(screen, 7, 5, offset, width=36)
                text(screen, 10, 5, '02   DRAWER', accent)
                if 'order' in clues:
                    text(screen, 12, 5, 'Fuse order: ' + ' > '.join(clues['order']), width=36)
                    text(screen, 13, 5, 'Repeat twice (6 nodes).', curses.A_DIM)
                else:
                    text(screen, 12, 5, 'No record yet.')
                text(screen, 15, 5, '03   GATE LOG', accent)
                if 'sequence' in clues:
                    text(screen, 17, 5, 'Terminals: ' + ' > '.join(map(str, clues['sequence'])), width=36)
                    text(screen, 19, 5, 'Only plate a is required.' if clues.get('emergency') else 'Keep BOTH plates powered.')
                elif 'order' in clues:
                    text(screen, 17, 5, 'Battery: reverse fuse labels.')
                    text(screen, 19, 5, 'A=1, C=2, V=3. Use plate a.')
                else:
                    text(screen, 17, 5, 'No record yet.')

                condition = clues.get('condition', 'STABLE')
                text(screen, 5, 47, 'EXPEDITION', accent)
                text(screen, 7, 47, condition)
                details = {'STABLE': 'Normal charge and access order.',
                           'POWER LEAK': 'Circuit starts with 80 less charge.',
                           'INTERFERENCE': 'Restored terminal order is altered.'}
                for y, detail in enumerate(wrap(details[condition], 28), 8):
                    text(screen, y, 47, detail, curses.A_DIM, width=28)
                text(screen, 12, 47, 'Installed modules', accent)
                for index, module in enumerate(clues.get('modules') or ['None']):
                    text(screen, 14 + index * 2, 47, module, width=28)
                text(screen, 19, 47, 'Modules last this run.', curses.A_DIM)
                text(screen, 20, 47, 'No cells = run over.', curses.A_DIM)
            elif page == 1:
                if 'badges' in clues:
                    if 'badge_stamps' in clues:
                        line(screen, 6, 'Badge values are hidden in the stamped numbers.')
                        line(screen, 8, 'Press Tab for BADGE CLUES and decode A, C and V.')
                        line(screen, 10, 'Then use the recovered totals in these terminal rules:')
                    else:
                        for index, (name, value) in enumerate(clues['badges'].items()):
                            line(screen, 6 + index * 2, f'Badge {name}     {value}', curses.color_pair(2))
                    line(screen, 13, '1 : A + offset')
                    line(screen, 15, '2 : C - offset')
                    line(screen, 17, '3 : V + 2 x offset')
                    line(screen, 19, 'Each terminal has its own rule. Use the console offset.')
                else:
                    line(screen, 7, 'Open the drawer to recover its numbered badges.')
            elif page == 2:
                if 'badge_stamps' in clues:
                    for index, (name, stamp) in enumerate(clues['badge_stamps'].items()):
                        line(screen, 5 + index * 2, f'Badge {name}: {stamp}', curses.color_pair(2))
                    line(screen, 12, f'1. Like OPEN: subtract offset {clues["shift"]} from each number.')
                    line(screen, 13, '   Wrap into 1..26, then read A=1, B=2, ... Z=26.')
                    line(screen, 15, '2. Like room 1: mirror each letter (A<->Z, B<->Y).')
                    line(screen, 17, '3. Add the mirrored letters using A=1 ... Z=26.')
                    line(screen, 19, 'That total is the badge value, not the terminal code.')
                    line(screen, 20, 'Example: final letters A B give a badge value of 1+2=3.')
                else:
                    line(screen, 7, 'Open the drawer to discover badge clues.')
                    if 'badges' in clues:
                        line(screen, 9, 'This older checkpoint has plain badges in ACCESS NOTES.')
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')) or ready and key in (10, 13, curses.KEY_ENTER):
            return
        if not ready:
            continue
        if key in (9, curses.KEY_RIGHT, curses.KEY_DOWN):
            page = (page + 1) % len(titles)
        elif key in (curses.KEY_LEFT, curses.KEY_UP):
            page = (page - 1) % len(titles)


# Read up to 45 printable ASCII characters with editing and hints; return None on cancellation.
def read_command(screen, title, clues, prompt_lines, hints):
    """Return a submitted string, or None on Escape; retain input on resize."""
    answer = ''
    hint = -1
    screen.timeout(-1)
    while True:
        ready = frame(screen, title, clues, 'Enter: submit    F1: hint    Tab: notebook    Esc: back')
        if ready:
            for y, message in enumerate(wrap_lines(prompt_lines, CONTENT_WIDTH)[:12], 4):
                line(screen, y, message)
            line(screen, 16, 'Your response', curses.A_DIM)
            line(screen, 17, '> ' + answer + '_', curses.color_pair(1))
            if hint < 0 and 'cells' in clues:
                text(screen, 21, 5, 'Wrong answers cost 1 cell. Hints and cancelling are free.')
            if hint >= 0:
                for y, message in enumerate(wrap_lines(hints[hint], 70)[:3], 19):
                    text(screen, y, 5, message)
            screen.refresh()
        key = screen.getch()
        if key == 27:
            return None
        if not ready:
            if key in (ord('q'), ord('Q')):
                return None
            continue
        if key == 9:
            show_notes(screen, clues)
        elif key == curses.KEY_F1:
            hint = min(hint + 1, len(hints) - 1)
        elif key in (10, 13, curses.KEY_ENTER):
            return answer.strip()
        elif key in (curses.KEY_BACKSPACE, 8, 127):
            answer = answer[:-1]
        elif 32 <= key <= 126 and len(answer) < 45:
            answer += chr(key)


# Show a message and wait for acknowledgement; disable continuation while the terminal is too small.
def notice(screen, title, clues, messages):
    screen.timeout(-1)
    while True:
        ready = frame(screen, title, clues, 'Enter: continue    Tab: notebook    Esc: back')
        if ready:
            for y, message in enumerate(wrap_lines(messages, CONTENT_WIDTH)[:13], 5):
                line(screen, y, message)
            screen.refresh()
        key = screen.getch()
        if ready and key == 9:
            show_notes(screen, clues)
        if key in (27, ord('q'), ord('Q')) or ready and key in (10, 13, curses.KEY_ENTER):
            return
