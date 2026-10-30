#Suggestions:
#1. Improve logics for users to reach the alphabet table, not too simple for users to guess, but set a direction of guess for users, that they may not need the alphabet clue to decode.
#2. Integrate "Curses", may check formats in the main program and other deciphers.
#3. For reference https://docs.python.org/3/howto/curses.html, or ask for AI-Agents
#4. Design a new storyboard for Decipher 1, the overall storyboard -> main.py

print("You are trapped inside a dark vault room.")
print("A dark control panel displays the following message:")
print("KIVHH GSV YFGGLM")
print("You must decode the message and type the correct action to restore the power.\n")

failures = 0

while True:
    player_input = input("Enter your command: ").strip().upper()

    if player_input == "PRESS THE BUTTON":
        print("\n>>> BOOM! The lights flicker on and the vault door unlocks. <<<")
        print("The power has been successfully restored!")
        break
    else:
        failures += 1
        print("The panel flashes red. Incorrect command.\n")
        if failures > 5:
            print("[SYSTEM CLUE]: The alphabet is mirrored: A <-> Z, B <-> Y, C <-> X.\n")
