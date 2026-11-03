# Run rules for sector variation, shared cells, module rewards and resource costs.
"""Small run rules shared by the four rooms. No extra libraries."""
from include.interface import frame, line

# The seed selects the sector; module names and descriptions share indices for the reward menu.
CONDITIONS = ('STABLE', 'POWER LEAK', 'INTERFERENCE')
MODULES = ('Spare cell', 'Capacitor', 'Surge fuse')
DESCRIPTIONS = (
    'Add one emergency cell (maximum 5).',
    'Add 120 charge to each circuit attempt.',
    'Absorb the next cell loss; then the fuse breaks.',
)


# Start with three cells; modules and bonus charge do not carry over from the previous expedition.
def new_run(seed):
    return {'seed': seed, 'cells': 3, 'condition': CONDITIONS[seed % 3],
            'bonus_charge': 0, 'fuse': False, 'modules': []}


# Calculate circuit charge from the base budget, capacitor bonuses and any power leak penalty.
def circuit_charge(clues):
    charge = 420 + clues.get('bonus_charge', 0)
    if clues.get('condition') == 'POWER LEAK':
        charge -= 80
    return charge


# Return the gate handshake order, using a different sequence in an interference sector.
def power_sequence(clues):
    if clues.get('condition') == 'INTERFERENCE':
        return (3, 1, 2)
    return (2, 3, 1)


# Absorb a loss with the fuse first; otherwise subtract one cell without going below zero.
def lose_cell(clues):
    """Costs persist through room exits, retries and undo."""
    if clues.get('fuse', False):
        clues['fuse'] = False
        return 'Surge fuse absorbed the loss.'
    clues['cells'] = max(0, clues.get('cells', 3) - 1)
    return f'Emergency cells remaining: {clues["cells"]}.'


# Install and record a module: 0 adds a cell, 1 adds circuit charge, and 2 protects against one loss.
def apply_module(clues, module):
    if module == 0:
        clues['cells'] = min(5, clues.get('cells', 3) + 1)
    elif module == 1:
        clues['bonus_charge'] = clues.get('bonus_charge', 0) + 120
    else:
        clues['fuse'] = True
    clues.setdefault('modules', []).append(MODULES[module])


# Offer two rewards; after the circuit, offer only cells and fuses because circuit charge is no longer useful.
def reward(screen, clues, stage):
    """One two-item offer per completed room. Esc skips it permanently."""
    first = (clues.get('seed', 0) + stage) % 3
    # Once the circuit is repaired, extra circuit charge has no further use.
    offers = (0, 2) if stage == 2 else (first, (first + 1) % 3)
    screen.timeout(-1)
    while True:
        ready = frame(screen, 'SALVAGE / TAKE ONE MODULE', clues,
                      '1/2: install module | Esc/Q: leave the salvage')
        if ready:
            line(screen, 5, 'Supplies for the gate and exit passage.' if stage == 2
                 else 'A maintenance cache contains two usable modules.')
            for index, module in enumerate(offers):
                line(screen, 8 + index * 4, f'[{index + 1}] {MODULES[module]}')
                line(screen, 9 + index * 4, DESCRIPTIONS[module])
            line(screen, 17, 'Leaving this cache forfeits its unclaimed module.')
            line(screen, 18, 'Modules last only for this expedition.')
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if ready and key in (ord('1'), ord('2')):
            apply_module(clues, offers[key - ord('1')])
            return
