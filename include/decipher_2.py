# lock2
import curses
import time


def main(screen):
    screen.clear()

    screen.addstr(2, 2, 'The lights went suddenly on.')
    screen.addstr(3, 2, 'You can now see the whole view of the room you are in.')
    screen.addstr(4, 2, 'You noticed a drawer--the only furniture in this battered room.')
    code = [22, 23, 12, 21]
    strcode = '-'.join(map(str, code))

    screen.addstr(5, 2, 'Embedded upon it is a powered keyboard that displays:')
    screen.addstr(6, 2, strcode)
    screen.refresh()

    time.sleep(3)
    while True:
        # hint2 = input('Need a hint? Enter 1 for YES and 0 for NO')
        screen.addstr(10, 2, 'Need a hint? Enter 1 for YES and 0 for NO')
        hint2_bytes = screen.getstr(10, 45, 1)
        hint2 = hint2_bytes.decode('utf-8').strip()
        screen.refresh()
        if hint2 == '1':
            screen.addstr(11, 2, '7 is a magic number.')
            screen.refresh()
            break
        elif hint2 == '0':
            break
        else:
            screen.addstr(11, 2, 'Please enter 1 or 0 only.')
            screen.refresh()
    while True:
        # answer2 = input('Please enter your answer:')
        screen.addstr(14, 2, 'Please enter your answer:')
        answer2_bytes = screen.getstr(14, 28, 20)
        answer2 = answer2_bytes.decode('utf-8').strip().upper()
        screen.refresh()
        if answer2 == 'OPEN':
            screen.addstr(16, 2, 'The drawer cracked open to reveal a key.')
            screen.addstr(17, 2, 'Press any key to continue...')
            screen.refresh()
            screen.getch()
            return True
            break
        else:
            screen.addstr(16, 2, 'Wrong answer. Try again.')
            screen.refresh()

def run_lock2():
    return curses.wrapper(main)

if __name__ == "__main__":
    curses.wrapper(run_lock2())
