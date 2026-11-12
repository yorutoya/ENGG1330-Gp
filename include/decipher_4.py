# Room 4: power the gate with crates, verify terminals and influence the escape through radio actions.
"""Lock 4: matching crates, powered doors, and sequenced identity checks."""
import curses
from include.interface import frame, line, text, read_command, show_notes, DIRECTIONS
from include.expedition import lose_cell
# Static map: # marks walls, D controlled doors and E the exit; draw other objects as overlays.
MAP = (
    '#############',
    '#......#...E#',
    '#....#.#....#',
    '#.#....D....#',
    '#......#....#',
    '#...#..D....#',
    '#......#....#',
    '#......#....#',
    '#############',
)
# Positions use logical (x, y) grid coordinates, converted to terminal coordinates when drawn.
START = (1, 4)
BOXES = {'A': (3, 4), 'B': (5, 4)}
PLATES = {'A': (3, 2), 'B': (3, 6)}
TERMINALS = {1: (9, 2), 2: (10, 4), 3: (9, 6)}
EXIT = (11, 1)
RADIO = (11, 6)
ALARM = (1, 1)


FORMULAS = {1: 'A + offset', 2: 'C - offset', 3: 'V + 2 x offset'}


# Combine the drawer badges and console offset to calculate a separate code for each terminal.
def terminal_keys(clues):
    badges = clues['badges']
    offset = clues['shift']
    return {1: badges['A'] + offset, 2: badges['C'] - offset,
            3: badges['V'] + 2 * offset}


