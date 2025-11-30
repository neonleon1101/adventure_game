import time, sys, random, threading, msvcrt, textwrap, json, os

# Room information from rooms.json
with open("./rooms.json", "r") as f:
    roomContents = json.load(f)
# Item information from items.json
with open("./items.json", "r") as f:
    itemContents = json.load(f)

# Global Game States
run = True
mainMenu = True
pauseMenu = False
inventoryMenu = False
itemsMenu = False
notesMenu = False
play = False
play_resumed = False

# Player Stats <= Stuff that needs to be 'saved' and recalled when 'loaded'
current_room = "exterior"
inv_items = []
inv_notes = [None, None, None, None, None, None]
rooms_explored = []
removed_choices = {}

# Dictionary of crafting/combining recipes
recipes = {
    tuple(sorted(["PAN-T-XXX-02", "FRD-T-XXX-02", "PAN-T-XXX-03"])): "XXX-T-RAT-01"
}

#----------------------
# TYPEWRITER
#----------------------
typing_speed = 150 #wpm
textDivide = ('=' * 81)
skip_event = threading.Event() #press 'space' to get text instantly
def listen_for_space():
    global skip_typing
    while True:
        if msvcrt.kbhit():
            if msvcrt.getch() == b' ':
                skip_event.set()
                return
        time.sleep(0.01)
def slowReader(text: str, toggleDivide: bool):
    global typing_speed
    skip_event.clear()

    listener = threading.Thread(target=listen_for_space, daemon=True)
    listener.start()

    paragraphs = text.split('\n\n')
    if toggleDivide == True:
        print(textDivide+'\n')

    if toggleDivide == False:
        space = "\n"
    elif toggleDivide == True:
        space = "\n\n"

    for paragraph in paragraphs:
        wrapped = textwrap.fill(paragraph, width=81) + space

        # Print one char at a time
        for i, char in enumerate(wrapped):
            if skip_event.is_set():
                sys.stdout.write(wrapped[i:])
                sys.stdout.flush()
                break
            
            sys.stdout.write(char)
            sys.stdout.flush()
            
            delay_per_char = 60 / (typing_speed * 5)
            variation = random.uniform(0,2)
            time.sleep(delay_per_char * variation)
                
    if toggleDivide == True:
        print(textDivide)
def fastReader(text: str, toggleDivide: bool):
    paragraphs = text.split('\n\n')
    if toggleDivide == True:
        print(textDivide+'\n')

    if toggleDivide == False:
        space = ""
    elif toggleDivide == True:
        space = "\n"
    for paragraph in paragraphs:
        wrapped = textwrap.fill(paragraph, width=81) + space
        print(wrapped)

    if toggleDivide == True:
        print(textDivide)
# Add sound? if laptop ever gets fixed lol, add sound warning to menu



#----------------------
#  GAME FUNCTIONS
#----------------------
# Saves relevant game data to a .txt file to be loaded later
def saveGame():
    global current_room, inv_items, inv_notes, rooms_explored, removed_choices

    save_data = {
        "current_room": current_room,
        "inv_items": inv_items,
        "inv_notes": inv_notes,
        "rooms_explored": rooms_explored,
        "removed_choices": removed_choices
    }
    with open("./save_file.json", "w") as f:
        json.dump(save_data, f, indent=4)
    return

# Checks if any save data exists
def check_save_data() -> bool:
    filepath = "./save_file.json"
    if os.path.getsize(filepath) == 0:
        return False
    else:
        return True

# Loads relevant game data from a .txt file and continues the game from there
def loadGame():
    with open("./save_file.json", "r") as f:
        save_data = json.load(f)
    
    if check_save_data() == True:
        load_current_room(save_data["current_room"])
        load_inv_items(save_data["inv_items"])
        load_inv_notes(save_data["inv_notes"])
        load_rooms_explored(save_data["rooms_explored"])
        load_removed_choices(save_data["removed_choices"])
    if check_save_data() == False:
        msg = "No save data found"
        slowReader(msg, False)
        time.sleep(3)

