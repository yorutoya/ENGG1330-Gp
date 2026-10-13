from include.effects import typewriter
from include.decipher_3 import run_lock3
import time
import os

end = False
while not end:
    typewriter(
        "You wake to the sound of a piercing alarm. \n"
        "You are trapped in an unfamiliar underground room, "
        "and the heavy exit door is sealed shut. \n"
        "Red letters flash across its screen: "
        "“THREE SECURITY LOCKS ACTIVATED.”\n\n"
        "On a nearby desk, "
        "you find a handwritten note: \n"
        "“If you’re reading this, the evacuation failed. \n"
        "I’ve hidden a way out in the system. \n"
        "First, restore the power. \n"
        "Then, open the drawer to find the control key. \n"
        "The final lock has a damaged circuit. \n"
        "Guide the energy snake to collect eight energy points within forty-five seconds to power the exit.”"
    )
    time.sleep(5)
    os.system("cls" if os.name == "nt" else "clear")
    typewriter("If you are ready, press any key then ENTER to continue...")
    key = input(">").strip().lower()
    os.system("cls" if os.name == "nt" else "clear")
    #Part 1 Invoker
        #Pending
    #Part 2 Invoker
        #Pending
    decipher_2_solved = True
    #Part 3 Invoker
    if decipher_2_solved:
        typewriter("The drawer reveals access to the exit challenge.")
        time.sleep(3)
        os.system("cls" if os.name == "nt" else "clear")
        if run_lock3():
            typewriter("The exit opens. You win!\n")
            typewriter("If you'd like to restart the game, press L then ENTER to continue...\n")
            typewriter("\nOr you can press another then ENTER to stop the game.\n")
            key = input(">").strip().lower()
            if key.lower() == "l":
                os.system("cls" if os.name == "nt" else "clear")
                typewriter("Restarting the game...")
                time.sleep(1)
                os.system("cls" if os.name == "nt" else "clear")
            else:
                end = True
        else:
            typewriter("The exit remains locked.")



