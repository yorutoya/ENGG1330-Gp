# Game entry point: initialize the terminal and connect the map, puzzles, saves and ending archive.
"""One curses session, four connected puzzles. Run: python3 main.py."""
import curses
from include import decipher_1, decipher_2, decipher_3, decipher_4, finale, savegame, archive
from include.interface import frame, line, text, notice, show_notes, DIRECTIONS
from include.expedition import new_run, reward

PUZZLES = (decipher_1.main, decipher_2.main, decipher_3.main, decipher_4.main)
TITLES = ('Mirror console', 'Locked drawer', 'Energy circuit', 'Security interlock')


# Create a run seed, advancing the previous seed when starting another expedition.
def new_clues(previous_seed=None):
    # Built-in hash varies between Python processes; no extra library needed.
    # Advance within a session so restarting always changes the badge set.
    seed = hash('underground-access') % 8000 if previous_seed is None else (previous_seed + 137) % 8000
    return new_run(seed)


# Check room access: no cells means no entry; passing the gate locks unfinished rooms.
def available(stage, solved, clues):
    """After finding the drawer key, either remaining room is accessible."""
    if clues.get('cells', 3) <= 0:
        return False
    if solved[3]:
        return solved[stage]
    if stage == 0:
        return True
    if stage == 1:
        return solved[0]
    return solved[1]


# Derive the ending from restored power and radio actions rather than a menu choice.
def ending(clues):
    # Outcomes follow completed work and actual room actions, not a route menu.
    if 'sequence' not in clues:
        return 'LAST LIGHT'
    if clues.get('radio') == 'sent':
        return 'DAWN'
    return 'SILENT EXIT'


# Display the ending and its story fragment; visit_exit handles collection records.
def show_ending(screen, clues):
    result = clues.get('finale_kind', ending(clues))
    if result == 'DAWN':
        messages = [
            'You step into daylight. A rescue team answers',
            'the coordinates you transmitted from the gate.',
            'Restored power keeps the evacuation route open.',
        ]
    elif result == 'SILENT EXIT':
        messages = [
            'The facility hums behind you as you reach daylight.',
            'No rescue signal was transmitted.',
            'You leave the powered facility without an escort.',
        ]
        if clues.get('radio') == 'cut':
            messages.append('The isolated alarm feed has silenced the radio.')
    else:
        messages = [
            'The spare battery dies as you reach daylight.',
            'The gate closes. The rescue radio stays silent.',
            'You escaped, but the facility remains offline.',
        ]
    fragments = {
        'DAWN': 'Your evacuation log preserves a fragment of an unknown voice.',
        'SILENT EXIT': 'Your scanner log contains part of a missing crew roster.',
        'LAST LIGHT': 'The lift recorder saves an unlisted shelter location.',
    }
    messages.extend(['', fragments[result]])
    notice(screen, 'ENDING / ' + result, clues, messages)


# Explain the setting and the shared failure budget before the first map screen.
def show_intro(screen, clues):
    notice(screen, 'UNDERGROUND / EMERGENCY EVACUATION', clues, [
        'You wake inside an underground facility after a power failure.',
        'The corridors are dark, and the security gate is locked.',
        'Recover clues, restore systems, and find a way to the surface.', '',
        'Your emergency pack starts with 3 cells.',
        'Wrong answers and failed challenges can cost a cell.',
        'At 0 cells, this expedition ends and you cannot enter any rooms.',
        'You must start a new expedition or load an earlier checkpoint.', '',
        'On the map: N then Y starts again; L loads a saved checkpoint.',
        'Press P on the map to save. Quitting does not save automatically.',
    ])


# Use the same restart instructions for room failures and final-challenge failures.
def show_run_over(screen, clues):
    notice(screen, 'GAME OVER / NO CELLS LEFT', clues, [
        'Your emergency cells have run out. This expedition has ended.',
        'All rooms are now unavailable.', '',
        'Press Enter to return to the map.',
        'Then press N, followed by Y, to restart with 3 cells.',
        'You can also press L on the map to load an earlier checkpoint.', '',
        'A new expedition resets rooms, clues, and modules.',
        'Your collected endings are kept.',
    ])
    return 'GAME OVER. N then Y: restart with 3 cells. L: load. Q: quit.'