# LOAD FUNCTIONS: Functions that run whenever the player loads a save to make sure all values are correct
def load_current_room(save_data_room: str):
    global current_room
    current_room = save_data_room
    return

def load_inv_items(save_data_items: list):
    global inv_items

    if not save_data_items:
        return
    for item_code in save_data_items:
        inv_items.append(item_code)
        itemContents[item_code]['hasItem'] = True
    return

def load_inv_notes(save_data_notes: list):
    global inv_notes

    for item_code in save_data_notes:
        if item_code is None:
            continue
        code_values = item_code.split('-', 3)
        slot_number = int(code_values[2])
        inv_notes[slot_number - 1] = item_code
        itemContents[item_code]['hasItem'] = True
    return

def load_rooms_explored(save_data_explored: list):
    global rooms_explored, roomContents
    
    for room in save_data_explored:
        rooms_explored.append(room)

def load_removed_choices(save_data_removed: dict):
    global removed_choices, roomContents

    if not save_data_removed:
        return
        
    for room_key, choice_list in save_data_removed.items():
        for choice_key in choice_list:
            if choice_key in roomContents[room_key]['choices']:
                del roomContents[room_key]['choices'][choice_key]
    removed_choices = save_data_removed.copy()

# When nav = true, changes current_room based on user_input
def enterRoom(room_key: str, user_input: str):
    global roomContents, current_room, rooms_explored

    if room_key not in rooms_explored:
        rooms_explored.append(room_key)

    choice = roomContents[room_key]['choices'][user_input]
    
    choice_text = None
    for k in choice.keys():
        if k not in ("once", "nav", "item"):
            choice_text = k
            break

    destination = choice[choice_text]
    checkNav = check_nav(current_room, user_input)
    if checkNav == True:
        current_room = destination
        return
    else:
        print("ERROR: enterRoom")
        return

# Removes choice from list of choices for a room and adds it to the removed_choices dict
def removeChoice(room_key:str, user_input: str):
    global roomContents, removed_choices

    choices = roomContents[room_key]['choices']
    if user_input not in choices:
        return
    del choices[user_input]

    if room_key not in removed_choices:
        removed_choices[room_key] = []
    else:
        pass
    removed_choices[room_key].append(user_input)

# Reloads room data for when the player starts a new game without exiting the program
def reset_roomData():
    global roomContents
    with open("./rooms.json", "r") as f:
        roomContents = json.load(f)
#^^^^^^^^^^^^^^^^^^^^^^



#----------------------
#  PRINT FUNCTIONS
#----------------------
# Shows Game Start Menu
def show_mainMenu():
    os.system('color a')
    os.system('cls')
    with open('./text/ascii_Scarlet_Manor.txt', 'r', errors='ignore') as file:
            content = file.read()
    print(textDivide + '\n')
    print(content)
    print(textDivide + '\n')
    slowReader("Welcome to the Secret of Scarlet Manor!", False)
    print(' 1 - New Game')
    print(' 2 - Load Game')
    print(' 3 - Quit Game')
    print('\n' + textDivide)

# Shows Pause Menu
def show_pauseMenu():
    print(textDivide + '\n')
    slowReader('Game Paused', False)
    print(' 1 - Continue')
    print(' 2 - Save Game')
    print(' 3 - Quit to Main Menu')
    print(' 4 - Quit Game')
    print('\n' + textDivide)
    
# Shows Inventory Menu (Meets 'showInventory' requirement)
def show_inventoryMenu():
    print(textDivide + '\n')
    slowReader('Inventory:', False)
    print(' 1 - View Items')
    print(' 2 - View Notes')
    print(' 0 - Return')
    print('\n' + textDivide)

