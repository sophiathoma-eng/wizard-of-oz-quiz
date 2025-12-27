import time
import os
import sys
import threading

# -----------------------------
# ANSI ESCAPE CODES
# -----------------------------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
MOVE_CURSOR_UP = "\033[A"
CLEAR_CURRENT_LINE = "\x1b[2K"

# -----------------------------
# SIMPLE BEEP
# (only works on unix systems)
# -----------------------------

UNIX_BEEP = 'printf "\a"'

def beep_correct():
    if os.name != 'nt':
        os.system(UNIX_BEEP)

def beep_wrong():
    if os.name != 'nt':
        os.system(UNIX_BEEP)
        os.system(UNIX_BEEP)


# -----------------------------
# CLEAR SCREEN
# -----------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# -----------------------------
# HIGH SCORE SYSTEM
# -----------------------------
HIGHSCORE_FILE = "oz_highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


# -----------------------------
# TITLE SCREEN
# -----------------------------
def title_screen():
    clear_screen()
    print(MAGENTA + "==============================")
    print("     WIZARD OF OZ QUIZ GAME 🌈")
    print("==============================" + RESET)
    print(CYAN + "3 Levels • Timed Questions • Highscore" + RESET)
    print(YELLOW + f"Current Highscore: {load_highscore()} ⭐" + RESET)
    input(GREEN + "\nPress ENTER to begin..." + RESET)


# -----------------------------
# QUESTION OBJECT
# -----------------------------
class Question:
    def __init__(self, text, options, answer, time_limit=12):
        self.text = text
        self.options = options
        self.answer = answer
        self.time_limit = time_limit

    def ask(self):
        """Zeigt die Frage, startet einen Countdown-Thread und prüft Antwort/Zeit."""
        print(BLUE + "\n" + self.text + RESET)
        for opt in self.options:
            print(opt)

        print(YELLOW + f"You have {self.time_limit} seconds ⏳" + RESET)

        # flag für den Countdown-Thread
        thread_shared = {'answered': False}

        def countdown():
            for remaining in range(self.time_limit, 0, -1):
                if thread_shared['answered']:
                    break
                
                # Cursor zurück zum Anfang der Zeile bewegen, wenn es nicht die erste Anzeige ist
                prefix = '\r' if remaining == self.time_limit else f'{MOVE_CURSOR_UP}\r'

                print(f"{prefix}{CLEAR_CURRENT_LINE}Time remaining: {remaining} seconds\nYour answer (A/B/C): ", end="", flush=True)
                time.sleep(1)
            if not thread_shared['answered']:
                print(f"{CLEAR_CURRENT_LINE}{MOVE_CURSOR_UP}{CLEAR_CURRENT_LINE}")

                print(RED + f"⏳ Too slow! You took {int(self.time_limit)} seconds." + RESET)
                beep_wrong()

        # Countdown threaded starten
        t = threading.Thread(target=countdown, daemon=True)
        t.start()

        user_answer = input("").upper()
        thread_shared['answered'] = True

        if user_answer == self.answer:
            print(GREEN + "Correct! 🌟" + RESET)
            beep_correct()
            return True
        else:
            print(RED + "Incorrect ❌" + RESET)
            beep_wrong()
            return False


# -----------------------------
# QUIZ OBJECT
# -----------------------------
class Quiz:
    def __init__(self, levels):
        self.levels = levels  # list of lists of Question objects
        self.score = 0

    def start(self):
        title_screen()
        self.story_intro()

        level_number = 1
        for level in self.levels:
            self.play_level(level, level_number)
            level_number += 1

        self.show_results()
        self.ask_replay()

    def story_intro(self):
        clear_screen()
        print(CYAN + "You awaken in a dazzling land full of color and magic..." + RESET)
        time.sleep(2)
        print(CYAN + "Toto runs toward you barking excitedly 🐶" + RESET)
        time.sleep(2)
        print(CYAN + "He wants you to follow the Yellow Brick Road..." + RESET)
        time.sleep(2)
        print(YELLOW + "\nYour adventure in Oz begins now! 🌟" + RESET)
        input(GREEN + "Press ENTER to continue." + RESET)

    def play_level(self, level_questions, level_number):
        clear_screen()
        print(MAGENTA + f"===== LEVEL {level_number} =====" + RESET)
        time.sleep(1)

        for question in level_questions:
            correct = question.ask()
            if correct:
                self.score += 1
            time.sleep(1)

    def show_results(self):
        clear_screen()
        print(MAGENTA + "===== QUIZ COMPLETE =====" + RESET)
        print(YELLOW + f"You scored {self.score} points! 🎉" + RESET)

        high = load_highscore()
        if self.score > high:
            print(GREEN + "🎉 NEW HIGHSCORE! 🎉" + RESET)
            save_highscore(self.score)
        else:
            print(CYAN + f"Highscore remains at: {high} ⭐" + RESET)

    def ask_replay(self):
        answer = input(CYAN + "Play again? (yes/no): " + RESET).lower()
        if answer == "yes":
            self.score = 0
            self.start()
        else:
            print(GREEN + "Thanks for playing! Goodbye 👋" + RESET)
            sys.exit()


# -----------------------------
# QUESTIONS (mit Emojis & Levels)
# -----------------------------
level1 = [
    Question(
        "Who is the main girl in the story?",
        ["A: Dorothy 🌪️", "B: Alice 🐇", "C: Wendy 🧚"],
        "A"
    ),
    Question(
        "What magical shoes does Dorothy wear?",
        ["A: Ruby slippers 👠", "B: Boots 🥾", "C: Sneakers 👟"],
        "A"
    )
]

level2 = [
    Question(
        "What is the name of Dorothy’s dog?",
        ["A: Scooby 🐕", "B: Toto 🐶", "C: Bella 🐩"],
        "B"
    ),
    Question(
        "What color is the famous road leading to Oz?",
        ["A: Blue road 💙", "B: Red road ❤️", "C: Yellow road 💛"],
        "C"
    ),
]

level3 = [
    Question(
        "What does the Scarecrow want from the Wizard?",
        ["A: A brain 🧠", "B: A heart ❤️", "C: Courage 🦁"],
        "A"
    ),
    Question(
        "Which witch is defeated by water?",
        ["A: Good Witch of the North ✨",
         "B: Wicked Witch of the West 🧹",
         "C: Wicked Witch of the East 🌪️"],
        "B"
    ),
    Question(
        "What does the Tin Man want?",
        ["A: A new hat 🎩", "B: A heart ❤️", "C: A house 🏠"],
        "B"
    ),
    Question(
        "Which friends travel with Dorothy?",
        ["A: Scarecrow, Tin Man, Lion",
         "B: Fairy, Dragon, Knight",
         "C: Dwarf, Elf, Giant"],
        "A"
    )
]

all_levels = [level1, level2, level3]

# -----------------------------
# START GAME
# -----------------------------
if __name__ == "__main__":
    quiz = Quiz(all_levels)
    quiz.start()

