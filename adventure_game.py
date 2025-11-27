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

# Other global booleans
skip_Description = False
play_resumed = False

# Player Stats <= Stuff that needs to be 'saved' and recalled when 'loaded'
current_room = "exterior"
inv_items = []
inv_notes = [None, None, None, None, None, None]
removed_items = []
rooms_explored = []

# example change on master branch

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
    ...

# Loads relevant game data from a .txt file and continues the game from there
def loadGame():
    ...

# When nav = true, changes current_room based on user_input
def enterRoom(room_key: str, user_input: str):
    global roomContents, current_room

    roomContents[room_key]['explored'] = True 
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

# Removes choice from list of choices for a room
def removeChoice(room_key:str, user_input: str):
    global roomContents

    choices = roomContents[room_key]['choices']
    del choices[user_input]
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
        print('\n r - Remove Item')        
    print(' 0 - Return')
    print('\n' + textDivide)

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

# Shows Game Intro
def show_gameIntro():
    global current_room, gameChoices, commands
    current_room = "exterior"
    
    os.system('cls')
    with open('./text/introduction.txt', 'r', errors='ignore') as file:
        content = file.read()
    slowReader(content, True)
    time.sleep(2)
    print("press 'enter' to continue")
    input('')

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
    removeChoice(room_key, user_input)

# Show current options
def show_Choices(room_key: str, toggleType: bool):
    global roomContents

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
    global roomContents

    explored = roomContents[room_key]['explored']
    if explored == False:
        return False  # <= First time visit
    elif explored == True:
        return True   # <= Return to room
    else:
        print('ERROR: check_explored')

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
    global itemContents

    hasItem = itemContents[item_code]['hasItem']
    if hasItem == False:
        return False
    elif hasItem == True:
        return True
    else:
        print('ERROR: check_hasItem')

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

# Removes an item from the player's inventory and places it in the current_room
def removeItem(user_input: str):
    global roomContents, itemContents, inv_items

    item = inv_items[int(user_input) - 1]
    if check_essential(item) == False:
        msg = "Once you remove and item it will be lost forever. Are you sure you want to remove this item?"
        slowReader(msg, False)
        removePrompt = input('> ').lower().strip()
        if removePrompt == 'yes':
            item = inv_items[int(user_input) - 1]
            if item in inv_items:
                inv_items.remove(item)
                removed_items.append(item)
            else:
                return
            msg = show_removeItemDesc(item)
            slowReader(msg, False)
            time.sleep(1)
        else:
            print("Remove canceled")
            time.sleep(1)
    elif check_essential(item) == True:
        msg = show_removeItemDesc(item)
        slowReader(msg, False)
        time.sleep(1)
        return
    else:
        print("ERROR: removeItem")

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

def show_removeItemDesc(item_code: str) -> str:
    global itemContents

    item = itemContents[item_code]
    if item:
        return item.get('removeDescription')
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
# GAME LOOP
#----------------------
while run:
    while mainMenu:
        show_mainMenu()
        
        dest = input('> ')

        if dest == '1':
            print('Loading...')
            time.sleep(3)
            print("New game!")
            time.sleep(1)
            show_gameIntro()
            mainMenu = False
            play = True
        elif dest == '2':
            print('Loading...')
            time.sleep(3)
            print("Game loaded!")
            time.sleep(1)
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

        user_input = input('> ')

        if user_input == '1':
            pauseMenu = False
            play = True
            play_resumed = True
            os.system('cls')
        elif user_input == '2':
            saveGame()
            print("Game saved!")
            time.sleep(1)
        elif user_input == '3':
            pauseMenu = False
            mainMenu = True
        elif user_input == '4':
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
                    if check_nav(current_room, user_input) == True:
                        enterRoom(current_room, user_input)
        else:
            print("I don't understand that command.")
            time.sleep(1)
            play_resumed = True
#^^^^^^^^^^^^^^^^^^^^^^