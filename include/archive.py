# Cross-run archive: record distinct endings and unlock a replayable story after all three are collected.
"""Cross-expedition ending records and a short unlockable epilogue."""
import curses
from include import savegame
from include.interface import frame, line

ENDINGS = ('DAWN', 'SILENT EXIT', 'LAST LIGHT')
# Each page contains a title and English body lines sized for the fixed terminal viewport.
STORY = (
    ('THE FOURTH SIGNAL / 1 OF 3', (
        'Three evacuation records resolve into one transmission.', '',
        'The rescue channel supplied a voice.',
        'The scanner corridor supplied a missing crew roster.',
        'The emergency shaft supplied a shelter location.', '',
        'Each route carried only part of the message.',
        'Together, they reveal a room absent from your map:', '',
        'LEVEL ZERO / OCCUPIED',
    )),
    ('THE FOURTH SIGNAL / 2 OF 3', (
        'A maintenance recording begins.', '',
        '"We sealed the lower shelter when the cooling system failed.',
        'The people inside are alive. Their transmitter is broken.', '',
        'The alarm and radio share a feed because we had one cable left.',
        'The battery route was our last way to reach the surface.', '',
        'If this recording opens, someone has found every way out.',
        'Please use what you learned to find a way back in."',
    )),
    ('THE FOURTH SIGNAL / 3 OF 3', (
        'You send the shelter coordinates across the recovered channel.',
        'The rescue team answers with a new route into Level Zero.', '',
        'For a moment, there is only static.', '',
        'Then another voice:', '',
        '"We can hear footsteps above us. Is someone there?"', '',
        'You press the transmitter.', '',
        '"Yes. This time, everyone comes home."',
    )),
)


# Keep ending records and I/O errors separate from run checkpoints so loading cannot erase achievements.
class Archive:
    # Read known ending names from endings.sav; start with an empty collection if the file does not exist.
    def __init__(self):
        # Separate from the run checkpoint: loading an old run cannot erase wins.
        self.path = savegame.SAVE_PATH.rsplit('/', 1)[0] + '/endings.sav'
        self.completed = set()
        self.error = ''
        try:
            with open(self.path, encoding='utf-8') as records:
                rows = records.read(1025).splitlines()
            self.completed = set(rows) & set(ENDINGS)
            if any(row not in ENDINGS for row in rows):
                self.error = 'Some archive records could not be read.'
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError):
            self.error = 'Archive could not be read. Check the game folder.'

    # Unlock only after all three distinct endings; the set automatically removes duplicates.
    @property
    def unlocked(self):
        return len(self.completed) == len(ENDINGS)

    # Record and save an ending; return True only when this call completes the collection.
    def record(self, kind):
        """Return True only when a distinct win completes the collection."""
        if kind not in ENDINGS:
            return False
        was_unlocked = self.unlocked
        if kind in self.completed and not self.error:
            return False
        # Keep the achievement in memory even if writing fails, allowing a later save retry.
        self.completed.add(kind)
        try:
            with open(self.path, 'w', encoding='utf-8') as records:
                records.write(''.join(name + '\n' for name in ENDINGS
                                      if name in self.completed))
            self.error = ''
        except OSError:
            self.error = 'Ending kept this session only. Open Archive to retry saving.'
        return self.unlocked and not was_unlocked


# Show the story with forward/back navigation; pause page changes if the terminal is too small.
def show_story(screen, clues):
    page = 0
    screen.timeout(-1)
    while True:
        title, messages = STORY[page]
        ready = frame(screen, title, clues,
                      'Enter/Right: next    Left: previous    Esc/Q: return')
        if ready:
            for row, message in enumerate(messages, 6):
                line(screen, row, message)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if not ready:
            continue
        if key in (10, 13, curses.KEY_ENTER, curses.KEY_RIGHT):
            if page == len(STORY) - 1:
                return
            page += 1
        elif key == curses.KEY_LEFT:
            page = max(0, page - 1)


# Show the collection and offer story replay; retry a previously failed save when opening the archive.
def show_archive(screen, clues, collection):
    if collection.error and collection.completed:
        collection.record(next(iter(collection.completed)))
    screen.timeout(-1)
    while True:
        controls = 'Enter: play recovered transmission    Esc/Q: return' if collection.unlocked else 'Esc/Q: return'
        ready = frame(screen, 'EVACUATION ARCHIVE', clues, controls)
        if ready:
            line(screen, 5, f'Recovered records: {len(collection.completed)} / 3')
            for index, name in enumerate(ENDINGS):
                line(screen, 8 + index * 2,
                     '[RECOVERED] ' + name if name in collection.completed else '[MISSING]   Unknown evacuation record')
            line(screen, 16, 'THE FOURTH SIGNAL / UNLOCKED' if collection.unlocked
                 else 'Three different escapes will complete the transmission.')
            line(screen, 18, 'Ending records are saved automatically across expeditions.')
            line(screen, 20, collection.error, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if ready and collection.unlocked and key in (10, 13, curses.KEY_ENTER):
            show_story(screen, clues)
