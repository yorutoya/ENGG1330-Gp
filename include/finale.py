# Three exit challenges share one input loop and retain their state when returning to the map.
"""Three small exit challenges. Rules are turn-based and use only curses."""
import curses
from include.interface import frame, line, text, show_notes, DIRECTIONS
from include.expedition import lose_cell


# Rescue-route antenna puzzle: rotating one antenna also turns its neighbour.
class Relay:
    title = 'EXIT / SIGNAL RELAY'
    controls = '1/2/3: turn antenna    Enter: transmit    Tab: notes    Q: back'

    # Scramble a solved configuration using legal rotations so every starting state remains solvable.
    def __init__(self, seed):
        self.dials = [0, 0, 0]
        self.won = False
        for index in range(3):
            for _ in range(1 + (seed // (4 ** index)) % 3):
                self.turn(index)
        if self.dials == [0, 0, 0]:
            self.turn(0)
        self.message = 'The reply is faint. Align all antennas UP before transmitting.'

    # Rotate the selected antenna and its next neighbour clockwise through four directions.
    def turn(self, index):
        self.dials[index] = (self.dials[index] + 1) % 4
        neighbour = (index + 1) % 3
        self.dials[neighbour] = (self.dials[neighbour] + 1) % 4

    # Handle rotation or transmission; a bad transmission reports failure for the shared loop to charge.
    def act(self, action):
        if action in ('1', '2', '3'):
            self.turn(int(action) - 1)
            locked = self.dials.count(0)
            self.message = ('Static only.', 'A voice breaks through.',
                            'The rescue team can almost hear you.',
                            'Clear signal. Press Enter to send the location.')[locked]
        elif action == 'submit':
            if self.dials == [0, 0, 0]:
                self.won = True
            else:
                self.message = f'{self.dials.count(0)}/3 aligned. Each control also turns its neighbour.'
                return 'failure'

    # Draw antenna directions and coupling rules without changing the puzzle state.
    def draw(self, screen):
        line(screen, 5, 'Coupled gears: 1 turns 1+2, 2 turns 2+3, 3 turns 3+1.')
        for index, value in enumerate(self.dials):
            x = 14 + index * 22
            style = curses.color_pair(1 if value == 0 else 2)
            text(screen, 9, x, f'ANTENNA {index + 1}')
            text(screen, 11, x + 3, '[ ' + '^>v<'[value] + ' ]', style | curses.A_BOLD)
            text(screen, 14, x + 2, 'LOCKED' if value == 0 else 'DRIFT', style)
        line(screen, 17, 'Target: all ^. Turning is free; a bad transmission costs one cell.')


# Corridor map: C is permanent cover and E is the exit; scans cycle through SCAN_COLUMNS.
CORRIDOR = (
    '###########',
    '#...#....E#',
    '#...#.#.C.#',
    '#..C..#...#',
    '#.#....C..#',
    '#....C....#',
    '###########',
)
SCAN_COLUMNS = (3, 5, 7, 8)


# Solo escape corridor: each valid move or wait advances the scanner by one phase.
class Corridor:
    title = 'EXIT / WATCHFUL CORRIDOR'
    controls = 'Arrows/WASD: move    Space: wait    Tab: notes    Q: back'

    # Set the seeded initial scan phase and place the player at the fixed entrance.
    def __init__(self, seed):
        self.start_phase = seed % 4
        self.player = (1, 1)
        self.phase = self.start_phase
        self.won = False
        self.message = 'Power has restarted the scanners. Watch the NEXT sweep.'

    # Check whether the scan covers a position in this phase; walls and cover are safe.
    def danger(self, position, phase):
        x, y = position
        return x == SCAN_COLUMNS[phase] and CORRIDOR[y][x] not in '#C'

    # Validate the action, advance the scan and check detection; reset to the entrance on detection.
    def act(self, action):
        if action == 'wait':
            dx, dy = 0, 0
        elif isinstance(action, tuple):
            dx, dy = action
        else:
            return
        target = (self.player[0] + dx, self.player[1] + dy)
        x, y = target
        if not (0 <= y < len(CORRIDOR) and 0 <= x < len(CORRIDOR[0])) or CORRIDOR[y][x] == '#':
            self.message = 'Wall. No movement or scan tick was spent.'
            return
        self.phase = (self.phase + 1) % 4
        if self.danger(target, self.phase):
            self.player = (1, 1)
            self.phase = self.start_phase
            self.message = 'Detected. Back at the entrance; avoid the marked NEXT sweep.'
            return 'failure'
        self.player = target
        self.won = CORRIDOR[y][x] == 'E'
        self.message = 'Cover shields you from every sweep.' if CORRIDOR[y][x] == 'C' else 'One beat passed. Study the next sweep before moving.'

    # Show both current and next scans so the player can plan before acting.
    def draw(self, screen):
        line(screen, 4, f'Scan beat {self.phase + 1}/4. Movement and waiting advance one beat.')
        for y, row in enumerate(CORRIDOR):
            for x, tile in enumerate(row):
                pos = (x, y)
                style = curses.A_DIM
                if tile != '#':
                    if self.danger(pos, (self.phase + 1) % 4):
                        tile, style = '!', curses.color_pair(2)
                    elif self.danger(pos, self.phase):
                        tile, style = ':', curses.color_pair(3)
                    elif tile in 'CE':
                        style = curses.color_pair(1)
                if pos == self.player:
                    tile, style = '@', curses.color_pair(1) | curses.A_BOLD
                text(screen, y + 7, x * 3 + 24, tile, style)
        line(screen, 16, '@ you    ! next sweep    : current sweep    C cover    E exit')
        line(screen, 18, 'Time moves only when you act. Detection costs one cell.')


# Battery escape shaft: one battery supplies the light, bridge motor or lift at a time.
class Shaft:
    title = 'EXIT / EMERGENCY POWER SHAFT'
    controls = '1/2/3: power  Space: align  Arrows: walk  Enter: lift  Tab: notes  Q: back'

    # Choose the safe bridge position from the seed and start an attempt with seven charge.
    def __init__(self, seed):
        self.target = 1 + seed % 2
        self.won = False
        self.reset()
        self.message = 'One battery, three devices. Scan the ledge before building a path.'

    # Reset local charge and equipment for this attempt without replenishing shared run cells.
    def reset(self):
        self.energy = 7
        self.device = 0
        self.bridge = 0
        self.position = 0
        self.scanned = False

    # Handle connections, bridge alignment, walking and lift launch; report failure when charge runs out.
    def act(self, action):
        if action in ('1', '2', '3'):
            device = int(action)
            if self.position != 0:
                self.message = 'Battery sockets are at the dock. Walk back to reconnect.'
                return
            if device == self.device:
                self.message = 'Already connected. No charge used.'
                return
            self.device = device
            self.energy -= 1
            if device == 1:
                self.scanned = True
                self.message = f'Light reveals ledge {self.target}. The marking is now recorded.'
            elif device == 2:
                self.message = 'Bridge motor online. Space cycles alignment 0 > 1 > 2.'
            else:
                self.message = 'Lift online. Cross the latched bridge, then press Enter.'
        elif action == 'wait':
            if self.device != 2 or self.position != 0:
                self.message = 'Align from the dock with the bridge motor connected.'
                return
            self.bridge = (self.bridge + 1) % 3
            self.energy -= 1
            self.message = 'Alignment set. The mechanical latch holds without power.'
        elif isinstance(action, tuple):
            dx, dy = action
            if dy or dx == 0:
                return
            target = self.position + dx
            if not 0 <= target <= 2:
                return
            if not self.scanned or self.bridge != self.target:
                self.message = 'No safe crossing. Scan the ledge and align the bridge first.'
                return
            self.position = target
            self.message = 'Walking uses no charge. Battery sockets remain at the dock.'
        elif action == 'submit':
            if self.position != 2 or self.device != 3:
                self.message = 'Stand on the lift with its cable connected.'
                return
            self.energy -= 1
            self.won = True
            return
        if self.energy <= 0:
            self.reset()
            self.message = 'Battery depleted. One cell restarts the shaft with 7 charge.'
            return 'failure'

    # Draw remaining charge, connected equipment, bridge alignment and player position.
    def draw(self, screen):
        devices = ('none', 'light', 'bridge motor', 'lift')
        line(screen, 5, f'Charge {self.energy}/7    Connected: {devices[self.device]}')
        line(screen, 8, '[1] LIGHT          [2] BRIDGE MOTOR          [3] LIFT')
        line(screen, 10, 'Dock  ----------------  Bridge  ----------------  Lift')
        text(screen, 12, (6, 30, 57)[self.position], '@', curses.color_pair(1) | curses.A_BOLD)
        target = str(self.target) if self.scanned else '? (connect light to inspect)'
        line(screen, 15, f'Bridge alignment: {self.bridge}    Safe ledge: {target}')
        line(screen, 17, 'Connect / align / launch: 1 charge each. Walking and notes are free.')
        line(screen, 18, 'Aligned bridges stay latched even after their power is disconnected.')


# Create the challenge for the committed ending using the current run seed.
def make_room(kind, seed):
    if kind == 'DAWN':
        return Relay(seed)
    if kind == 'SILENT EXIT':
        return Corridor(seed)
    return Shaft(seed)


# Share input handling and failure costs; store the room in clues so leaving does not reset it.
def play(screen, clues, kind):
    # Keep the room object on return to the map: no free battery refill on Q.
    if 'exit_room' not in clues:
        clues['exit_room'] = make_room(kind, clues.get('seed', 0))
    room = clues['exit_room']
    screen.timeout(-1)
    while clues.get('cells', 3) > 0:
        if room.won:
            return True
        ready = frame(screen, room.title, clues, room.controls)
        if ready:
            room.draw(screen)
            line(screen, 20, room.message, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return False
        if not ready or key == curses.KEY_RESIZE:
            continue
        if key == 9:
            show_notes(screen, clues)
            continue
        # Translate keys into direction tuples or action names; unknown keys do not advance the puzzle.
        action = DIRECTIONS.get(key)
        if key in (10, 13, curses.KEY_ENTER):
            action = 'submit'
        elif key == ord(' '):
            action = 'wait'
        elif key in (ord('1'), ord('2'), ord('3')):
            action = chr(key)
        # Apply reported failures here so all challenges share the same cell and fuse rules.
        if room.act(action) == 'failure':
            lose_cell(clues)
    return False