# Track crates, player position, terminal checks and radio state, with undoable room actions.
class GatePuzzle:
    """Room state and rules. main() below only handles drawing and keys."""
    # Validate the terminal order; bypass=True uses battery power because the circuit was not repaired.
    def __init__(self, sequence=(2, 1, 3), bypass=False):
        if sorted(sequence) != [1, 2, 3]:
            raise ValueError('Terminal sequence must be a permutation of 1, 2, 3')
        self.bypass = bypass
        self.sequence = tuple(sequence)
        self.player = START
        self.boxes = dict(BOXES)
        self.entered = []
        self.authorized = False
        self.history = []
        self.moves = 0
        self.won = False
        self.radio = 'idle'

    # Battery mode needs only A on a; mains mode requires both crates on their matching plates.
    @property
    def powered(self):
        if self.bypass:
            return self.boxes['A'] == PLATES['A']
        for name, position in PLATES.items():
            if self.boxes[name] != position:
                return False
        return True

    # Check map bounds and walls; controlled doors can be crossed only while the plates provide power.
    def walkable(self, pos):
        x, y = pos
        if not (0 <= y < len(MAP) and 0 <= x < len(MAP[y])):
            return False
        if MAP[y][x] == '#':
            return False
        if MAP[y][x] == 'D' and not self.powered:
            return False
        return True

    # Snapshot the room before an action, excluding run cells so undo cannot refund resources.
    def snapshot(self):
        self.history.append((self.player, dict(self.boxes), list(self.entered),
                             self.authorized, self.moves, self.won, self.radio))

    # Restore the previous valid action, including crates, terminal progress and radio operations.
    def undo(self):
        if self.history:
            (self.player, self.boxes, self.entered, self.authorized,
             self.moves, self.won, self.radio) = self.history.pop()

    # Move or push a crate; losing power clears verification, and a powered, verified exit completes the room.
    def move(self, direction):
        if self.won:
            return 'Evacuation is complete.'
        dx, dy = direction
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self.walkable(target):
            return 'Blocked by a wall or closed door. H: how to open the doors.'
        box = None
        for name, position in self.boxes.items():
            if position == target:
                box = name
                break
        if box:
            destination = (target[0] + dx, target[1] + dy)
            if not self.walkable(destination) or destination in self.boxes.values():
                return 'The crate cannot move there. U: undo a previous move.'
        if target == EXIT and not (self.powered and self.authorized):
            return 'Exit locked. Keep the plates pressed and unlock all 3 terminals.'
        self.snapshot()
        if box:
            self.boxes[box] = destination
        self.player = target
        self.moves += 1
        if not self.powered:
            self.entered = []
            self.authorized = False
        self.won = self.player == EXIT
        if self.won:
            return 'Exit reached!'
        if self.powered:
            return 'Doors open. Keep the boxes in place. Use terminals 1, 2 and 3.'
        if self.bypass:
            return 'Battery power: use A on a. Plate b needs mains power from room 3.'
        return 'Push box A onto a and box B onto b. You cannot pull boxes.'

    # Check the nearby terminal code and order; wrong order clears progress, while the input loop handles costs.
    def activate(self, key, expected_keys):
        if self.won:
            return 'Evacuation is complete.'
        nearby = self.terminal_nearby()
        if nearby is None:
            return 'Stand on or next to a numbered terminal first.'
        if not self.powered:
            return 'The required plates must be powered.'
        if str(key).strip() != str(expected_keys[nearby]):
            return "Wrong code. Combine the badge with this terminal's rule."
        if self.authorized:
            return 'Already verified. Proceed to exit E.'
        self.snapshot()
        if nearby != self.sequence[len(self.entered)]:
            self.entered = []
            return f'Wrong terminal. Start again at terminal {self.sequence[0]}. Tab: order.'
        self.entered.append(nearby)
        self.authorized = len(self.entered) == 3
        if self.authorized:
            return 'All 3 terminals unlocked. Walk to E when ready to leave.'
        return f'Terminal {nearby} accepted ({len(self.entered)}/3).'

    # Find a terminal on or beside the player, returning None when none is within reach.
    def terminal_nearby(self):
        for number, position in TERMINALS.items():
            if self.near(position):
                return number
        return None

    # Use Manhattan distance to include the same cell and orthogonal neighbours, but not diagonals.
    def near(self, position):
        return abs(self.player[0] - position[0]) + abs(self.player[1] - position[1]) <= 1

    # Operate F or O: cutting the shared feed disables rescue calls; mains power allows transmission.
    def operate(self):
        """E operates the nearby fixture. None means use a security terminal."""
        # Radio states: idle means no call, cut means disconnected, sent means transmitted; undo restores them.
        if self.near(ALARM):
            if self.radio == 'sent':
                return 'F is locked: keep the rescue transmission powered.'
            if self.radio == 'cut':
                return 'The alarm and radio feed are already disconnected.'
            self.snapshot()
            self.radio = 'cut'
            return 'Alarm silenced; O disconnected. No rescue call. U: undo.'
        if self.near(RADIO):
            if self.radio == 'cut':
                return 'O has no power: F cut its shared feed. No rescue contact.'
            if self.bypass or not self.powered:
                return 'Radio needs mains power and both pressure plates.'
            if self.radio == 'sent':
                return 'Rescuers have your location. Complete the relay beyond the gate.'
            self.snapshot()
            self.radio = 'sent'
            return 'Rescue team: "Location received. Reach the relay to guide us in."'
        return None

    # Explain equipment consequences using current power and radio state without presenting ending choices.
    def fixture_hint(self):
        """Explain equipment consequences without offering an ending menu."""
        if self.bypass:
            consequence = 'No mains power: escape alone through the emergency shaft.'
        elif self.radio == 'sent':
            consequence = 'Rescue contact made. Finish the exit relay to reach the team.'
        else:
            consequence = 'No rescue contact: the powered exit leads to a scanner corridor.'
        if self.near(ALARM):
            if self.radio == 'sent':
                return 'F locked: the alarm feed now powers your rescue call.', consequence
            if self.radio == 'cut':
                return 'F disconnected: alarm silent; O cannot call rescuers.', consequence
            return 'Press E here to cut F: stop the alarm AND disable radio O.', consequence
        if self.near(RADIO):
            if self.radio == 'cut':
                return 'O offline: cutting F also disconnected the rescue radio.', consequence
            if self.bypass:
                return 'O needs mains power. Return to repair the circuit first.', consequence
            if not self.powered:
                return 'O needs both crates on their plates before it can call rescue.', consequence
            if self.radio == 'sent':
                return 'O transmitting: the rescue team has your coordinates.', consequence
            return 'Press E here to use O: send your location to rescuers.', consequence
        if not self.powered:
            task = 'Next: push box A onto a.' if self.bypass else 'Next: push box A onto a and box B onto b.'
        elif not self.authorized:
            task = f'Next: find terminal {self.sequence[len(self.entered)]} and press E beside it.'
        else:
            task = 'Gate unlocked. Visit O for rescue, or walk to exit E.'
        return task, consequence