# Shows the items menu within the inventory menu
def show_itemsMenu():
    global inv_items, itemContents

    print(textDivide + '\n')
    slowReader('Items:', False)

    if not inv_items:
        print("You have no items")
    else:
        item_number = 0
        for item in inv_items:
            item_name = get_itemName(item)
            item_number = item_number + 1
            print(f' {item_number} - {item_name}')
        print('\n c - Combine Items')
        print(' r - Remove Item')        
    print(' 0 - Return')
    print('\n' + textDivide)
    print("Enter the number of any item to examine it further.")

# Shows the notes menu within the inventory menu
def show_notesMenu():
    global inv_notes, itemContents

    print(textDivide + '\n')
    slowReader('Notes:', False)

    for i in range(6):
        note_code = inv_notes[i]
        if note_code is None:
            print(f" {i+1} - ")
        else:
            note_name = get_itemName(note_code)
            print(f" {i+1} - {note_name}")
            
    print('\n 0 - Return')
    print('\n' + textDivide)
    print("Enter the number of any item to examine it further.")

# Shows Game Intro
def show_prologue():
    global current_room, gameChoices, commands
    current_room = "exterior"
    
    os.system('cls')
    with open('./text/prologue.txt', 'r', errors='ignore') as file:
        content = file.read()
    slowReader(content, True)
    time.sleep(2)
    print("press 'enter' to continue")
    input('')

# Show New Game loading
def newGame():
    global current_room, inv_items, inv_notes, rooms_explored, removed_choices

    current_room = "exterior"
    inv_items = []
    inv_notes = [None, None, None, None, None, None]
    rooms_explored = []
    removed_choices = {}

    save_data = {
        "current_room": current_room,
        "inv_items": inv_items,
        "inv_notes": inv_notes,
        "rooms_explored": rooms_explored,
        "removed_choices": removed_choices
    }
    with open("./save_file.json", "w") as f:
        json.dump(save_data, f, indent=4)
    reset_roomData()

    print('Loading...')
    time.sleep(3)
    print("New game!")
    time.sleep(1)

# Show Loaded Game loading
def show_loadGame():
    print('Loading...')
    time.sleep(3)
    print("Game loaded!")
    time.sleep(1)

# Show Description of Whatever room the player is in
def show_roomDesc(room_key: str, toggleType: bool):
    global roomContents

    os.system('cls')
    roomDesc = roomContents[room_key]['description']
    if toggleType == False:
        slowReader(roomDesc, True)
    elif toggleType == True:
        fastReader(roomDesc, True)

# Show return description of a room the player has previously explored
def show_ReturnDesc(room_key: str, toggleType: bool):
    global roomContents

    os.system('cls')
    returnDesc = roomContents[room_key]['returnDesc']
    if toggleType == False:
        slowReader(returnDesc, True)
    elif toggleType == True:
        fastReader(returnDesc, True)

# Show description for an action that occurs once
def show_OnceDesc(room_key: str, user_input: str):
    global roomContents

    os.system('cls')
    choices = roomContents[room_key]['choices']
    choice = choices[user_input]

    choice_text = None
    for k in choice.keys():
        if k not in ("once", "nav", "item"):
            choice_text = k
            break
    onceDesc = choice[choice_text]
    
    slowReader(onceDesc, True)
    time.sleep(2)
    print("press 'enter' to continue")
    input('')

# Show current options
def show_Choices(room_key: str, toggleType: bool):
    global roomContents, current_room

    if toggleType == False:
        slowReader("What will you do?", False)
    elif toggleType == True:
        fastReader("What will you do?", False)
   
    choices = roomContents[room_key]['choices']
    for number, data in choices.items():
        choiceNumber = number
        for key in data.keys():
            if key not in ("once", "nav", "item"):
                msg = f" {choiceNumber} - {key}"
                print(msg)
    print()
    print(' 0 - Pause Game')
    print(' i - Inventory')
    print(textDivide)
