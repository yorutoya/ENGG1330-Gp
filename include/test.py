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
