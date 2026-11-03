# Room 3: route the energy snake using drawer clues and recover the gate terminal sequence.
"""Lock 3: energy snake with the drawer's repeating fuse order."""
import curses
from include.interface import frame, line, text, notice, show_notes, DIRECTIONS
from include.expedition import circuit_charge, power_sequence, lose_cell

# These are logical grid dimensions; each cell occupies two terminal columns when drawn.
WIDTH, HEIGHT = 24, 14
TARGET, CHARGE = 6, 420



# Keep snake, node, charge and movement state separate from terminal drawing.
class EnergyCircuit:
    """Keep the snake state and movement rules together; no drawing here."""
    # Initialize the snake, direction, target order and charge budget for this attempt.
    def __init__(self, order, charge=CHARGE, seed=0):
        self.order = tuple(order)
        self.snake = [(6, 7), (5, 7), (4, 7)]
        self.direction = (1, 0)
        self.score = 0
        self.charge = charge
        self.seed = seed
        self.status = 'ready'
        self.nodes = {}
        self.spawn_nodes()

    # Cycle through the required colours using the score modulo the order length.
    @property
    def expected(self):
        return self.order[self.score % len(self.order)]

    # Place nodes away from the snake; seed and score make each layout varied but reproducible.
    def spawn_nodes(self):
        x, y = self.snake[0]
        free = []
        for cy in range(1, HEIGHT - 1):
            for cx in range(1, WIDTH - 1):
                distance = abs(cx - x) + abs(cy - y)
                if (cx, cy) not in self.snake and distance > 2:
                    free.append((cx, cy))
        self.nodes = {}
        for index, colour in enumerate(self.order):
            # Spread nodes across the board without needing a random library.
            position = (self.seed + self.score * 53 + index * 41 + 17) % len(free)
            self.nodes[colour] = free.pop(position)

    # Advance one move, spend charge and check collisions, wrong colours and the six-node target.
    def step(self, direction=None):
        if self.status != 'running':
            return
        if direction is not None and direction != (-self.direction[0], -self.direction[1]):
            self.direction = direction
        self.charge -= 1
        x, y = self.snake[0]
        head = (x + self.direction[0], y + self.direction[1])
        colour = None
        for name, position in self.nodes.items():
            if position == head:
                colour = name
                break
        # The tail moves away unless a node is collected, so its old cell is safe only on non-growing moves.
        body = self.snake if colour else self.snake[:-1]
        if not (0 < head[0] < WIDTH - 1 and 0 < head[1] < HEIGHT - 1) or head in body:
            self.status = 'collision'
        elif colour and colour != self.expected:
            self.status = 'short circuit'
        else:
            self.snake.insert(0, head)
            if colour:
                self.score += 1
                if self.score == TARGET:
                    self.status = 'won'
                else:
                    self.spawn_nodes()
            else:
                self.snake.pop()
        if self.charge <= 0 and self.status == 'running':
            self.status = 'out of charge'


# Handle drawing, input and pausing; failures and abandoned active attempts cost a run cell.
def main(screen, clues):
    if 'order' not in clues:
        return False
    circuit = EnergyCircuit(clues['order'], circuit_charge(clues), clues.get('seed', 0))
    while True:
        ready = frame(screen, '03 / ENERGY CIRCUIT', clues,
                      'Arrows: steer    Space: pause    Tab: notebook    R: retry    Q: back')
        if not ready and circuit.status == 'running':
            circuit.status = 'paused'
        if ready:
            line(screen, 4, f'Nodes {circuit.score}/{TARGET}    Charge {circuit.charge}    Next {circuit.expected}    {circuit.status.upper()}')
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    char = '#' if x in (0, WIDTH - 1) or y in (0, HEIGHT - 1) else '.'
                    text(screen, y + 6, x * 2 + 16, char, curses.A_DIM)
            for colour, (x, y) in circuit.nodes.items():
                text(screen, y + 6, x * 2 + 16, colour, curses.A_BOLD | curses.color_pair({'A': 2, 'C': 1, 'V': 3}[colour]))
            for index, (x, y) in enumerate(circuit.snake):
                text(screen, y + 6, x * 2 + 16, '@' if index == 0 else 'o', curses.color_pair(1))
            if circuit.status == 'ready':
                text(screen, 21, 5, 'Space to begin. Failure or abandoning after movement costs 1 cell.')
            else:
                text(screen, 21, 5, 'Each movement uses one charge. Pause to plan a route.')
            if circuit.status not in ('ready', 'running', 'paused'):
                text(screen, 21, 5, 'Circuit failed. Press R to retry; earlier clues are safe.')
            screen.refresh()
        # One movement every 160 ms, regardless of how fast keys are pressed.
        if circuit.status == 'running':
            curses.napms(160)
            screen.timeout(0)
        else:
            screen.timeout(-1)
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            if circuit.status in ('running', 'paused') and circuit.charge < circuit_charge(clues):
                lose_cell(clues)
            screen.timeout(-1)
            return False
        if key == curses.KEY_RESIZE:
            if circuit.status == 'running':
                circuit.status = 'paused'
            continue
        if not ready:
            continue
        if key == 9:
            if circuit.status == 'running':
                circuit.status = 'paused'
            show_notes(screen, clues)
        elif key in (ord('r'), ord('R')):
            if circuit.status in ('running', 'paused') and circuit.charge < circuit_charge(clues):
                lose_cell(clues)
                if clues.get('cells', 3) <= 0:
                    return False
            circuit = EnergyCircuit(clues['order'], circuit_charge(clues), clues.get('seed', 0))
        elif key == ord(' '):
            if circuit.status in ('ready', 'paused'):
                circuit.status = 'running'
            elif circuit.status == 'running':
                circuit.status = 'paused'
        elif circuit.status == 'running':
            circuit.step(DIRECTIONS.get(key))
            if circuit.status == 'won':
                clues['sequence'] = power_sequence(clues)
                notice(screen, '03 / POWER RESTORED', clues, [
                    'The gate controller returns an archived access log:', '',
                    'TERMINAL HANDSHAKE: ' + ' > '.join(map(str, clues['sequence'])),
                    'ACCESS: each terminal has its own badge formula.',
                    'INTERLOCK: both matching pressure plates must stay on.', '',
                    'The final security room is now accessible.',
                ])
                return True
            # Charge for failure once here; leaving or restarting this failed attempt must not charge again.
            if circuit.status not in ('running', 'won'):
                lose_cell(clues)
                if clues.get('cells', 3) <= 0:
                    return False
