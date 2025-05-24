#!/usr/bin/env python3
"""
Nusantara Mission - Interactive Text Adventure Game
"""

import os
import json
import time
import random
from typing import Dict, List, Any

class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = []
        self.current_era = "intro"
        self.completed_eras = []
        self.choices = {}  # Stores important choices made by the player

    def add_item(self, item: str):
        self.inventory.append(item)
        print(f"\n[+] {item} added to inventory!")

    def remove_item(self, item: str):
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"\n[-] {item} removed from inventory.")
            return True
        return False

    def has_item(self, item: str) -> bool:
        return item in self.inventory

    def show_inventory(self):
        print("\n=== INVENTORY ===")
        if not self.inventory:
            print("Inventory is empty.")
        else:
            for i, item in enumerate(self.inventory, 1):
                print(f"{i}. {item}")
        print("================")


class Game:
    def __init__(self):
        self.player = None
        self.eras = {
            "intro": self.era_intro,
            "majapahit": self.era_majapahit,
            "colonial": self.era_colonial,
            # Other eras will be added later
        }
        self.game_data = {}
        self.save_file = "nusantara_mission_save.json" # Renamed save file
        # self.load_game_data() # Removed - will be called during start

    def load_game_data(self):
        """Loads game data from a JSON file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    self.game_data = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Error loading game data: {e}")
            return False

    def save_game(self):
        """Saves game progress to a JSON file"""
        if not self.player:
            return False

        save_data = {
            "player_name": self.player.name,
            "inventory": self.player.inventory,
            "current_era": self.player.current_era,
            "completed_eras": self.player.completed_eras,
            "choices": self.player.choices
        }

        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            print("\n[Game saved]")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def type_text(self, text: str, delay: float = 0.03):
        """Displays text with a typing effect"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

    def show_options(self, options: List[str]) -> int:
        """Displays options and returns the chosen index"""
        print("\nOptions:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        while True:
            try:
                choice = input("\nYour choice [type number or 'm' for menu]: ")

                if choice.lower() == 'm':
                    self.show_menu()
                    print("\nOptions:") # Show options again after menu
                    for i, option in enumerate(options, 1):
                        print(f"{i}. {option}")
                    continue

                choice = int(choice)
                if 1 <= choice <= len(options):
                    return choice - 1
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number or 'm' for menu.")

    def start(self):
        self.clear_screen()

        if os.path.exists(self.save_file):
            self.type_text("Saved game data found.")
            options = ["Continue previous game", "Start new game"]
            choice = self.show_options(options)

            if choice == 0:
                if self.load_saved_game():
                    self.type_text(f"Welcome back, {self.player.name}!")
                    input("\nPress ENTER to continue...")
                else:
                    self.type_text("Failed to load saved game. Starting a new game...")
                    time.sleep(2)
                    self.new_game()
            else:
                self.new_game()
        else:
            self.new_game()

        current_era = self.player.current_era
        while current_era:
            era_function = self.eras.get(current_era)
            if era_function:
                next_era = era_function()
                if next_era:
                    self.player.current_era = next_era
                    current_era = next_era
                    self.save_game()
                else:
                    break
            else:
                print(f"Error: Era '{current_era}' not found.")
                break

        self.show_ending()

    def new_game(self):
        """Starts a new game"""
        self.clear_screen()
        title = """
███╗   ███╗██╗███████╗██╗    ███╗   ██╗██╗   ██╗███████╗ █████╗ ███╗   ██╗████████╗ █████╗ ██████╗  █████╗ 
████╗ ████║██║██╔════╝██║    ████╗  ██║██║   ██║██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
██╔████╔██║██║███████╗██║    ██╔██╗ ██║██║   ██║███████╗███████║██╔██╗ ██║   ██║   ███████║██████╔╝███████║
██║╚██╔╝██║██║╚════██║██║    ██║╚██╗██║██║   ██║╚════██║██╔══██║██║╚██╗██║   ██║   ██╔══██║██╔══██╗██╔══██║
██║ ╚═╝ ██║██║███████║██║    ██║ ╚████║╚██████╔╝███████║██║  ██║██║ ╚████║   ██║   ██║  ██║██║  ██║██║  ██║
╚═╝     ╚═╝╚═╝╚══════╝╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
        """
        print(title)
        self.type_text("\nWelcome to Nusantara Mission!")
        self.type_text("An adventure through time to save Indonesian history.")

        player_name = input("\nEnter your name: ")
        while not player_name:
            print("Name cannot be empty.")
            player_name = input("Enter your name: ")

        self.player = Player(player_name)
        self.show_intro() # Call intro after getting the name

    def load_saved_game(self):
        """Loads a saved game"""
        try:
            if self.load_game_data():
                self.player = Player(self.game_data["player_name"])
                self.player.inventory = self.game_data["inventory"]
                self.player.current_era = self.game_data["current_era"]
                self.player.completed_eras = self.game_data["completed_eras"]
                self.player.choices = self.game_data.get("choices", {})
                return True
            return False
        except Exception as e:
            print(f"Error loading saved game: {e}")
            return False

    def show_intro(self):
        """Displays the narrative intro (without the title)"""
        self.type_text(f"\nYou are {self.player.name}, a youth from the future sent back")
        self.type_text("to the past to save Indonesian history from the threat of time changes.")
        self.type_text("\nYour task is to explore various eras of Indonesian history,")
        self.type_text("complete missions, and collect important artifacts.")
        input("\nPress ENTER to start your adventure...")

    def era_intro(self):
        self.clear_screen()
        self.type_text("Year 2150, Jakarta...")
        self.type_text(f"\nProfessor Wijaya: \"{self.player.name}, you are our last hope. This time machine will")
        self.type_text("take you to various important eras in Indonesian history.\"")
        self.type_text("\nProfessor Wijaya: \"The Time Corruptors have altered our historical timeline.")
        self.type_text("Your duty is to ensure history stays on its intended path.\"")

        self.type_text("\nProfessor Wijaya hands you a device.")
        self.player.add_item("Time Chronometer")

        self.type_text("\nProfessor Wijaya: \"This Chronometer will help you travel between eras")
        self.type_text("and track historical changes. Now, prepare for your first journey.\"")

        options = ["Ready to depart for the Majapahit Kingdom era",
                   "Ask for more details about this mission"]

        choice = self.show_options(options)

        if choice == 1:
            self.clear_screen()
            self.type_text("Professor Wijaya: \"The Time Corruptors want to change Indonesian history")
            self.type_text("so that our nation never unites. They have sent agents")
            self.type_text("to various important eras to alter key events.\"")

            self.type_text("\nProfessor Wijaya: \"Your task is to find these agents,")
            self.type_text("thwart their plans, and ensure history remains on track.\"")

            input("\nPress ENTER to continue...")

        self.clear_screen()
        self.type_text("The time machine begins to vibrate. A blinding white light surrounds you.")
        self.type_text("You feel your body being pulled into a vortex of time...")
        self.type_text("\n*WHOOOSH*")

        input("\nPress ENTER to continue...")
        return "majapahit"

    def era_majapahit(self):
        self.clear_screen()

        if "majapahit" in self.player.completed_eras:
            self.type_text("You have completed the mission in the Majapahit era.")
            self.type_text("The Time Chronometer indicates the timeline here is secure.")
            options = ["Revisit the Majapahit era", "Continue to the next era"]
            choice = self.show_options(options)
            if choice == 1:
                return "colonial"

        self.type_text("Year 1350, Majapahit Kingdom...")
        self.type_text("\nYou arrive in a bustling market. People in traditional attire")
        self.type_text("pass by. The air is filled with the scent of spices.")
        self.type_text("\nThe Time Chronometer blinks, displaying a message:")
        self.type_text("\"MISSION: Ensure Gajah Mada still utters the Palapa Oath\"")
        self.type_text("\nAn old merchant approaches you.")
        self.type_text("Merchant: \"You're not from around here, young one. Your clothes are strange.\"")

        options = [
            "Say you are an envoy from a distant kingdom",
            "Ask about Gajah Mada",
            "Inquire about recent strange occurrences"
        ]
        choice = self.show_options(options)
        self.player.choices["majapahit_merchant"] = choice

        if choice == 0:
            self.clear_screen()
            self.type_text("You: \"I am an envoy from a distant kingdom, here to meet the leader of Majapahit.\"")
            self.type_text("\nMerchant: \"Hmm, suspicious. But if you wish to meet the leader,")
            self.type_text("you must go to the palace. Be careful, security has been tight lately.\"")
            self.type_text("\nThe merchant gives you a batik cloth.")
            self.player.add_item("Majapahit Batik Cloth")
            self.type_text("\nMerchant: \"Wear this so you don't stand out so much.\"")
        elif choice == 1:
            self.clear_screen()
            self.type_text("You: \"I wish to know about Gajah Mada. Where can I find him?\"")
            self.type_text("\nMerchant: \"Gajah Mada? Our great Mahapatih? He is in great trouble.")
            self.type_text("I hear someone has poisoned his mind, making him doubt his own oath.\"")
            self.type_text("\nMerchant: \"If you want to see him, he is at Lingsar Temple")
            self.type_text("seeking peace. But beware, there are suspicious strangers around him.\"")
        else:
            self.clear_screen()
            self.type_text("You: \"Have there been any strange occurrences lately?\"")
            self.type_text("\nMerchant: \"Indeed! A strangely dressed foreigner like you arrived")
            self.type_text("a few days ago. He became close to Gajah Mada's advisors, and since then,")
            self.type_text("our Mahapatih has begun to doubt his plan to unite Nusantara.\"")
            self.type_text("\nMerchant: \"If you wish to know more, seek Empu Tantular in the palace library.\"")
            self.type_text("He suspects something about that foreigner.")

        self.type_text("\nWhere will you go next?")
        locations = ["Majapahit Palace", "Lingsar Temple", "Palace Library"]
        location_choice = self.show_options(locations)
        self.player.choices["majapahit_location"] = location_choice

        self.clear_screen()
        self.type_text(f"You decide to go to {locations[location_choice]}...")
        self.type_text("\n[This part will be developed further]")
        input("\nPress ENTER to continue...")

        self.clear_screen()
        self.type_text("After various adventures in the Majapahit era...")
        self.type_text("\nYou managed to foil the Time Corruptors' plans and ensure")
        self.type_text("Gajah Mada still utters the Palapa Oath, keeping the timeline intact.")
        self.type_text("\nThe Time Chronometer blinks, signaling your mission here is complete.")
        self.type_text("Time to move to the next era...")
        self.player.completed_eras.append("majapahit")
        input("\nPress ENTER to continue...")
        return "colonial"

    def era_colonial(self):
        """Dutch Colonial Era"""
        self.clear_screen()

        if "colonial" in self.player.completed_eras:
            self.type_text("You have completed the mission in the Dutch Colonial era.")
            self.type_text("The Time Chronometer indicates the timeline here is secure.")
            options = ["Revisit the Dutch Colonial era", "Continue to the next era"]
            choice = self.show_options(options)
            if choice == 1:
                return None # No 'independence' era yet

        self.type_text("Year 1830, Batavia...")
        self.type_text("\nYou arrive at a busy port. Large ships are docked,")
        self.type_text("transporting spices and other produce. Dutch soldiers")
        self.type_text("patrol the harbor.")
        self.type_text("\nThe Time Chronometer blinks, displaying a message:")
        self.type_text("\"MISSION: Ensure the Forced Cultivation System still incites public resistance\"")
        self.type_text("\nAn old man in shabby clothes approaches you.")
        self.type_text("Old Man: \"Be careful, young one. Your clothes are too conspicuous.")
        self.type_text("The Company is always suspicious of strangers.\"")

        options = [
            "Ask about the conditions in Batavia",
            "Learn about the Forced Cultivation System",
            "Ask about public resistance"
        ]
        choice = self.show_options(options)
        self.player.choices["colonial_intro"] = choice

        if choice == 0:
            self.clear_screen()
            self.type_text("You: \"What are the conditions in Batavia like right now?\"")
            self.type_text("\nOld Man: \"Bad, very bad. The Company is becoming crueler with")
            self.type_text("their new policies. People are forced to grow crops they")
            self.type_text("want, not what we need to eat.\"")
            self.type_text("\nOld Man: \"Many are starving, sick, even dying. But")
            self.type_text("they don't care as long as their warehouses are full of spices and coffee.\"")
        elif choice == 1:
            self.clear_screen()
            self.type_text("You: \"Can you tell me about the Forced Cultivation System?\"")
            self.type_text("\nOld Man: \"Ah, you don't know? Cultuurstelsel, they call it.")
            self.type_text("We are forced to use 20% of our land to grow export crops:")
            self.type_text("coffee, sugarcane, indigo, tobacco... not the rice we need.\"")
            self.type_text("\nOld Man: \"What's strange is, recently a foreigner like you")
            self.type_text("was seen talking to the Governor-General. Since then, there are rumors")
            self.type_text("the system will be changed to be more 'humane'. That must not happen!\"")
            self.type_text("\nYou: \"Why not?\"")
            self.type_text("\nOld Man: \"Because it is the cruelty of this system that will spark")
            self.type_text("a great resistance! If the system is softened, the people will not")
            self.type_text("rise against the colonizers!\"")
        else:
            self.clear_screen()
            self.type_text("You: \"Is there any resistance from the people?\"")
            self.type_text("\nOld Man: \"Shh! Not so loud. Yes, of course, there is.")
            self.type_text("The Diponegoro War just ended five years ago, but")
            self.type_text("the spirit of resistance still burns in the people's hearts.\"")
            self.type_text("\nOld Man: \"But something is odd. Lately, some resistance leaders")
            self.type_text("have suddenly disappeared or changed their stance.")
            self.type_text("It's as if someone is deliberately trying to quell the flames.\"")
            self.type_text("\nThe Old Man gives you a letter.")
            self.player.add_item("Secret Letter")
            self.type_text("\nOld Man: \"This is a letter from one of the resistance leaders.")
            self.type_text("Please investigate what is happening. Meet Sentot Prawirodirjo")
            self.type_text("at the market tonight. He will recognize you by this letter.\"")

        self.type_text("\nWhere will you go next?")
        locations = ["Governor-General's Office", "Batavia Market", "Plantation on the outskirts"]
        location_choice = self.show_options(locations)
        self.player.choices["colonial_location"] = location_choice

        self.clear_screen()
        self.type_text(f"You decide to go to {locations[location_choice]}...")

        if location_choice == 0:
            self.type_text("\nYou arrive in front of a grand European-style building. Tight security")
            self.type_text("with armed soldiers at every corner.")
            self.type_text("\nA soldier stops you.")
            self.type_text("Soldier: \"Halt! Who are you and what is your business?\"")
            if self.player.has_item("Dutch Permit") or self.player.has_item("Dutch Official Uniform"): # Example items
                self.type_text("\nYou show your fake identification.")
                self.type_text("Soldier: \"Please proceed, Sir.\"")
                self.type_text("\nInside, you see a man in futuristic clothing")
                self.type_text("talking to the Governor-General. It must be a Time Corruptor!")
            else:
                self.type_text("\nYou have no way to get inside.")
                self.type_text("You decide to go back and find another way.")
        elif location_choice == 1:
            self.type_text("\nThe market is bustling with activity. Local and")
            self.type_text("foreign traders mingle, selling their goods.")
            self.type_text("\nYou look for Sentot Prawirodirjo as mentioned,")
            self.type_text("if you have the Secret Letter.")
            if self.player.has_item("Secret Letter"):
                self.type_text("\nA man in a turban approaches you.")
                self.type_text("Man: \"You carry the letter. Follow me.\"")
                self.type_text("\nHe leads you to a hidden warehouse.")
                self.type_text("Man: \"I am Sentot. We know about the foreigner")
                self.type_text("trying to change history. He's trying to make the Cultivation")
                self.type_text("System less cruel, so the resistance won't happen.\"")
                self.player.add_item("Secret Map")
                self.type_text("\nSentot gives you a map.")
                self.type_text("Sentot: \"This map leads to their secret base.")
                self.type_text("Stop their plan before it's too late.\"")
            else:
                self.type_text("\nYou wander around the market, gathering information.")
                self.type_text("Some traders talk about secret meetings")
                self.type_text("between Dutch officials and a suspicious foreigner.")
                self.player.add_item("Secret Meeting Info")
        else:
            self.type_text("\nYou arrive at a vast plantation. Dozens of natives work")
            self.type_text("under the hot sun, watched by Dutch overseers.")
            self.type_text("\nYou witness the cruelty of the system firsthand.")
            self.type_text("\nAn old worker quietly approaches you.")
            self.type_text("Worker: \"Sir, please help us. There's talk the system")
            self.type_text("will change, but not for our benefit. They just")
            self.type_text("want to prevent future resistance.\"")
            self.type_text("\nWorker: \"Meet the Resistance Leader in the cave on that hill")
            self.type_text("tonight. He will tell you everything.\"")
            self.player.add_item("Resistance Base Location")

        input("\nPress ENTER to continue...")

        self.clear_screen()
        self.type_text("After various adventures in the Dutch Colonial era...")
        self.type_text("\nYou managed to foil the Time Corruptors' plans and ensure")
        self.type_text("the Forced Cultivation System still incites resistance, keeping")
        self.type_text("the historical path of the independence struggle intact.")
        self.type_text("\nThe Time Chronometer blinks, signaling your mission here is complete.")
        self.type_text("Time to move to the next era...")
        self.player.completed_eras.append("colonial")
        input("\nPress ENTER to continue...")
        return None  # End the game here for now

    def show_ending(self):
        self.clear_screen()
        completed_count = len(self.player.completed_eras)

        if completed_count == 0:
            self.type_text("You haven't completed a single mission...")
            self.type_text("The journey through time is long. Indonesian history awaits you!")
        elif completed_count == 1:
            self.type_text(f"You have completed 1 era: {self.player.completed_eras[0].capitalize()}")
            self.type_text("But many more eras need saving!")
        else:
            self.type_text(f"You have completed {completed_count} eras:")
            for era in self.player.completed_eras:
                self.type_text(f"- {era.capitalize()}")

            if "majapahit" in self.player.completed_eras and "colonial" in self.player.completed_eras:
                self.type_text("\nYou have saved two important eras in Indonesian history!")
                self.type_text("But your journey isn't over. Other eras still await.")

        self.type_text("\nThank you for playing Nusantara Mission!")
        self.type_text("This game is still under development.")
        self.type_text("Other eras like the proclamation of independence will be added later.")

        options = ["Play again", "Exit"]
        choice = self.show_options(options)

        if choice == 0:
            self.player = None # Reset player for a new game
            self.start()
        else:
            self.type_text("\nSee you in the next adventure!")
            exit(0)

    def show_menu(self):
        """Displays the in-game menu"""
        self.clear_screen()
        self.type_text("=== MENU ===")
        options = [
            "Continue game",
            "Show inventory",
            "Save game",
            "Exit" # Simplified menu
        ]

        choice = self.show_options(options)

        if choice == 0:
            self.clear_screen()
            return  # Continue game
        elif choice == 1:
            self.player.show_inventory()
            input("\nPress ENTER to return...")
            return self.show_menu()
        elif choice == 2:
            self.save_game()
            input("\nPress ENTER to return...")
            return self.show_menu()
        else: # Exit
            self.type_text("\nAre you sure you want to exit? (y/n)")
            confirm = input("> ").lower()
            if confirm == 'y':
                self.type_text("\nThank you for playing Nusantara Mission!")
                exit(0)
            else:
                return self.show_menu()


if __name__ == "__main__":
    game = Game()
    game.start()