# Run the exit challenge, record a completed ending and reveal the story when all three are collected.
def visit_exit(screen, clues, collection=None):
    # The gate fixes the branch; returning to the map cannot choose another ending.
    kind = clues.setdefault('finale_kind', ending(clues))
    if clues.get('escaped') or finale.play(screen, clues, kind):
        clues['escaped'] = True
        unlocked = collection.record(kind) if collection is not None else False
        show_ending(screen, clues)
        if unlocked:
            archive.show_story(screen, clues)
        if collection is not None and collection.error:
            return collection.error
        if unlocked:
            return 'All records recovered. [V] Archive replays the hidden transmission.'
        return 'EXPEDITION COMPLETE. Start again to explore the facility.'
    if clues.get('cells', 3) <= 0:
        return show_run_over(screen, clues)
    return 'Exit passage unfinished. Select the gate to resume where you left off.'


# Screen positions, not new rooms: the drawer branches into two accessible wings.
ROOM_POSITIONS = ((5, 8), (30, 8), (55, 4), (55, 12))
ROOM_LABELS = ('1  MIRROR PANEL', '2  DRAWER', '3  CIRCUIT', '4  SECURITY GATE')


# Move selection between map neighbours: 0-3 are rooms and 4 is the new-run button.
def navigate(selected, direction):
    # Neighbours in left, right, up, down order. No wrap across the map edges.
    neighbours = ((0, 1, 0, 4), (0, 2, 2, 3), (1, 2, 2, 3),
                  (1, 3, 2, 3), (4, 1, 0, 4))
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    return neighbours[selected][directions.index(direction)]


# Draw rooms, corridors and completion states without changing progress or handling input.
def draw_map(screen, selected, solved, clues):
    dim = curses.A_DIM
    active = curses.color_pair(1)
    text(screen, 5, 5, 'ACCESS WING', dim)
    text(screen, 6, 5, 'Restore lighting. Find the key.', dim)

    # Solid corridors show accessible connections; dots show locked passages.
    text(screen, 10, 24, '------' if solved[0] else '......', active if solved[0] else dim)
    text(screen, 10, 49, '---+' if solved[1] else '...+', active if solved[1] else dim)
    for y in range(6, 15):
        text(screen, y, 52, '|' if solved[1] else ':', active if solved[1] else dim)
    text(screen, 10, 52, '+', active if solved[1] else dim)
    for y in (6, 14):
        text(screen, y, 52, '+--' if solved[1] else '+..', active if solved[1] else dim)
    # This is an optional power link, not a lock on the lower branch.
    text(screen, 8, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 9, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 9, 66, 'power', dim)
    text(screen, 10, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 11, 64, 'v', active if solved[2] else dim)

    for i, (x, y) in enumerate(ROOM_POSITIONS):
        state = 'LOCKED'
        if i == 3 and solved[i] and not clues.get('escaped'):
            state = 'EXIT AHEAD'
        elif solved[i]:
            state = 'COMPLETE'
        elif available(i, solved, clues):
            state = 'READY'
        style = active if state != 'LOCKED' else dim
        if i == selected:
            style = curses.color_pair(2) | curses.A_BOLD
        text(screen, y, x, '+' + '-' * 17 + '+', style)
        marker = '>' if i == selected else ' '
        text(screen, y + 1, x, '|' + marker + ROOM_LABELS[i].ljust(16) + '|', style)
        text(screen, y + 2, x, '|' + state.center(17) + '|', style)
        text(screen, y + 3, x, '+' + '-' * 17 + '+', style)

    style = curses.color_pair(2) | curses.A_BOLD if selected == 4 else dim
    text(screen, 15, 5, ('> ' if selected == 4 else '  ') + '[N] New expedition', style)
    text(screen, 17, 5, f'{sum(solved)} / 4 rooms complete', dim)
    text(screen, 17, 39, '[P] Save    [L] Load checkpoint', dim)