#^^^^^^^^^^^^^^^^^^^^^^



#----------------------
#  CHECK FUNCTIONS
#----------------------
# Check if room has been explored or not
def check_explored(room_key: str) -> bool: # Read as "has [room_key] been explored?" return false = no, return true = yes
    global rooms_explored, roomContents

    if room_key not in rooms_explored:
        return False  # <= First time visit
    else:
        return True   # <= Return to room

# Check if the choice is avalaible more than once or not (returns bool)
def check_once(room_key: str, user_input: str) -> bool:
    global roomContents

    choice = roomContents[room_key]['choices'][user_input]['once']
    if choice == False:
        return False  # <= Action can be performed many times
    elif choice == True:
        return True   # <= Action can only be performed once
    else:
        print('ERROR: check_once')

# Check if the choice is for navigation or not (returns bool)
def check_nav(room_key: str, user_input: str) -> bool:
    global roomContents

    choice = roomContents[room_key]['choices'][user_input]['nav']
    if choice == False:
        return False  # <= Action is not used to move somewhere
    elif choice == True:
        return True   # <= Action is used to move somewhere (change current_room)
    else:
        print("ERROR: check_nav")

# Check if the choice is related to an item or not (returns bool)
def check_item(room_key: str, user_input: str) -> bool:
    global roomContents

    choice = roomContents[room_key]['choices'][user_input]['item']
    if choice == False:
        return False  # <= Action is NOT related to an item
    elif choice == True:
        return True   # <= Action is related to an item
    else:
        print('ERROR: check_item')

# Checks if the player has a specific needed item (meets 'hasItem' requirement)
def check_hasItem(item_code: str) -> bool:
    global inv_items

    if item_code in inv_items:
        return True
    else:
        return False

# Checks if the item is essential or not (needed to win the game)
def check_essential(item_code:str) -> bool:
    global itemContents

    essential = itemContents[item_code]['essential']
    if essential == False:
        return False
    elif essential == True:
        return True
    else:
        print('ERROR: check_hasItem')

# Checks if the players inventory is full or not
def check_invFull(room_key: str, user_input: str) -> bool:
    global roomContents, inv_items

    item_code = get_itemCode(room_key, user_input)
    code_values = item_code.split('-', 3)

    if code_values[1] == 'T':
        if len(inv_items) >= 10:
            return True
        elif len(inv_items) < 10:
            return False
        else:
            print("ERROR: check_invFull")
            time.sleep(1)
    elif code_values[1] == 'N':
        return False
    else:
        pass

# Checks if the player meets the conditions for an event loop, then sends them there if so
def check_ifEvent():
    global current_room
    
    if current_room == "rat_hole":
        if check_hasItem("XXX-T-RAT-01"):
            event_lureRat()
            return
    elif current_room == "greenhouse":
        if check_hasItem("UTC-T-PTB-01"):
            event_digHole()
            return
    elif current_room == "planter_box":
        if check_hasItem("PLB-T-LBD-02"):
            event_digHoleReturn()
            return
    else:
        return
#^^^^^^^^^^^^^^^^^^^^^^



#----------------------
#  INVENTORY FUNCTIONS
#----------------------
# Adds an item associated with a command to the player's inventory
def addItem(room_key: str, user_input: str):
    global inv_items, inv_notes, roomContents, itemContents

    item_code = get_itemCode(room_key, user_input)
    code_values = item_code.split('-', 3)

    if code_values[1] == 'T':
        inv_items.append(item_code)
    elif code_values[1] == 'N':
        slot_number = int(code_values[2])
        inv_notes[slot_number - 1] = item_code
    else:
        pass

    itemContents[item_code]['hasItem'] = True
    msg = show_addItemDesc(item_code)
    slowReader(msg, False)
    time.sleep(1)

