import sys
import time

def typewriter(text, delay=0.025, pause=0.6, end="\n"):
    text = str(text)
    for i, char in enumerate(text):
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
        if char in ".!?。！？\n":
            if i == len(text) - 1 or text[i + 1] not in ".!?。！？\n":
                time.sleep(pause)
    sys.stdout.write(end)
    sys.stdout.flush()