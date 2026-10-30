"""Optional legacy text effect, using only curses for its delay."""
import curses

def typewriter(text, delay=0.025, pause=0.6, end="\n"):
    for char in str(text):
        print(char, end="", flush=True)
        curses.napms(int(delay * 1000))
        if char in ".!?。！？\n":
            curses.napms(int(pause * 1000))
    print(end, end="", flush=True)
