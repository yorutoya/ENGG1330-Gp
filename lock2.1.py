#lock2
import curses
import time

def run_lock2(screen):
    screen.clear()

    time.sleep(1.5)
    screen.addstr(2,2,'The lights went suddenly on.')
    screen.refresh()
    time.sleep(1.5)
    screen.addstr(3,2,'You can now see the whole view of the room you are in.')
    screen.refresh()
    time.sleep(1.5)
    screen.addstr(4,2,'You noticed a drawer--the only furniture in this battered room.')
    screen.refresh()
    time.sleep(1.5)
    code=[22,23,12,21]
    strcode='-'.join(map(str,code))
    screen.addstr(5,2,'Embedded upon it is a powered keyboard that displays:')
    screen.addstr(6,33,strcode)
    screen.refresh()
    time.sleep(2.5)

    while True:
        #hint2=input('Look for a hint? Enter 1 for YES and 0 for NO')
        screen.addstr(10,2,'Look for hints? Enter 1 for YES and 0 for NO')
        curses.echo()
        hint2_bytes=screen.getstr(10,49,1)
        curses.noecho()
        hint2=hint2_bytes.decode('utf-8').strip()
        screen.refresh()
        if hint2=='1':
            screen.addstr(11,2,'You found a piece of torn paper underneath the keyboard.')
            screen.refresh()
            time.sleep(1.5)
            screen.addstr(12,2,'Written on it was:')
            screen.refresh()
            time.sleep(1.5)
            screen.addstr(13,30,'A=1  |  H=8  |  O=15')
            screen.addstr(14,30,'B=2  |  I=9  |  P=16')
            screen.addstr(15,30,'C=3  |  J=10 |  Q=17')
            screen.refresh()
            time.sleep(2)
            screen.addstr(17,2,'Did you spot the pattern？')
            screen.refresh()
            time.sleep(1.5)
            screen.addstr(18,2,'A shift in the numbers is required.')
            screen.refresh()
            time.sleep(1.5)
            break
        elif hint2=='0':
            break
        else:
            screen.addstr(11,2,'Please enter 1 or 0 only.')
            screen.refresh()
            time.sleep(1)
            screen.clear()

    while True:
        #answer2=input('Please enter your answer:')
        screen.addstr(20,2,'Please enter your answer:')
        curses.echo()
        answer2_bytes=screen.getstr(20,32,20)
        curses.noecho()
        answer2=answer2_bytes.decode('utf-8').strip().upper()
        screen.refresh()
        if answer2=='OPEN':
            screen.addstr(22,2,'The drawer cracked open to reveal a key.')
            screen.refresh()
            time.sleep(1)
            screen.addstr(23,2,'Press any key to continue...')
            screen.refresh()
            screen.getch()
            return True
            break
        else:
            screen.addstr(21,2,'Wrong answer. Try again.')
            screen.refresh()
            time.sleep(2)
            screen.addstr(21,2,' '*40)
            screen.refresh()

if __name__ == "__main__":
    curses.wrapper(run_lock2)
            