# Removes an item from the player's inventory and places it in the current_room
def removeItem(user_input: str):
    global roomContents, itemContents, inv_items

    item = inv_items[int(user_input) - 1]
    if check_essential(item) == False:
        msg = "Once you remove an item it will be lost forever. Are you sure you want to remove this item?"
        slowReader(msg, False)
        removePrompt = input('> ').lower().strip()
        if removePrompt == 'yes':
            item = inv_items[int(user_input) - 1]
            if item in inv_items:
                inv_items.remove(item)
            else:
                return
            msg = "You removed the " + get_itemName(item)
            slowReader(msg, False)
            time.sleep(1)
        else:
            print("Remove canceled")
            time.sleep(1)
    elif check_essential(item) == True:
        msg = "You cannot remove this item."
        slowReader(msg, False)
        time.sleep(1)
        return
    else:
        print("ERROR: removeItem")

# Combines 2 or more items if they're item code it in the recipes dictionary
def combineItems():
    global itemContents, inv_items
    
    slowReader("Which items would you like to combine? (Input as: #-#-#)", False)
    user_input = input('> ').strip()
    numbers = user_input.split('-')

    item_codes = []
    for number in numbers:
        if not number.isdigit():
            print("Invalid item(s)")
            time.sleep(2)
            return
        else:
            index = int(number)
            if index < 1 or index > len(inv_notes):
                print("Invalid item number")
                time.sleep(2)
                return
            else:
                item_codes.append(inv_items[index-1])
    
    sorted_codes = tuple(sorted(item_codes))
    if sorted_codes in recipes:
        new_item = recipes[sorted_codes]
        for code in item_codes:
            inv_items.remove(code)
        inv_items.append(new_item)
        msg = show_addItemDesc(new_item)
        slowReader(msg, False)
        time.sleep(1)
    else:
        print("Those items cannot be combined.")
        time.sleep(2)
        return

# Searchs through roomContents and gets the item code of the item of the corresponding input
def get_itemCode(room_key: str, user_input: str) -> str:
    global roomContents
    
    choice = roomContents[room_key]['choices'][user_input]
    choice_text = None
    for k in choice.keys():
        if k not in ("once", "nav", "item"):
            choice_text = k
            break

    item_code = choice[choice_text]
    if item_code:
        return item_code
    else:
        return None
    
# Searches through itemContents and gets the item name of the corresponding item code
def get_itemName(item_code: str) -> str:
    global itemContents

    item = itemContents[item_code]
    if item:
        return item.get('item_name')
    else:
        return None

# Searches through roomContents and gets the room that an item comes from based off its item_code
def get_itemRoom(item_code: str) -> str:
    global roomContents

    code_values = item_code.split('-', 3)

    for room in roomContents:
        room_code = roomContents[room]['room_code']
        if code_values[0] == room_code:
            return room
        else:
            pass

# Searches through roomContents and gets the choice number that an item corresponds to bassed off its item_code
def get_itemChoice(item_code: str) -> str:
    global roomContents

    room = get_itemRoom(item_code)
    choices = roomContents[room]['choices']

    for choice_number, choice_data in choices.items():
        for key in choice_data.keys():
            if key in ("once", "nav", "item"):
                continue
            if choice_data[key] == item_code:
                return choice_number
    return None     
            
# PRINVENTORY FUNCTIONS (print + inventory, credit: Aiden Williams)
def show_itemDesc(user_input: str) -> str:
    global inv_items

    if int(user_input) in range(1, len(inv_items)+1):
        item = inv_items[int(user_input) - 1]
        if item:
            itemDesc = itemContents[item]['description']
            os.system('cls')
            slowReader(itemDesc, True)
        else:
            return None
    else:
        print("I don't understand that command.")
    time.sleep(2)
    print("press 'enter' to continue")
    input('')

