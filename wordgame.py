import random
import requests
from functools import reduce

# Constants
FLAG_LOST = '#'

# Function to check if a word fragment is valid according to the dictionary
def is_valid_fragment(fragment, dictionary):
    return reduce(lambda acc, val: acc or val,
                  map(lambda word: word.startswith(fragment) or word.endswith(fragment), dictionary),
                  False)

# Function to check if a word fragment can lead to a complete word
def can_form_complete_word(fragment, dictionary):
    return reduce(lambda acc, val: acc or val,
                  map(lambda word: (word.startswith(fragment) or word.endswith(fragment)) and len(word) > len(fragment),
                      dictionary),
                  False)
    
def fetch_dictionary(url):   
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text      
    except requests.RequestException as e:
        print(f"Error fetching dictionary: {e}")
        return None

def process_dictionary(raw_text):
    if raw_text:
        return raw_text.splitlines()
    return ["apple", "apply", "applicable", "apex", "bat", "battle", "cat", "cater", "dog", "dodge"]

def load_dictionary():
    url = "https://raw.githubusercontent.com/powerlanguage/word-lists/refs/heads/master/1000-most-common-words.txt"
    raw_text = fetch_dictionary(url)
    return process_dictionary(raw_text)

def validate_move():
    move = input("Add a letter at the (B)eginning or (E)nd? ").strip().upper()
    if move in ("B", "E"):
        return move
    print("Invalid choice. Please enter 'B' for beginning or 'E' for end.")
    return validate_move()

# Function to add a letter to the current word based on the move
def add_letter(current_word, move, letter):
    return letter + current_word if move == "B" else current_word + letter

# Generate possible moves using map and lambda
def generate_possible_moves(current_word, dictionary):
    return list(filter(
        lambda x: is_valid_fragment(x[1], dictionary),
        map(lambda x: (x, add_letter(current_word, x[0], x[1])),
            [("B", letter) for letter in "abcdefghijklmnopqrstuvwxyz"] + [("E", letter) for letter in "abcdefghijklmnopqrstuvwxyz"])
    ))

# Choose a move that keeps options open and prioritizes the shortest possible word
def choose_optimal_move(possible_moves, dictionary):
    best_move = None

    for move in possible_moves:
        fragment = move[1]

        for word in dictionary:
            if (word.startswith(fragment) or word.endswith(fragment)) and (
                not best_move or len(word) < len(best_move[1])
            ):
                best_move = (move, word)

    return best_move[0] if best_move else possible_moves[0] if possible_moves else None


# Function to play a single turn
def play_turn(current_word, player_turn, dictionary):
    print(f"Current word fragment: '{current_word}'")

    if player_turn:
        current_word = player_move(current_word, dictionary)
    else:
        current_word = computer_move(current_word, dictionary)

    if current_word == FLAG_LOST: return

    # Check if the current word fragment cannot lead to any valid words
    if not can_form_complete_word(current_word, dictionary):
        print(f"'{current_word}' cannot form any valid word. Game over!")
        print("You win!" if player_turn else "Computer wins!")
        return

    # Recursively call play_turn for the next turn
    play_turn(current_word, not player_turn, dictionary)

def player_move(current_word, dictionary):
    print("Your turn!")
    move = validate_move()
    letter = input("Enter a letter: ").strip().lower()

    new_fragment = add_letter(current_word, move, letter)

    if not is_valid_fragment(new_fragment, dictionary):
        print(f"'{new_fragment}' is not a valid fragment. You lose!")
        return FLAG_LOST

    return new_fragment


def computer_move(current_word, dictionary):
    print("Computer's turn!")
    possible_moves = generate_possible_moves(current_word, dictionary)

    if not possible_moves:
        print("The computer cannot make a valid move. You win!")
        return FLAG_LOST

    chosen_move = choose_optimal_move(possible_moves, dictionary)
    print(f"Computer chose to add '{chosen_move[0][1]}' at the {'beginning' if chosen_move[0][0] == 'B' else 'end'}.")

    return chosen_move[1]

# Main function for the game
def play_game():
    print("Welcome to the Word Building Game!")

    # Load dictionary
    dictionary = load_dictionary()

    # Start the game with initial state
    play_turn("", True, dictionary)

play_game()