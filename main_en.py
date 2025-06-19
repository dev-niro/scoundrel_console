import argparse
import random
import json
import sys

# System arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode",
    type=str,
    default="normal"
)
parser.add_argument(
    "--language",
    type=str,
    default="es"
)
args = parser.parse_args()

# Language
def load_locale(lang="es"):
    with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)

T = load_locale(args.language)

# Deck init
# Scoundrel does not use jokers or red face cards. A counts as a face card
SUITS = ['♠', '♣', '♦', '♥']
VALUES = list(range(2, 11)) + ['A', 'J', 'Q', 'K']
DECK = [f"{v}{s}" for s in SUITS for v in VALUES if not (s in ['♦', '♥'] and isinstance(v, str))]

# Game state
state = {
    "life": 20,  # Starting life total
    "weapon": 0,  # Currently equipped weapon
    "last_monster_killed": 0,  # Last monster defeated with the equipped weapon
    "room": [],  # Currently displayed cards (the room)
    "deck": DECK.copy(),  # Initial deck; in the future, there may be different decks
    "healed": False,  # Indicates whether a potion has already been used in the current room
    "avoided": False  # Indicates whether the current room has already been avoided
}

# Helpers
def get_value(card):
    # Face cards values
    values = {
        'A': 14,
        'K': 13,
        'Q': 12,
        'J': 11
    }
    # Remove the suit from the card
    value = card[:-1]
    return int(values.get(value, value))  
 
def get_suit(card):
    return card[-1]

def shuffle_deck():
    random.shuffle(state["deck"])

def fill_room():
    # Cleanup
    state['healed'] = False
    state['room'] = []
    # Draw four cards
    for _ in range(4):
        if state['deck']:
            state["room"].append(state["deck"].pop(0))

def UI():
    print(T['health_bar'].format(life=state['life'], weapon=state['weapon'], last_monster_killed=state['last_monster_killed']))
    print(T["room_display"].format(cards=", ".join(state["room"])))
    print(T["deck_quantity"].format(deck=len(state["deck"])))

def life_loss(value, type):
    state["life"] -= value
    attack_types ={
        1: T['barehanded'],
        2: T['weapon_fight']
    }
    text = attack_types.get(type, T['barehanded'])
    print(T['life_loss'].format(text=text,value=value))

def change_room():
    state["avoided"] = True
    state["deck"].extend(state["room"])
    fill_room()
    print(T["room_avoided"])

def restart():
    state["life"] = 20
    state["weapon"] = 0
    state["last_monster_killed"] = 0
    state["deck"] = DECK.copy()
    shuffle_deck()
    fill_room()
    if args.mode == "test":
        del state["deck"][:30]

def verify_defeat():
    if state["life"] <= 0:
        print(T["defeat"])
        restart()

def verify_victory():
    if not state["deck"] and not state["room"]:
        print(T["victory"])
        restart()

def pick_card(index):
    try:
        card = state["room"].pop(index-1)
    except IndexError:
        print(T["error_index"])
        return

    value = get_value(card)
    suit = get_suit(card)

    if suit == '♥':
        if state["healed"] == False:
            state["healed"] = True
            gained = min(20 - state["life"], value)
            state["life"] += gained
            print(T["life_gained"].format(gained=gained))
        else:
            print(T["already_healed"])
    elif suit == '♦':
        state["weapon"] = value
        state["last_monster_killed"] = 0
        print(T["equipped"].format(value=value))
    else:
        if state["weapon"] == 0 or (value >= state["last_monster_killed"] and state["last_monster_killed"] != 0):
            life_loss(value,1)
        else: 
            print(T["fight_style"])
            option = input(">> ").strip().lower()
            if  option == 'n':
                life_loss(value,1)
            else:
                damage = max(value - state["weapon"], 0)
                state["last_monster_killed"] = value
                life_loss(damage,2)

    if len(state["room"]) == 1:
        state["healed"] = False
        state["avoided"] = False
        print(T["new_room"])
        for _ in range(3):
            if state["deck"]:
                state["room"].append(state["deck"].pop(0))

    verify_defeat()
    verify_victory()

# GAME LOOP
def main():
    restart()
    while True:
        UI()
        print("\n" + T["pick_card"])
        print(" " + T["choose_position"].format(n=len(state["room"])))
        if len(state["room"]) == 4 and state["avoided"]==False:
            print(" " + T["avoid_room"])
        print(" " + T["quit_game"])
        option = input(">> ").strip().lower()

        if option in ['4', '1', '2', '3']:
            pick_card(int(option))
        elif option == 'r' and len(state["room"]) == 4 and state["avoided"]==False and state["deck"]:
            change_room()
        elif option == 'q':
            print(T["goodbye"])
            break
        else:
            print(T["invalid_command"])

if __name__ == "__main__":
    main()
