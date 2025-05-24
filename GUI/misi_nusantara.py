#!/usr/bin/env python3
"""
Nusantara Mission - Pygame Enhanced Text Adventure
"""

import os
import json 
import time
import random
import pygame

# --- Pygame Setup ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)
LIGHT_GREY = (150, 150, 150) 
TEXT_BOX_COLOR = (40, 40, 50) 
TEXT_BOX_BORDER_COLOR = (100, 100, 120)
BUTTON_BASE_COLOR = (60, 60, 80)
BUTTON_HOVER_COLOR = (90, 90, 120) 
BUTTON_TEXT_COLOR = WHITE
NARRATIVE_TEXT_COLOR = (230, 230, 230) 
TITLE_TEXT_COLOR = (255, 215, 0) 
ERA_TITLE_COLOR = (200, 200, 255) 
EVENT_MSG_COLOR = (173, 255, 47) # Greenyellow untuk pesan event

# Font setup
FONT_NAME_PATH = "Merriweather_24pt-Regular.ttf" 
DEFAULT_FONT_SIZE = 22 
OPTION_FONT_SIZE = 18
TITLE_FONT_SIZE = 52
ERA_TITLE_FONT_SIZE = 28
MENU_FONT_SIZE = 24

# Text Box and Options Area
TEXT_BOX_ACTUAL_HEIGHT = 250 
TEXT_BOX_RECT = pygame.Rect(
    50, 
    (SCREEN_HEIGHT - TEXT_BOX_ACTUAL_HEIGHT) // 2 + 30, 
    SCREEN_WIDTH - 100, 
    TEXT_BOX_ACTUAL_HEIGHT
)
NARRATIVE_AREA_RECT = pygame.Rect(
    TEXT_BOX_RECT.x + 20, 
    TEXT_BOX_RECT.y + 20, 
    TEXT_BOX_RECT.width - 40, 
    TEXT_BOX_RECT.height - 150 
)
OPTIONS_START_Y = NARRATIVE_AREA_RECT.bottom + 15
# Define BUTTON_HEIGHT before OPTION_SPACING
BUTTON_HEIGHT = 35 
OPTION_SPACING = BUTTON_HEIGHT + 5 # Total step for next button (button height + gap)

SAVE_FILE_NAME = "nusantara_mission_pygame_save.json"

# --- Helper Functions ---

def render_text_wrapped(surface, text, font, color, rect, aa=True, bkg=None, line_spacing_modifier=1.0):
    lines = text.splitlines()
    y = rect.top
    line_spacing = int(font.get_linesize() * line_spacing_modifier)

    for line in lines:
        words = line.split(' ')
        current_line_text = ""
        while words:
            word = words.pop(0)
            test_line = current_line_text + word + " "
            if font.size(test_line)[0] < rect.width:
                current_line_text = test_line
            else:
                if current_line_text.strip(): 
                    text_surface = font.render(current_line_text.strip(), aa, color, bkg)
                    surface.blit(text_surface, (rect.left, y))
                y += line_spacing
                current_line_text = word + " "
                if y + line_spacing > rect.bottom: 
                    if current_line_text.strip():
                         text_surface = font.render(current_line_text.strip(), aa, color, bkg)
                         surface.blit(text_surface, (rect.left, y))
                         y += line_spacing
                    return y 
        
        if current_line_text.strip(): 
            text_surface = font.render(current_line_text.strip(), aa, color, bkg)
            surface.blit(text_surface, (rect.left, y))
            y += line_spacing
        if y + line_spacing > rect.bottom and lines.index(line) < len(lines) -1 : 
             return y 
    return y


