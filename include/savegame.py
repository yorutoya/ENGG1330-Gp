# Manual checkpoints: store a run as plain text and validate its format and state when loading.
"""One plain-text checkpoint, using built-in file I/O only (never eval)."""
from include import decipher_2, finale
from include.expedition import new_run, power_sequence, MODULES

# Keep the save in the project root so it is found regardless of the working directory.
SAVE_PATH = __file__.replace('\\', '/').rsplit('/', 2)[0] + '/progress.sav'


# Convert a field to an integer within bounds; raise ValueError for the UI to report invalid data.
def number(value, low, high):
    result = int(value)
    if not low <= result <= high:
        raise ValueError('Invalid checkpoint value')
    return result


# Encode resources, room completion and exit progress as twelve fixed lines rather than saving objects.
def encode(clues, solved, selected):
    room = clues.get('exit_room')
    state = '-'
    if isinstance(room, finale.Relay):
        state = room.dials + [int(room.won)]
    elif isinstance(room, finale.Corridor):
        state = [*room.player, room.phase, int(room.won)]
    elif isinstance(room, finale.Shaft):
        state = [room.energy, room.device, room.bridge, room.position,
                 int(room.scanned), int(room.won)]
    if state != '-':
        state = ','.join(map(str, state))
    # Line order: version, seed, cells, bonus charge, fuse, modules, completed rooms,
    # map selection, radio state, ending type, escaped flag, and exit challenge state.
    # A dash marks absent data; parsing converts values and never executes file contents.
    return '\n'.join((
        'UNDERGROUND SAVE 1', str(clues['seed']), str(clues['cells']),
        str(clues['bonus_charge']), str(int(clues['fuse'])),
        '|'.join(clues['modules']) or '-',
        ''.join(str(int(done)) for done in solved), str(selected),
        clues.get('radio', '-'), clues.get('finale_kind', '-'),
        str(int(clues.get('escaped', False))), state,
    )) + '\n'


# Validate fields and room prerequisites, then rebuild and return clues, solved and selected.
def decode(contents):
    fields = contents.splitlines()
    if len(fields) != 12 or fields[0] != 'UNDERGROUND SAVE 1':
        raise ValueError('Unsupported or incomplete checkpoint')
    seed = number(fields[1], 0, 7999)
    clues = new_run(seed)
    clues['cells'] = number(fields[2], 0, 5)
    clues['bonus_charge'] = number(fields[3], 0, 240)
    clues['fuse'] = bool(number(fields[4], 0, 1))
    clues['modules'] = [] if fields[5] == '-' else fields[5].split('|')
    if len(clues['modules']) > 2 or any(m not in MODULES for m in clues['modules']):
        raise ValueError('Invalid modules')
    if len(fields[6]) != 4 or any(c not in '01' for c in fields[6]):
        raise ValueError('Invalid room progress')
    solved = [c == '1' for c in fields[6]]
    if (solved[1] and not solved[0]) or (any(solved[2:]) and not solved[1]):
        raise ValueError('Missing earlier room')
    selected = number(fields[7], 0, 4)
    # Rebuild fixed clues from this run's seed and completed rooms.
    if solved[0]:
        clues['shift'] = 7
    if solved[1]:
        clues['order'] = decipher_2.make_order(seed)
        clues['badges'] = decipher_2.make_badges(seed)
    if solved[2]:
        clues['sequence'] = power_sequence(clues)
    if fields[8] not in ('-', 'idle', 'sent', 'cut'):
        raise ValueError('Invalid radio state')
    if fields[8] != '-':
        clues['radio'] = fields[8]
    escaped = bool(number(fields[10], 0, 1))
    if not solved[3]:
        if fields[8:10] != ['-', '-'] or escaped or fields[11] != '-':
            raise ValueError('Exit reached before gate')
        return clues, solved, selected
    expected = ('DAWN' if clues.get('radio') == 'sent' else 'SILENT EXIT') if solved[2] else 'LAST LIGHT'
    if fields[9] != expected or fields[11] == '-':
        raise ValueError('Invalid exit passage')
    clues['finale_kind'] = expected
    # Create the matching challenge before restoring mutable fields; code and seed define its fixed layout.
    room = finale.make_room(expected, seed)
    values = fields[11].split(',')
    if isinstance(room, finale.Relay):
        if len(values) != 4:
            raise ValueError('Invalid antenna state')
        room.dials = [number(v, 0, 3) for v in values[:3]]
    elif isinstance(room, finale.Corridor):
        if len(values) != 4:
            raise ValueError('Invalid corridor state')
        x, y = number(values[0], 0, 10), number(values[1], 0, 6)
        if finale.CORRIDOR[y][x] == '#':
            raise ValueError('Player inside wall')
        room.player = (x, y)
        room.phase = number(values[2], 0, 3)
    else:
        if len(values) != 6:
            raise ValueError('Invalid shaft state')
        room.energy = number(values[0], 0, 7)
        room.device = number(values[1], 0, 3)
        room.bridge = number(values[2], 0, 2)
        room.position = number(values[3], 0, 2)
        room.scanned = bool(number(values[4], 0, 1))
    room.won = bool(number(values[-1], 0, 1))
    if isinstance(room, finale.Shaft) and room.energy == 0 and not room.won:
        raise ValueError('Unfinished shaft without power')
    if escaped != room.won:
        raise ValueError('Incomplete ending')
    room.message = 'Progress restored. Continue from where you left off.'
    clues['exit_room'] = room
    if escaped:
        clues['escaped'] = True
    return clues, solved, selected


# Validate the encoded state before replacing the checkpoint; let the main UI handle file errors.
def save(clues, solved, selected):
    contents = encode(clues, solved, selected)
    decode(contents)  # Validate before replacing the previous checkpoint.
    with open(SAVE_PATH, 'w', encoding='utf-8') as checkpoint:
        checkpoint.write(contents)


# Limit the amount read and decode it; let the caller report missing, damaged or unreadable files.
def load():
    with open(SAVE_PATH, encoding='utf-8') as checkpoint:
        contents = checkpoint.read(4097)
    if len(contents) > 4096:
        raise ValueError('Checkpoint is too large')
    return decode(contents)