# Explain one topic per page so help remains readable within the fixed viewport.
def show_help(screen, clues, gate):
    order = ' > '.join(map(str, gate.sequence))
    pages = (
        ('1/3 / MOVE THE BOXES', [
            'Goal: open the doors, unlock 3 terminals, then walk to exit E.', '',
            '@ is you. CAPITAL A/B are boxes. Small a/b are floor plates.',
            'Stand beside a box. Walk INTO it to push it away from you.',
            'You cannot pull a box. Press U if a push puts it in the wrong place.', '',
            'Battery power runs plate a only. Push box A onto a.' if gate.bypass
            else 'Mains power needs BOTH plates: push A onto a and B onto b.',
            'Plate b works after room 3 is repaired; it then needs box B.',
            'Leave the required boxes on their plates to keep the doors open.',
            'D is a closed door. / is an open door.',
        ]),
        ('2/3 / UNLOCK THE TERMINALS', [
            'Use the numbered terminals in this order: ' + order, '',
            'Stand ON or BESIDE a terminal, then press the E key.',
            'Enter its numeric code. Each terminal has a DIFFERENT code.', '',
            'Terminal 1: badge A + offset',
            'Terminal 2: badge C - offset',
            'Terminal 3: badge V + (2 x offset)', '',
            'Tab: BADGE CLUES explains how to decode the stamped numbers.',
            'Decode each stamp, mirror the letters, then add their A1Z26 values.',
            'A wrong code or wrong terminal order costs 1 emergency cell.',
        ]),
        ('3/3 / RADIO, ALARM AND EXIT', [
            'O and F are map symbols. Stand nearby and press E to use them.', '',
            'O = rescue radio. It sends your location to a rescue team.',
            'It works only after room 3 is repaired AND both plates are pressed.',
            'Calling rescue leads to an antenna challenge beyond the gate.', '',
            'F = alarm switch. Using it stops the alarm but also disables O.',
            'With room 3 repaired but no call, you escape via a scanner corridor.',
            'If room 3 was skipped, the exit leads to a battery-powered shaft.', '',
            'F and O are optional. Neither replaces the 3 terminal checks.',
            'U undoes actions. Walking onto exit E locks in your escape route.',
        ]),
    )
    page = 0
    screen.timeout(-1)
    while True:
        title, messages = pages[page]
        ready = frame(screen, 'GATE HELP / ' + title, clues,
                      'Left/Right: page    Enter: next/close    H/Esc/Q: close')
        if ready:
            for y, message in enumerate(messages, 5):
                line(screen, y, message)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')) or ready and key in (ord('h'), ord('H')):
            return
        if not ready:
            continue
        if key in (10, 13, curses.KEY_ENTER):
            if page == len(pages) - 1:
                return
            page += 1
        elif key == curses.KEY_RIGHT:
            page = min(page + 1, len(pages) - 1)
        elif key == curses.KEY_LEFT:
            page = max(0, page - 1)