class Button:
    def __init__(self, x, y, width, height, text, font, 
                 base_color=BUTTON_BASE_COLOR, 
                 hover_color=BUTTON_HOVER_COLOR, 
                 text_color=BUTTON_TEXT_COLOR,
                 border_radius=7,  
                 border_width=0,   
                 border_color=None,
                 action_tag=None): 
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_bg_color = base_color
        self.is_hovered = False
        self.border_radius = border_radius
        self.border_width = border_width
        self.border_color = border_color if border_color else base_color 
        self.action_tag = action_tag if action_tag else text 

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_bg_color, self.rect, self.border_width, self.border_radius)
        if self.border_width > 0 and self.border_color: 
             pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, self.border_radius)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_bg_color = self.hover_color
            self.is_hovered = True
        else:
            self.current_bg_color = self.base_color
            self.is_hovered = False

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# --- Player Class ---
class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = []
        self.completed_eras = []
        self.choices = {} 

    def add_item(self, item: str, game_instance): 
        if item not in self.inventory:
            self.inventory.append(item)
            game_instance.add_event_message(f"[+] '{item}' added to inventory!")
        else:
            game_instance.add_event_message(f"You already have '{item}'.")


    def has_item(self, item: str) -> bool:
        return item in self.inventory
        
    def get_inventory_display(self):
        if not self.inventory:
            return ["Inventory is empty."]
        return [f"{i+1}. {item}" for i, item in enumerate(self.inventory)]
    
    def to_dict(self):
        return {
            "name": self.name,
            "inventory": self.inventory,
            "completed_eras": self.completed_eras,
            "choices": self.choices
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"])
        player.inventory = data["inventory"]
        player.completed_eras = data["completed_eras"]
        player.choices = data["choices"]
        return player

# --- Game Class ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nusantara Mission")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = None
        
        self.game_state = "START_MENU" 
        self.current_era_title = "" 
        
        try:
            self.base_font = pygame.font.Font(FONT_NAME_PATH, DEFAULT_FONT_SIZE)
            self.option_font = pygame.font.Font(FONT_NAME_PATH, OPTION_FONT_SIZE)
            self.title_font = pygame.font.Font(FONT_NAME_PATH, TITLE_FONT_SIZE)
            self.era_title_font = pygame.font.Font(FONT_NAME_PATH, ERA_TITLE_FONT_SIZE)
            self.menu_font = pygame.font.Font(FONT_NAME_PATH, MENU_FONT_SIZE)
        except Exception as e:
            print(f"Font error: {e}. Using Pygame default font.")
            self.base_font = pygame.font.Font(None, DEFAULT_FONT_SIZE + 6) 
            self.option_font = pygame.font.Font(None, OPTION_FONT_SIZE + 4)
            self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE + 10)
            self.era_title_font = pygame.font.Font(None, ERA_TITLE_FONT_SIZE + 6)
            self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE + 6)


        self.current_narrative_text = ""
        self.current_options_buttons = [] 
        self.event_messages = [] 
        
        self.input_text = "" 
        self.name_input_active = False
        self.previous_game_state = None 

        self.background_colors = {
            "START_MENU": (30, 30, 60), 
            "NAME_INPUT": (30, 30, 60),
            "GAME_MENU": (40, 40, 70),
            "INTRO": (20, 40, 60), 
            "INTRO_DETAILS": (20, 40, 60),
            "MAJAPAHIT_MARKET": (139, 115, 85), 
            "MAJAPAHIT_MERCHANT_TALK_ENVOY": (139, 115, 85), 
            "MAJAPAHIT_MERCHANT_TALK_GAJAHMADA": (139, 115, 85), 
            "MAJAPAHIT_MERCHANT_TALK_STRANGE": (139, 115, 85),
            "MAJAPAHIT_PALACE_LIBRARY": (101, 67, 33), 
            "MAJAPAHIT_LINGSAR_TEMPLE": (112, 128, 144), 
            "MAJAPAHIT_OATH_SECURED": (255, 223, 186), 
            "MAJAPAHIT_END_ERA": (50, 50, 80),
            "COLONIAL_ERA_INTRO_PLACEHOLDER": (70,80,90), 
            "INVENTORY_VIEW": (50, 50, 70),
            "DEFAULT": BLACK
        }
        
        self.setup_state() 

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60) 
        pygame.quit()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.name_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_text:
                        self.player = Player(self.input_text.strip())
                        self.name_input_active = False
                        self.change_state("INTRO")
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if len(self.input_text) < 20: 
                         self.input_text += event.unicode
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    for i, button in enumerate(self.current_options_buttons):
                        if button.check_click(mouse_pos):
                            self.process_choice(i, button.action_tag) 
                            break 
            
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_i and self.game_state not in ["START_MENU", "NAME_INPUT", "GAME_MENU"]:
                    if self.game_state != "INVENTORY_VIEW" and self.player:
                        self.previous_game_state = self.game_state 
                        self.change_state("INVENTORY_VIEW")
                    elif self.game_state == "INVENTORY_VIEW":
                        if self.previous_game_state: 
                            self.change_state(self.previous_game_state)
                elif event.key == pygame.K_m and self.game_state not in ["START_MENU", "NAME_INPUT", "GAME_MENU"]:
                     if self.player: 
                        self.previous_game_state = self.game_state
                        self.change_state("GAME_MENU")
                elif event.key == pygame.K_ESCAPE and self.game_state == "GAME_MENU": 
                    if self.previous_game_state:
                        self.change_state(self.previous_game_state)


        for button in self.current_options_buttons:
            button.check_hover(mouse_pos)

    def update(self):
        pass

    def draw(self):
        bg_color = self.background_colors.get(self.game_state, self.background_colors["DEFAULT"])
        self.screen.fill(bg_color)

        if self.game_state == "START_MENU":
            self.draw_title_screen("Nusantara Mission")
        elif self.game_state == "NAME_INPUT":
            self.draw_name_input_screen()
        elif self.game_state == "INVENTORY_VIEW":
            self.draw_inventory_screen()
        elif self.game_state == "GAME_MENU":
            self.draw_game_menu_screen()
        else: 
            if self.current_era_title:
                era_title_surf = self.era_title_font.render(self.current_era_title, True, ERA_TITLE_COLOR)
                era_title_rect = era_title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y= TEXT_BOX_RECT.top - self.era_title_font.get_height() - 20) 
                self.screen.blit(era_title_surf, era_title_rect)

            pygame.draw.rect(self.screen, TEXT_BOX_COLOR, TEXT_BOX_RECT, 0, 15) 
            pygame.draw.rect(self.screen, TEXT_BOX_BORDER_COLOR, TEXT_BOX_RECT, 3, 15) 
           
            render_text_wrapped(self.screen, self.current_narrative_text, self.base_font, NARRATIVE_TEXT_COLOR, NARRATIVE_AREA_RECT, line_spacing_modifier=1.1)

            for button in self.current_options_buttons:
                button.draw(self.screen)
            
            if self.event_messages:
                msg_y = TEXT_BOX_RECT.top - 28 * len(self.event_messages) - 15 
                for msg_index, msg in enumerate(self.event_messages):
                    msg_bg_rect = pygame.Rect(0,0,0,0) 
                    temp_surf = self.option_font.render(msg, True, EVENT_MSG_COLOR)
                    msg_bg_rect.size = (temp_surf.get_width() + 20, temp_surf.get_height() + 10)
                    msg_bg_rect.centerx = SCREEN_WIDTH // 2
                    msg_bg_rect.y = msg_y + (msg_index * 28)
                    
                    pygame.draw.rect(self.screen, DARK_GREY, msg_bg_rect, 0, 5) 
                    msg_surf = self.option_font.render(msg, True, EVENT_MSG_COLOR) 
                    msg_rect = msg_surf.get_rect(center=msg_bg_rect.center)
                    self.screen.blit(msg_surf, msg_rect)


        pygame.display.flip()

    def draw_title_screen(self, title):
        title_surf = self.title_font.render(title, True, TITLE_TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 30))
        self.screen.blit(title_surf, title_rect)

        subtitle_surf = self.option_font.render("A Pygame Text Adventure", True, GREY)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, title_rect.bottom + 20))
        self.screen.blit(subtitle_surf, subtitle_rect)

        for button in self.current_options_buttons:
            button.draw(self.screen)
            
    def draw_name_input_screen(self):
        prompt_surf = self.base_font.render("Enter your hero's name:", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(prompt_surf, prompt_rect)

        input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 20, 360, 50)
        pygame.draw.rect(self.screen, LIGHT_GREY, input_box_rect, 0, 8)
        pygame.draw.rect(self.screen, WHITE, input_box_rect, 2, 8)

        text_surf = self.base_font.render(self.input_text, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(input_box_rect.left + 15, input_box_rect.centery))
        self.screen.blit(text_surf, text_rect)
        
        if time.time() % 1 > 0.5 and self.name_input_active:
            cursor_x = text_rect.right + 5 if self.input_text else input_box_rect.left + 15
            cursor_rect = pygame.Rect(cursor_x, input_box_rect.top + 10, 3, input_box_rect.height - 20)
            pygame.draw.rect(self.screen, DARK_GREY, cursor_rect)

        instr_surf = self.option_font.render("Press ENTER to continue", True, GREY)
        instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(instr_surf, instr_rect)

    def draw_inventory_screen(self):
        title_surf = self.title_font.render("Inventory", True, TITLE_TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)

        items = self.player.get_inventory_display()
        item_y = title_rect.bottom + 40
        for item_text in items:
            item_surf = self.base_font.render(item_text, True, WHITE)
            item_rect = item_surf.get_rect(x=100, y=item_y) 
            self.screen.blit(item_surf, item_rect)
            item_y += self.base_font.get_height() + 10
        
        for button in self.current_options_buttons: 
            button.draw(self.screen)
        
        instr_surf = self.option_font.render("Press 'I' to close or ESC from Game Menu", True, GREY)
        instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(instr_surf, instr_rect)
        
    def draw_game_menu_screen(self):
        title_surf = self.title_font.render("Game Menu", True, TITLE_TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        for button in self.current_options_buttons:
            button.draw(self.screen)
        
        instr_surf = self.option_font.render("Press 'M' or ESC to return to game", True, GREY)
        instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(instr_surf, instr_rect)


    def add_event_message(self, message):
        self.event_messages.append(message)

    def clear_event_messages(self):
        self.event_messages = []

    def change_state(self, new_state):
        print(f"Changing state from {self.game_state} to {new_state}") 
        self.game_state = new_state
        self.clear_event_messages() 
        self.setup_state() 

    def setup_state(self):
        self.current_options_buttons = [] 
        button_width_narrative = TEXT_BOX_RECT.width - 60 
        button_height_narrative = BUTTON_HEIGHT
        button_x_narrative = TEXT_BOX_RECT.left + (TEXT_BOX_RECT.width - button_width_narrative) // 2
        
        button_width_menu = 300
        button_height_menu = 50
        button_x_menu = SCREEN_WIDTH // 2 - button_width_menu // 2
        menu_start_y = SCREEN_HEIGHT // 2 - 100
        menu_spacing = 70

        self.current_era_title = "" 

        if self.game_state == "START_MENU":
            self.current_narrative_text = "" 
            self.current_options_buttons = [
                Button(button_x_menu, menu_start_y, button_width_menu, button_height_menu, "Start New Game", self.menu_font, border_radius=10, action_tag="START_NEW_GAME"),
                Button(button_x_menu, menu_start_y + menu_spacing, button_width_menu, button_height_menu, "Load Game", self.menu_font, border_radius=10, action_tag="LOAD_GAME"),
                Button(button_x_menu, menu_start_y + menu_spacing * 2, button_width_menu, button_height_menu, "Exit", self.menu_font, border_radius=10, action_tag="EXIT_GAME"),
            ]
        elif self.game_state == "NAME_INPUT":
            self.current_narrative_text = ""
            self.input_text = ""
            self.name_input_active = True
        
        elif self.game_state == "GAME_MENU":
            self.current_narrative_text = ""
            self.current_era_title = "Game Paused"
            self.current_options_buttons = [
                Button(button_x_menu, menu_start_y - menu_spacing, button_width_menu, button_height_menu, "Continue Game", self.menu_font, action_tag="CONTINUE_GAME"),
                Button(button_x_menu, menu_start_y, button_width_menu, button_height_menu, "Save Game", self.menu_font, action_tag="SAVE_GAME"),
                Button(button_x_menu, menu_start_y + menu_spacing, button_width_menu, button_height_menu, "Load Game", self.menu_font, action_tag="LOAD_GAME_MENU"),
                Button(button_x_menu, menu_start_y + menu_spacing*2, button_width_menu, button_height_menu, "Inventory", self.menu_font, action_tag="OPEN_INVENTORY_MENU"),
                Button(button_x_menu, menu_start_y + menu_spacing*3, button_width_menu, button_height_menu, "Exit to Main Menu", self.menu_font, action_tag="EXIT_TO_MAIN_MENU"),
            ]

        elif self.game_state == "INTRO":
            self.current_era_title = "The Beginning: Year 2150"
            self.current_narrative_text = (f"Professor Wijaya: \"{self.player.name}, you are our last hope. This time machine will take you "
                                           f"to various important eras in Indonesian history.\n\n"
                                           f"Your duty is to ensure history stays on its intended path.\"")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Ask for more details.", self.option_font),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Ready to go to Majapahit!", self.option_font),
            ]
        
        elif self.game_state == "INTRO_DETAILS":
            self.current_era_title = "The Mission Briefing"
            self.current_narrative_text = ("Professor Wijaya: \"The Time Corruptors want to change Indonesian history "
                                           "so that our nation never unites. They have sent agents "
                                           "to various important eras to alter key events.\n\n"
                                           "Your task is to find these agents, thwart their plans, "
                                           "and ensure history remains on track.\"")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Understood. Let's go!", self.option_font),
            ]

        elif self.game_state == "MAJAPAHIT_MARKET":
            self.current_era_title = "Majapahit Kingdom - Year 1350: The Market"
            self.current_narrative_text = ("You arrive in a bustling market. The air is filled with the scent of spices.\n\n"
                                           "MISSION: Ensure Gajah Mada still utters the Palapa Oath.\n\n"
                                           "An old merchant approaches you: \"You're not from around here, young one. Your clothes are strange.\"")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Say you are an envoy.", self.option_font, action_tag="MAJAPAHIT_ENVOY"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Ask about Gajah Mada.", self.option_font, action_tag="MAJAPAHIT_ASK_GM"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * 2, button_width_narrative, button_height_narrative, "Inquire about strange occurrences.", self.option_font, action_tag="MAJAPAHIT_STRANGE"),
            ]
        
        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_ENVOY": 
            self.current_era_title = "Majapahit: Talking to Merchant"
            self.current_narrative_text = ("You: \"I am an envoy from a distant kingdom...\"\n\n"
                                           "Merchant: \"Hmm, suspicious... Go to the palace. Security is tight.\"\n\n"
                                           "The merchant gives you a batik cloth.")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Go to the Palace (WIP)", self.option_font, action_tag="GO_PALACE_WIP"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Return to Market Square", self.option_font, action_tag="RETURN_MARKET_SQUARE"),
            ]

        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_GAJAHMADA":
            self.current_era_title = "Majapahit: Talking to Merchant"
            self.current_narrative_text = ("You: \"I wish to know about Gajah Mada...\"\n\n"
                                           "Merchant: \"Gajah Mada? He is in great trouble. "
                                           "Someone has poisoned his mind... He is at Lingsar Temple.\"")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Go to Lingsar Temple", self.option_font, action_tag="GO_LINGSAR_TEMPLE"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Ask more (WIP)", self.option_font, action_tag="ASK_MORE_POISON_WIP"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * 2, button_width_narrative, button_height_narrative, "Return to Market Square", self.option_font, action_tag="RETURN_MARKET_SQUARE"),
            ]

        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_STRANGE":
            self.current_era_title = "Majapahit: Talking to Merchant"
            self.current_narrative_text = ("You: \"Have there been any strange occurrences lately?\"\n\n"
                                           "Merchant: \"Indeed! A strangely dressed foreigner arrived... "
                                           "Mahapatih doubts his plan to unite Nusantara. Seek Empu Tantular...\"")
            self.current_options_buttons = [
                Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Go to the Palace Library", self.option_font, action_tag="GO_PALACE_LIBRARY"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Ask about the foreigner (WIP)", self.option_font, action_tag="ASK_FOREIGNER_WIP"),
                Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * 2, button_width_narrative, button_height_narrative, "Return to Market Square", self.option_font, action_tag="RETURN_MARKET_SQUARE"),
            ]
        
        elif self.game_state == "MAJAPAHIT_PALACE_LIBRARY":
            self.current_era_title = "Majapahit: Palace Library"
            if not self.player.choices.get("met_empu_tantular"):
                self.current_narrative_text = ("You find Empu Tantular amidst scrolls and books.\n\n"
                                               "Empu Tantular: \"Greetings, traveler. Your attire is unusual. What brings you to this sanctuary of knowledge?\"")
                self.current_options_buttons = [
                    Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Discuss the foreigner.", self.option_font, action_tag="DISCUSS_FOREIGNER_ET"),
                    Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING, button_width_narrative, button_height_narrative, "Ask about Gajah Mada's doubt.", self.option_font, action_tag="ASK_GM_DOUBT_ET"),
                ]
            else: 
                 self.current_narrative_text = "Empu Tantular nods thoughtfully. The weight of the situation is clear on his face."
                 self.current_options_buttons = [
                    Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Leave the Library", self.option_font, action_tag="LEAVE_LIBRARY"),
                 ]


        elif self.game_state == "MAJAPAHIT_LINGSAR_TEMPLE":
            self.current_era_title = "Majapahit: Lingsar Temple"
            self.current_narrative_text = ("The air at Lingsar Temple is serene, yet a palpable tension surrounds Gajah Mada, who is in deep meditation. "
                                           "A shadowy figure in unusual garb lurks nearby, pretending to be an attendant.")
            
            options_at_temple = []
            # Logic to show "Approach Gajah Mada" only if conditions are met or it's a general option
            options_at_temple.append(Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * len(options_at_temple), button_width_narrative, button_height_narrative, "Approach Gajah Mada directly.", self.option_font, action_tag="APPROACH_GM"))
            
            if not self.player.choices.get("corruptor_fled_lingsar"): 
                options_at_temple.append(Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * len(options_at_temple), button_width_narrative, button_height_narrative, "Confront the shadowy figure.", self.option_font, action_tag="CONFRONT_FIGURE"))
            
            options_at_temple.append(Button(button_x_narrative, OPTIONS_START_Y + OPTION_SPACING * len(options_at_temple), button_width_narrative, button_height_narrative, "Return to market for more info.", self.option_font, action_tag="RETURN_MARKET_FROM_TEMPLE"))
            self.current_options_buttons = options_at_temple
            
        elif self.game_state == "MAJAPAHIT_OATH_SECURED":
            self.current_era_title = "Majapahit: Mission Accomplished!"
            self.current_narrative_text = ("Through your efforts, Gajah Mada's resolve is restored! " 
                                           "He confidently prepares to declare the Palapa Oath, ensuring the unity of Nusantara.\n\n"
                                           "The Time Corruptor's plan has failed here!\n\n"
                                           "A shimmering fragment materializes before you.")
            if self.player and "Palapa Keystone Fragment" not in self.player.inventory: 
                self.player.add_item("Palapa Keystone Fragment", self)
            self.current_options_buttons = [
                 Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Prepare for next era", self.option_font, action_tag="END_MAJAPAHIT_ERA"),
            ]

        elif self.game_state == "MAJAPAHIT_END_ERA":
            self.current_era_title = "Chronometer Activated"
            self.current_narrative_text = "Your Time Chronometer glows, indicating the timeline is stable. New coordinates are locked for the Colonial Era."
            self.current_options_buttons = [
                 Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "Travel to Colonial Era", self.option_font, action_tag="GOTO_COLONIAL"),
            ]
            
        elif self.game_state == "COLONIAL_ERA_INTRO_PLACEHOLDER":
            self.current_era_title = "Dutch Colonial Era - Batavia (WIP)"
            self.current_narrative_text = "You arrive in Batavia, 1830. The air is thick with humidity and the scent of spices and sea salt. Dutch colonial power is at its height. (Story to be continued...)"
            self.current_options_buttons = [
                 Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, button_height_narrative, "End Game Demo", self.option_font, action_tag="END_DEMO"),
            ]


        elif self.game_state == "INVENTORY_VIEW":
            self.current_narrative_text = "" 
            self.current_options_buttons = [] 


    def process_choice(self, index, action_tag):
        print(f"State: {self.game_state}, Action Tag: {action_tag}") 
        self.clear_event_messages() 
        
        button_width_narrative = TEXT_BOX_RECT.width - 60 
        button_x_narrative = TEXT_BOX_RECT.left + (TEXT_BOX_RECT.width - button_width_narrative) // 2

        if self.game_state == "START_MENU":
            if action_tag == "START_NEW_GAME":
                self.change_state("NAME_INPUT")
            elif action_tag == "EXIT_GAME":
                self.running = False
            elif action_tag == "LOAD_GAME":
                self.load_game_data_pygame()


        elif self.game_state == "GAME_MENU":
            if action_tag == "CONTINUE_GAME":
                if self.previous_game_state:
                    self.change_state(self.previous_game_state)
            elif action_tag == "SAVE_GAME":
                self.save_game_data_pygame()
            elif action_tag == "LOAD_GAME_MENU":
                self.load_game_data_pygame()
            elif action_tag == "OPEN_INVENTORY_MENU":
                self.state_before_inventory_from_menu = self.previous_game_state 
                self.previous_game_state = self.game_state 
                self.change_state("INVENTORY_VIEW")
            elif action_tag == "EXIT_TO_MAIN_MENU":
                self.player = None 
                self.change_state("START_MENU")


        elif self.game_state == "INTRO":
            if action_tag == "Ask for more details.":
                self.change_state("INTRO_DETAILS")
            elif action_tag == "Ready to go to Majapahit!":
                self.change_state("MAJAPAHIT_MARKET")
        
        elif self.game_state == "INTRO_DETAILS":
            if action_tag == "Understood. Let's go!":
                self.change_state("MAJAPAHIT_MARKET")

        elif self.game_state == "MAJAPAHIT_MARKET":
            if action_tag == "MAJAPAHIT_ENVOY":
                if self.player: self.player.add_item("Majapahit Batik Cloth", self) 
                self.change_state("MAJAPAHIT_MERCHANT_TALK_ENVOY") 
            elif action_tag == "MAJAPAHIT_ASK_GM":
                self.change_state("MAJAPAHIT_MERCHANT_TALK_GAJAHMADA")
            elif action_tag == "MAJAPAHIT_STRANGE":
                self.change_state("MAJAPAHIT_MERCHANT_TALK_STRANGE")
        
        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_ENVOY":
            if action_tag == "GO_PALACE_WIP":
                self.current_narrative_text = "You decide to head to the palace. The guards are stern, but the batik cloth seems to grant you some passage. (Palace interactions WIP)"
                self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "Return to Market Square", self.option_font, action_tag="RETURN_MARKET_SQUARE")]
            elif action_tag == "EXPLORE_MARKET_AGAIN" or action_tag == "RETURN_MARKET_SQUARE": 
                self.change_state("MAJAPAHIT_MARKET")
        
        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_GAJAHMADA":
            if action_tag == "GO_LINGSAR_TEMPLE":
                self.change_state("MAJAPAHIT_LINGSAR_TEMPLE")
            elif action_tag == "ASK_MORE_POISON_WIP":
                self.current_narrative_text = "Merchant: \"The details are murky, whispers in the wind... but his spirit seems clouded. Some say a foreign advisor has his ear.\" (WIP)"
                self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "Go to Lingsar Temple", self.option_font, action_tag="GO_LINGSAR_TEMPLE")]
            elif action_tag == "RETURN_MARKET_SQUARE": 
                self.change_state("MAJAPAHIT_MARKET")


        elif self.game_state == "MAJAPAHIT_MERCHANT_TALK_STRANGE":
            if action_tag == "GO_PALACE_LIBRARY":
                self.change_state("MAJAPAHIT_PALACE_LIBRARY")
            elif action_tag == "ASK_FOREIGNER_WIP":
                self.current_narrative_text = "Merchant: \"He spoke with a strange accent, and his clothes... not of any land I know. He vanished as quickly as he came after speaking to some officials.\" (WIP)"
                self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "Go to Palace Library", self.option_font, action_tag="GO_PALACE_LIBRARY")]
            elif action_tag == "RETURN_MARKET_SQUARE": 
                self.change_state("MAJAPAHIT_MARKET")
        
        elif self.game_state == "MAJAPAHIT_PALACE_LIBRARY":
            if not self.player.choices.get("met_empu_tantular"): 
                self.player.choices["met_empu_tantular"] = True 
            
            if action_tag == "DISCUSS_FOREIGNER_ET":
                self.current_narrative_text = ("Empu Tantular: \"Indeed, a strange individual. He sought to subtly spread doubt about the Mahapatih's Sumpah Palapa, "
                                               "claiming it would bring ruin rather than unity. I believe he left this...\" He hands you a strangely smooth, dark stone.")
                if self.player: self.player.add_item("Odd Dark Stone", self)
                self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "Ask about Gajah Mada's doubt.", self.option_font, action_tag="ASK_GM_DOUBT_ET_AGAIN")]
            elif action_tag == "ASK_GM_DOUBT_ET" or action_tag == "ASK_GM_DOUBT_ET_AGAIN":
                self.current_narrative_text = ("Empu Tantular: \"The Mahapatih is strong, but words of doubt, especially if repeated by trusted advisors influenced by this foreigner, "
                                               "can erode even the firmest resolve. The Sumpah Palapa is a monumental vow. The corruptor aims to make him falter before he speaks it publicly.\n"
                                               "Perhaps showing him proof of external manipulation could restore his conviction. You must act quickly!\"")
                if self.player: self.player.add_item("Empu Tantular's Counsel", self) 
                self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "Thank Empu Tantular and leave.", self.option_font, action_tag="LEAVE_LIBRARY")]
            elif action_tag == "LEAVE_LIBRARY":
                self.change_state("MAJAPAHIT_MARKET") 

        elif self.game_state == "MAJAPAHIT_LINGSAR_TEMPLE":
            if action_tag == "APPROACH_GM":
                if self.player.has_item("Odd Dark Stone") and self.player.has_item("Empu Tantular's Counsel"):
                    self.current_narrative_text = ("You approach Gajah Mada. He seems troubled. You present the evidence of the Time Corruptor's manipulation "
                                                   "(the Dark Stone) and share Empu Tantular's wisdom. Slowly, clarity returns to his eyes.")
                    self.player.choices["convinced_gajah_mada"] = True
                    self.current_options_buttons = [Button(button_x_narrative, OPTIONS_START_Y, button_width_narrative, BUTTON_HEIGHT, "The timeline feels more stable.", self.option_font, action_tag="CHECK_OATH_STATUS")]
                else:
                    self.current_narrative_text = "You approach Gajah Mada, but he is lost in thought... You feel you lack the means to help him now. You need more evidence or insight."
                    # Re-present temple options without changing state yet, so player can try another option from the temple
                    self.setup_state() 
                    return # Important: Return to avoid further processing in this process_choice call

            elif action_tag == "CONFRONT_FIGURE":
                if not self.player.choices.get("corruptor_fled_lingsar"): 
                    self.current_narrative_text = ("You confront the shadowy figure. It snarls, revealing a futuristic device before vanishing in a flash of distorted light! "
                                                   "It seems this was the Time Corruptor. You have scared them off for now.")
                    self.player.choices["corruptor_fled_lingsar"] = True
                else:
                    self.current_narrative_text = "The shadowy figure is already gone."
                # Re-present temple options after this action
                self.setup_state() 
                return

            elif action_tag == "RETURN_MARKET_FROM_TEMPLE":
                self.change_state("MAJAPAHIT_MARKET")
            
            elif action_tag == "CHECK_OATH_STATUS": 
                if self.player.choices.get("convinced_gajah_mada"):
                    self.change_state("MAJAPAHIT_OATH_SECURED")
                else: # Should not happen if logic is correct, but as a fallback
                    self.current_narrative_text = "Gajah Mada still seems troubled. The Time Corruptor's influence might linger or you haven't found the right way to help."
                    self.setup_state() # Re-present temple options
                    return


        elif self.game_state == "MAJAPAHIT_OATH_SECURED":
            if action_tag == "END_MAJAPAHIT_ERA":
                if self.player: self.player.completed_eras.append("Majapahit")
                self.change_state("MAJAPAHIT_END_ERA")

        elif self.game_state == "MAJAPAHIT_END_ERA":
            if action_tag == "GOTO_COLONIAL":
                self.change_state("COLONIAL_ERA_INTRO_PLACEHOLDER")
        
        elif self.game_state == "COLONIAL_ERA_INTRO_PLACEHOLDER":
            if action_tag == "END_DEMO":
                self.running = False 

        # Fallback: if after processing a choice, no new buttons were set for the *current* state
        # (and it's not a menu/input state), then something might be missing in the logic for that state.
        # This is a bit broad, ideally each state transition or action result explicitly sets next options.
        if not self.current_options_buttons and self.game_state not in ["START_MENU", "NAME_INPUT", "INVENTORY_VIEW", "GAME_MENU"]:
             if self.game_state.startswith("MAJAPAHIT_MERCHANT_TALK"):
                 self.add_event_message("You decide to return to the market square.")
                 self.change_state("MAJAPAHIT_MARKET")


    def save_game_data_pygame(self):
        if not self.player:
            self.add_event_message("No game to save!")
            return
        
        save_data = {
            "player_data": self.player.to_dict(),
            "current_game_state": self.game_state,
            "current_era_title": self.current_era_title,
            "previous_game_state": self.previous_game_state, 
            "player_choices_log": self.player.choices 
        }
        try:
            with open(SAVE_FILE_NAME, 'w') as f:
                json.dump(save_data, f, indent=4)
            self.add_event_message("Game progress saved!")
        except Exception as e:
            print(f"Error saving game: {e}")
            self.add_event_message("Error saving game.")

    def load_game_data_pygame(self):
        if not os.path.exists(SAVE_FILE_NAME):
            self.add_event_message("No save file found!")
            if self.game_state == "GAME_MENU" or self.game_state == "START_MENU": 
                 self.setup_state() 
            return

        try:
            with open(SAVE_FILE_NAME, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player.from_dict(save_data["player_data"])
            loaded_game_state = save_data["current_game_state"]
            self.current_era_title = save_data.get("current_era_title", "") 
            self.previous_game_state = save_data.get("previous_game_state", None)
            self.player.choices = save_data.get("player_choices_log", {}) 
            
            self.change_state(loaded_game_state) 
            self.add_event_message("Game loaded successfully!")

        except Exception as e:
            print(f"Error loading game: {e}")
            self.add_event_message(f"Error loading game data: {e}")
            if self.game_state == "GAME_MENU" or self.game_state == "START_MENU": 
                 self.setup_state()


# --- Main Execution ---
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()

