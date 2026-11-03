# Room 2: implement the numeric drawer puzzle directly, without importing the old lock2.1 script.
"""Lock 2, replacing the old decipher_2 with the lock2.1 drawer puzzle."""
from include.interface import read_command, notice
from include.expedition import lose_cell


# Generate three seeded badge numbers in separate ranges for the gate terminal formulas.
def make_badges(seed):
    # Three separate ranges keep all derived terminal codes distinct.
    return {'A': 10 + seed % 20, 'C': 50 + (seed // 20) % 20,
            'V': 80 + (seed // 400) % 20}


# Select one of three seeded colour orders for the circuit to repeat.
def make_order(seed):
    orders = (('A', 'C', 'V'), ('C', 'V', 'A'), ('V', 'A', 'C'))
    return orders[(seed // 3) % 3]


# Apply the offset and encode letters as numbers from 1 to 26, wrapping around the alphabet.
def encode_word(word='OPEN', shift=7):
    numbers = []
    for letter in word.upper():
        position = ord(letter) - ord('A')  # A=0, B=1, ..., Z=25
        encoded = (position + shift) % 26 + 1
        numbers.append(encoded)
    return numbers


# Check the drawer password while ignoring letter case and surrounding whitespace.
def check_answer(answer):
    return answer.strip().upper() == 'OPEN'


# Require the console clue, then store the colour order and badges after unlocking the drawer.
def main(screen, clues):
    if 'shift' not in clues:
        return False
    feedback = ''
    while True:
        answer = read_command(screen, '02 / LOCKED DRAWER', clues, [
            'The lights reveal a drawer with a powered keyboard.',
            'Its display reads:', '',
            ' - '.join(map(str, encode_word(shift=clues['shift']))), '',
            'A torn paper is tucked underneath. Press F1 to inspect.',
            'Decode the four-letter command.', '', feedback,
        ], [
            ['Torn paper: A=1 | H=8  | O=15',
             '            B=2 | I=9  | P=16',
             '            C=3 | J=10 | Q=17'],
            ['The encoder ADDED the console offset to each letter.',
             'Subtract that offset, then use A=1 ... Z=26.',
             'Wrap values below 1 back around by adding 26.'],
        ])
        if answer is None:
            return False
        if check_answer(answer):
            clues['order'] = make_order(clues.get('seed', 0))
            clues['badges'] = make_badges(clues.get('seed', hash('underground-access') % 8000))
            notice(screen, '02 / DRAWER OPENED', clues, [
                'Inside: a circuit key, fuse diagram and badges.',
                'Badge numbers are saved in ACCESS NOTES (Tab).',
                'Fuse routing: ' + ' > '.join(clues['order']),
                'Repeat this order twice to restore the power.', '',
                'Wrong-colour nodes will short the circuit.',
                'Battery wiring: A=1, C=2, V=3. Reverse the order.',
                'Battery mode: plate a only. Radio needs mains power.',
                'The key fits the circuit terminal and the gate.',
            ])
            return True
        feedback = 'Incorrect command. ' + lose_cell(clues)
        if clues.get('cells', 3) <= 0:
            return False