# Handle this room and its input; write radio back to shared clues only after reaching the exit.
def main(screen, clues):
    if 'order' not in clues or 'shift' not in clues or 'badges' not in clues:
        return False
    keys = terminal_keys(clues)
    bypass = 'sequence' not in clues
    # The room uses current power conditions. Leaving lets you repair power.
    # Use a display copy for battery wiring so its sequence is not mistaken for evidence of repaired power.
    display_clues = dict(clues)
    display_clues['emergency'] = bypass
    if bypass:
        numbers = {'A': 1, 'C': 2, 'V': 3}
        sequence = []
        for colour in reversed(clues['order']):
            sequence.append(numbers[colour])
        display_clues['sequence'] = tuple(sequence)
    gate = GatePuzzle(display_clues['sequence'], bypass)
    message = 'Push A onto a and B onto b. H: step-by-step help.'
    if bypass:
        message = 'Battery powers only a. Plate b needs room 3 repaired. H: help.'
    screen.timeout(-1)
    while True:
        display_clues.update(clues)
        ready = frame(screen, '04 / SECURITY INTERLOCK', display_clues,
                      'Arrows: move  E: use  Tab: notes  U: undo  R: reset  H: help  Q: back')
        if ready:
            required = 1 if bypass else 2
            plates = 0
            for name, position in PLATES.items():
                if name == 'B' and bypass:
                    continue
                if gate.boxes[name] == position:
                    plates += 1
            line(screen, 4, f'Moves {gate.moves} | Plates {plates}/{required} | Terminals {len(gate.entered)}/3')
            # Draw the room, then overlay plates, terminals, crates and player.
            for y, row in enumerate(MAP):
                for x, char in enumerate(row):
                    style = curses.A_DIM
                    if char == 'D':
                        char = '/' if gate.powered else 'D'
                        style = curses.color_pair(2)
                    text(screen, y + 6, x * 3 + 21, char, style)
            for name, (x, y) in PLATES.items():
                text(screen, y + 6, x * 3 + 21, name.lower(), curses.color_pair(1))
            for number, (x, y) in TERMINALS.items():
                colour = 1 if number in gate.entered else 3
                text(screen, y + 6, x * 3 + 21, str(number), curses.color_pair(colour))
            for name, (x, y) in gate.boxes.items():
                text(screen, y + 6, x * 3 + 21, name, curses.color_pair(2) | curses.A_BOLD)
            for symbol, (x, y) in (('O', RADIO), ('F', ALARM)):
                text(screen, y + 6, x * 3 + 21, symbol, curses.color_pair(3))
            x, y = gate.player
            text(screen, y + 6, x * 3 + 21, '@', curses.color_pair(1) | curses.A_BOLD)
            line(screen, 16, '@ you  A/B crates  a/b plates  D doors  E exit  O radio  F alarm')
            number = gate.terminal_nearby()
            context, consequence = gate.fixture_hint()
            if number is not None and not gate.near(ALARM) and not gate.near(RADIO):
                context = f'Press E for terminal {number}. Code = badge ' + FORMULAS[number]
            line(screen, 18, context, curses.color_pair(1) | curses.A_BOLD)
            line(screen, 20, consequence)
            text(screen, 19, 5, message, curses.color_pair(2))
            if gate.near(ALARM) or gate.near(RADIO):
                line(screen, 21, 'U: undo actions step by step. Crossing exit E commits this route.', curses.A_DIM)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return False
        if not ready:
            continue
        if key == 9:
            show_notes(screen, display_clues)
        elif key in DIRECTIONS:
            message = gate.move(DIRECTIONS[key])
            if gate.won:
                clues['radio'] = gate.radio
                return True
        elif key in (ord('u'), ord('U')):
            gate.undo()
            message = 'Last valid move or terminal activation undone.'
        elif key in (ord('r'), ord('R')):
            gate = GatePuzzle(display_clues['sequence'], bypass)
            message = 'Room reset. All earlier clues remain in the journal.'
        elif key in (ord('h'), ord('H')):
            show_help(screen, display_clues, gate)
        elif key in (ord('e'), ord('E')):
            result = gate.operate()
            if result is not None:
                message = result
                continue
            number = gate.terminal_nearby()
            if number is None:
                message = 'No device in reach. Move beside a numbered terminal, O or F.'
                continue
            badge = 'ACV'[number - 1]
            evidence = (f'Badge {badge} stamp: ' + clues['badge_stamps'][badge]
                        if 'badge_stamps' in clues else
                        f'Badge {badge}: {clues["badges"][badge]}')
            hints = [
                ['First use the drawer rule on each stamped number.',
                 'Subtract the room 1 offset. Add 26 if the result is below 1.',
                 'Convert the results to letters with A=1 ... Z=26.'],
                ['Now use the mirror alphabet from room 1 on those letters.',
                 'A becomes Z, B becomes Y, and so on.'],
                ['Add the final letters using A=1 ... Z=26: this is the badge.',
                 'Example: final letters A B give 1+2=3. Your stamp may differ.',
                 "Finally apply this terminal's formula to that badge total."],
            ] if 'badge_stamps' in clues else [
                ['Use the printed badge number in the terminal formula.']]
            answer = read_command(screen, f'04 / TERMINAL {number} ACCESS', display_clues, [
                f'You are using terminal {number}. Enter a number, not a letter.', '',
                'Code = badge ' + FORMULAS[number],
                evidence,
                f'Offset from room 1: {clues["shift"]}', '',
                'Terminal order: ' + ' > '.join(map(str, gate.sequence)),
                'Tab: badge clues. F1: step-by-step decoding hints.',
                'A wrong code or wrong order costs 1 cell. Esc cancels for free.',
            ], hints)
            if answer is not None:
                if gate.powered and not gate.authorized:
                    wrong_code = answer.strip() != str(keys[number])
                    wrong_order = number != gate.sequence[len(gate.entered)]
                    if wrong_code or wrong_order:
                        lose_cell(clues)
                message = gate.activate(answer, keys)
                if clues.get('cells', 3) <= 0:
                    return False
