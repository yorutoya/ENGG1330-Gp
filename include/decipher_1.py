# Room 1: decode a mirrored alphabet command to recover the shared cipher offset.
"""Lock 1: a mirror-alphabet command releases the shared numeric key."""
from include.interface import read_command, notice
from include.expedition import lose_cell

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


# Map A to Z, B to Y, and so on; preserve spaces and other non-letter characters.
def mirror(message):
    result = ''
    for letter in message.upper():
        if letter in ALPHABET:
            position = ALPHABET.index(letter)
            result += ALPHABET[25 - position]
        else:
            result += letter
    return result


# Check the full command while ignoring letter case and repeated whitespace.
def check_command(answer):
    return ' '.join(answer.upper().split()) == 'PRESS THE BUTTON'


# Save the offset and return True on success; return False on cancellation or exhausted cells.
def main(screen, clues):
    feedback = ''
    while True:
        answer = read_command(screen, '01 / MIRROR CONSOLE', clues, [
            'Emergency lighting is offline. A mirrored panel reads:', '',
            mirror('PRESS THE BUTTON'), '',
            'Etched above the panel: A ... Z | Z ... A',
            'Decode the message and enter the full English command.', '', feedback,
        ], [
            ['Read the alphabet from opposite ends: A <-> Z.'],
            ['B <-> Y, C <-> X. Decode each letter separately.'],
        ])
        if answer is None:
            return False
        if check_command(answer):
            clues['shift'] = 7
            notice(screen, '01 / EMERGENCY LIGHTING RESTORED', clues, [
                'A service label appears beneath the button:', '',
                'ENCODER OFFSET: +7. Subtract it when decoding.',
                'Keep this offset. Gate codes also need drawer badges.', '',
                'The powered drawer is now available.',
            ])
            return True
        feedback = 'Incorrect command. ' + lose_cell(clues)
        if clues.get('cells', 3) <= 0:
            return False