# Initialize curses and run the map loop, passing the shared clues dictionary to each puzzle.
def main(screen):
    screen.keypad(True)
    curses.noecho()
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # Each puzzle adds evidence to this dictionary for later puzzles.
    # Shared run data: seed controls variation, cells tracks lives, and modules lists installed rewards.
    # shift/order/badges/sequence store recovered clues; radio tracks rescue contact.
    # exit_room holds the final challenge; escaped becomes True only after completing the escape.
    clues = new_clues()
    # Keep the ending collection separate from clues so resets and checkpoint loads cannot erase it.
    collection = archive.Archive()
    # solved tracks the four rooms; selected is only the current map selection.
    solved = [False] * 4
    selected = 0
    message = 'Start at the mirror console to restore emergency lighting.'
    show_intro(screen, clues)
    while True:
        screen.timeout(-1)
        controls = 'Arrows: select  1-4: room  Enter: open  Tab: notes  N: new  Q: quit'
        ready = frame(screen, 'FACILITY MAP / SELECT A ROOM', clues, controls)
        if ready:
            descriptions = (
                'Inspect the mirror panel and restore lighting.',
                'Decode the drawer; inspect its numbered badges.',
                'Route coloured energy nodes to restore power.',
                'Explore the gate, radio and alarm equipment.',
                'Clear this expedition and generate new badges.',
            )
            draw_map(screen, selected, solved, clues)
            text(screen, 15, 30, f'[V] Archive {len(collection.completed)}/3', curses.color_pair(1))
            description = descriptions[selected]
            if selected == 3 and solved[3] and not clues.get('escaped'):
                description = 'Resume the exit passage beyond the open security gate.'
            line(screen, 18, description, curses.color_pair(1))
            text(screen, 20, 5, message, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if not ready:
            continue
        if key in (ord('v'), ord('V')):
            archive.show_archive(screen, clues, collection)
            continue
        if key in (ord('p'), ord('P')):
            try:
                savegame.save(clues, solved, selected)
                message = 'Progress saved. You can quit and load it with L next time.'
            except (OSError, ValueError):
                message = 'Could not save progress. Check that the game folder is writable.'
            continue
        if key in (ord('l'), ord('L')):
            try:
                checkpoint = savegame.load()
            except FileNotFoundError:
                message = 'No saved expedition yet. Press P to save your progress.'
            except (OSError, ValueError):
                message = 'Cannot read this checkpoint. Your current expedition is unchanged.'
            else:
                if frame(screen, 'LOAD CHECKPOINT?', clues,
                         'Y: load saved progress    Any other key: cancel'):
                    line(screen, 8, 'Replace this expedition with the saved checkpoint?')
                    line(screen, 10, f'Saved rooms: {sum(checkpoint[1])}/4    Cells: {checkpoint[0]["cells"]}')
                    screen.refresh()
                    if screen.getch() in (ord('y'), ord('Y')):
                        clues, solved, selected = checkpoint
                        message = 'Checkpoint loaded. Continue your expedition.'
                        if clues.get('cells', 3) <= 0:
                            selected = 4
                            message = show_run_over(screen, clues)
                        if clues.get('escaped'):
                            if collection.record(clues['finale_kind']):
                                archive.show_story(screen, clues)
                            if collection.error:
                                message = collection.error
            continue
        if key in (ord('n'), ord('N')):
            selected = 4
            key = 10
        if key == 9:
            show_notes(screen, clues)
        elif ord('1') <= key <= ord('4'):
            selected = key - ord('1')
        elif key in DIRECTIONS:
            selected = navigate(selected, DIRECTIONS[key])
        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 4:
                if not frame(screen, 'RESET EXPEDITION?', clues, 'Y: reset this expedition | Any other key: cancel'):
                    continue
                line(screen, 8, 'Clear all completed systems and recovered clues?')
                line(screen, 10, 'Saved checkpoints and ending records are kept.')
                screen.refresh()
                if screen.getch() in (ord('y'), ord('Y')):
                    clues = new_clues(clues['seed'])
                    solved = [False] * 4
                    selected = 0
                    message = 'New expedition. Start with the mirror console.'
            elif not available(selected, solved, clues):
                message = ('No cells left. Press N then Y to start a new expedition.'
                           if clues.get('cells', 3) <= 0 else
                           'This room is unavailable. Check the earlier systems.')
            elif solved[selected]:
                if selected == 3:
                    message = visit_exit(screen, clues, collection)
                    if clues.get('escaped') or clues.get('cells', 3) <= 0:
                        selected = 4
                    continue
                notice(screen, TITLES[selected].upper() + ' / COMPLETE', clues,
                       ['This system is restored. Its clues are in the journal.',
                        'Continue to the next system from mission control.'])
            # Each puzzle returns whether it was completed; returning False does not refund spent resources.
            elif PUZZLES[selected](screen, clues):
                solved[selected] = True
                if selected in (1, 2):
                    reward(screen, clues, selected)
                message = 'System restored. New evidence added to the journal.'
                if selected == 3:
                    message = visit_exit(screen, clues, collection)
                    if clues.get('escaped') or clues.get('cells', 3) <= 0:
                        selected = 4
                elif selected == 1:
                    selected = 2
                    message = 'The drawer key fits both the energy terminal and the gate.'
                else:
                    selected += 1
            elif clues.get('cells', 3) <= 0:
                message = show_run_over(screen, clues)
                selected = 4
            else:
                message = 'Back at control. Completed systems and clues are kept.'


if __name__ == '__main__':
    curses.wrapper(main)