def show_noteDesc(user_input: str) -> str:
    global inv_notes
    
    if 1 <= int(user_input) <= 6:
        note = inv_notes[int(user_input) - 1]
        if note is None:
            slowReader("You don't have that note.", False)
            time.sleep(1)
            return
        elif note:
            noteDesc = itemContents[note]['description']
            os.system('cls')
            slowReader(noteDesc, True)
        else:
            return None
    else:
        print("I don't understand that command.")
    time.sleep(2)
    print("press 'enter' to continue")
    input('')

def show_addItemDesc(item_code: str) -> str:
    global itemContents

    item = itemContents[item_code]
    if item:
        return item.get('addDescription')
    else:
        return None

def show_useItemDesc(item_code: str) -> str:
    global itemContents

    item = itemContents[item_code]
    if item:
        return item.get('useDescription')
    else:
        return None
#^^^^^^^^^^^^^^^^^^^^^^



#----------------------
#  EVENT LOOPS
#----------------------
# Luring the rat out of the hole with the sandwich
def event_lureRat():
    global inv_items, current_room
    
    os.system('cls')
    msg = "You crouch beside the small hole, the peanut butter and jelly sandwich in your hand filling the air with a faint, sweet scent. Almost immediately, you hear soft shuffling from within the darkness, and the rat begins to inch its way out, eyes fixed on the sandwich. You gently place it on the floor, backing your hand away. The rat hesitates only a moment before emerging fully, the crumpled note still clamped in its teeth. It drops the note at your feet, then seizes the sandwich and drags it eagerly back into its hole, disappearing with surprising strength. With the rat gone, you reach down and pick up the note."
    slowReader(msg, True)
    inv_items.remove("XXX-T-RAT-01")
    item_code = "RAT-N-002-01"
    code_values = item_code.split('-', 3)
    slot_number = int(code_values[2])
    inv_notes[slot_number - 1] = item_code
    input("press 'enter' to continue")
    current_room = "kitchen"
    return

# Digging up the key in the garden
def event_digHole():
    global roomContents, current_room
    choices = roomContents[current_room]['choices']
    choices["3"] = {
            "Dig in the strange spot": "planter_box",
            "once": False,
            "nav": True,
            "item": False
        }
    return
    
# Gets the player out of planter_box room and removes the pristine trowel item and the dig option
def event_digHoleReturn():
    global current_room, roomContents
    current_room = "greenhouse"
    inv_items.remove("UTC-T-PTB-01")
    choices = roomContents[current_room]['choices']
    del choices['3']
    return
#^^^^^^^^^^^^^^^^^^^^^^



#----------------------
# GAME LOOP
#----------------------
while run:
    while mainMenu:
        show_mainMenu()

        dest = input('> ')

        if dest == '1':
            if check_save_data() == False:
                pass
            elif check_save_data() == True:
                slowReader("Starting a new game will erase any previous save data. Are you sure you want to start a new game?", False)
                response = input('> ')
                if response == 'yes':
                    pass
                else:
                    break
            newGame()
            show_prologue()
            mainMenu = False
            play = True
        elif dest == '2':
            if check_save_data() == False:
                slowReader("No save data found", False)
                time.sleep(2)
                break
            show_loadGame()
            loadGame()
            mainMenu = False
            play = True
        elif dest == '3':
            slowReader("Thanks for playing, bye!", False)
            time.sleep(0.5)
            os.system('cls')
            os.system('color 07')
            quit()
        else:
            print("I don't understand that command.")
    
    while pauseMenu:
        os.system('cls')
        show_pauseMenu()

        user_input = input('> ').strip()

        if user_input == '1':
            pauseMenu = False
            play = True
            play_resumed = True
            os.system('cls')
        elif user_input == '2':
            saveGame()
            print("Saving...")
            time.sleep(3)
            print("Game saved!")
            time.sleep(1)
        elif user_input == '3':
            slowReader("Any unsaved progress will be lost. Are you sure you want to quit to the main menu?", False)
            response = input("> ").lower().strip()
            if response == 'yes':
                pass
            else:
                break
            current_room = "exterior"
            inv_items = []
            inv_notes = [None, None, None, None, None, None]
            rooms_explored = []
            removed_choices = {}
            pauseMenu = False
            mainMenu = True
        elif user_input == '4':
            slowReader("Any unsaved progress will be lost. Are you sure you want to quit?", False)
            response = input("> ").lower().strip()
            if response == 'yes':
                pass
            else:
                break
            slowReader("Thanks for playing, bye!", False)
            os.system('cls')
            os.system('color 07')
            quit()
        else:
            print("I don't understand that command.")
    
    while inventoryMenu:
        os.system('cls')
        show_inventoryMenu()

        user_input = input('> ').strip()

        if user_input == '1':
            inventoryMenu = False
            itemsMenu = True
        elif user_input == '2':
            inventoryMenu = False
            notesMenu = True
        elif user_input == '0':
            inventoryMenu = False
            play = True
            play_resumed = True
        else:
            print("I don't understand that command.")

    while itemsMenu:
        os.system('cls')
        show_itemsMenu()

        user_input = input('> ').lower().strip()

        if user_input == '0':
            itemsMenu = False
            inventoryMenu = True
        elif user_input == 'r':
            if inv_items:
                slowReader("Which item would you like to remove?", False)
                remove = input('> ').strip()
                if remove in '1023456789':
                    if int(remove) in range(1, len(inv_items)+1):
                        removeItem(remove)
                    else:
                        pass
            else:
                print("I don't understand that command.")
                time.sleep(1)
        elif user_input == 'c':
            if inv_items:
                combineItems()
            else:
                print("I don't understand that command.")
                time.sleep(1)
        elif user_input in '1023456789':
            if int(user_input) in range(1, len(inv_items)+1):
                show_itemDesc(user_input)
            else:
                pass
        else:
            print("I don't understand that command.")
            time.sleep(1)

    while notesMenu:
        os.system('cls')
        show_notesMenu()

        user_input = input('> ').strip()

        if user_input == '0':
            notesMenu = False
            inventoryMenu = True
        elif user_input in '123456':
            show_noteDesc(user_input)
        else:
            print("I don't understand that command.")

    while play:
        os.system('cls')
        check_ifEvent()

        roomExplored = check_explored(current_room)
        if roomExplored == False:
            show_roomDesc(current_room, play_resumed)
        elif roomExplored == True:
            show_ReturnDesc(current_room, play_resumed)
        show_Choices(current_room, play_resumed)
        play_resumed = False

        user_input = input('> ').strip()
        choices = roomContents[current_room]['choices']

        if user_input == '0':
            play = False
            pauseMenu = True
        elif user_input == 'i':
            play = False
            inventoryMenu = True
        elif user_input in choices:
            if check_once(current_room, user_input) == True:
                if check_item(current_room, user_input) == False:
                    show_OnceDesc(current_room, user_input)
                    play_resumed = True
                    removeChoice(current_room, user_input)
                elif check_item(current_room, user_input) == True:
                    if check_invFull(current_room, user_input) == False:
                        addItem(current_room, user_input)
                        time.sleep(1)
                        play_resumed = True
                        removeChoice(current_room, user_input)
                    elif check_invFull(current_room, user_input) == True:
                        msg = "You're inventory is full."
                        slowReader(msg, False)
                        time.sleep(1)
                        play_resumed = True
                    else:
                        continue
            elif check_once(current_room, user_input) == False:
                if check_nav(current_room, user_input) == True:
                    enterRoom(current_room, user_input)
                elif check_nav(current_room, user_input) == False:
                    show_OnceDesc(current_room, user_input)
                    play_resumed = True
                else:
                    continue
            else:
                continue
        else:
            print("I don't understand that command.")
            time.sleep(1)
            play_resumed = True
#^^^^^^^^^^^^^^^^^^^^^^