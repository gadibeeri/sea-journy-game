import pygame
import math
import os
import random
import time
from pygame import gfxdraw
import sys
from pygame import mixer
from pathlib import Path
import asyncio

# Basic settings
WIDTH, HEIGHT = 900, 700  # Smaller window size
ROWS, COLS = 9, 9
HEX_SIZE = 35  # Slightly smaller hexagons to fit in new window size
BOARD_WIDTH = COLS * HEX_SIZE * math.sqrt(3)  # Calculate total board width
BOARD_HEIGHT = ROWS * HEX_SIZE * 1.5  # Calculate total board height
BOARD_OFFSET_X = (WIDTH - BOARD_WIDTH) // 2 + 100  # Move board right to make space for card stacks
BOARD_OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2  # Center vertically

# Enhanced colors
BLUE = (0, 105, 148)  # Sea blue color for hexagons
DARK_BLUE = (0, 75, 118)  # Darker blue for depth
LIGHT_BLUE = (173, 216, 230)  # Light blue
WAVE_BLUE = (64, 164, 223)  # Wave color
WAVE_HIGHLIGHT = (128, 208, 255)  # Wave highlight color
LIGHT_GREEN = (144, 238, 144)  # Light green for board background
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)  # Crimson red
GOLD = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0, 100)  # Semi-transparent black
BG_COLOR = (240, 248, 255)  # Light blue background

# Animation settings
WAVE_SPEED = 0.02
WAVE_AMPLITUDE = 5
BOAT_ROCK_AMPLITUDE = 3
BOAT_ROCK_SPEED = 0.05
CARD_SPEED = 10

# Game states
GAME_STATE_MENU = 'menu'
GAME_STATE_PLAYING = 'playing'
GAME_STATE_WINNER = 'winner'  # New game state for when someone wins
GAME_STATE_BATTLE = 'battle'

# Card symbols and states
CARD_SYMBOLS = ['wheel', 'sea currents', 'fishing rode', 'passangers of the boat', 'the holes', 
                'waves', 'light house', 'compass', 'stars', 'other boats', 'diver', 
                'clouds and weather', 'anchor', 'telescope', 'bell', 'sea storm', 'pirats', 'main sail']  # Reflection card symbols
COPING_SYMBOLS = ['stormy clouds', 'tornedo', 'black clouds', 'mutiny', 'stack on the rocks',
                 'sea battle', 'counter winds', 'horricane', 'bombs away', 'no wind',
                 'turbulance', 'mermaids', 'wheel broken', 'changing rout']  # Coping card symbols
CARD_WIDTH = 200  # Standard card width
CARD_HEIGHT = 300  # Standard card height
LARGE_CARD_SIZE = 300  # Smaller centered card size
CARD_FONT_SIZE = 24  # Smaller font size
INSTRUCTION_FONT_SIZE = 18  # Smaller instruction font

# Add these variables after the other global variables
wave_offset = 0
boat1_offset = {'x': 0, 'y': 0, 'angle': 0}
boat2_offset = {'x': 0, 'y': 0, 'angle': 0}
animation_time = 0

# Enhanced colors for treasure map theme
PARCHMENT_COLOR = (255, 248, 220)  # Antique white
SEA_BLUE = (0, 105, 148)  # Darker blue
DEEP_BLUE = (0, 51, 102)  # Even darker blue for depth
WAVE_COLOR = (64, 164, 223)  # Brighter blue for waves
COMPASS_GOLD = (218, 165, 32)  # Golden rod
MAP_BORDER = (139, 69, 19)  # Saddle brown
AGED_BLACK = (48, 48, 48)  # Softer than pure black

# Add new colors for enhanced visuals
GRID_LINE_COLOR = (0, 0, 0, 30)  # Semi-transparent black for grid lines
HEX_HIGHLIGHT = (255, 255, 255, 50)  # Semi-transparent white for highlights
WATER_GRADIENT_START = (0, 105, 148)  # Deep blue
WATER_GRADIENT_END = (64, 164, 223)  # Light blue

# Animation settings
WAVE_COUNT = 3  # Number of wave layers
WAVE_SPEEDS = [0.03, 0.05, 0.07]  # Different speeds for each wave layer
WAVE_AMPLITUDES = [2, 3, 4]  # Different amplitudes for each wave layer
WAVE_FREQUENCIES = [4, 6, 8]  # Different frequencies for each wave layer

# Add these colors after the other color definitions
CLOSE_BUTTON_COLOR = (220, 53, 69)  # Red color for close button
CLOSE_BUTTON_HOVER = (241, 82, 97)  # Lighter red for hover effect

# Card display settings
CARD_STACK_WIDTH = 120  # Smaller card stack width
CARD_DISPLAY_HEIGHT = HEIGHT - 80
CARD_STACK_OFFSET = 20  # Smaller spacing between stacked cards

# UI Layout
DICE_SIZE = 60  # Dice size
DICE_MARGIN = 20
INFO_BOX_WIDTH = 120  # Info box width
INFO_BOX_HEIGHT = 100

# Add card limit constants after the CARD_SYMBOLS section
MAX_REFLECTION_CARDS = 6
MAX_COPING_CARDS = 6

# Initialize mixer
print("\nInitializing sound system...")
try:
    mixer.init()
    print("Pygame mixer initialized successfully")
except Exception as e:
    print(f"Failed to initialize mixer: {e}")

# Function to load sound with error checking
def load_sound(filename):
    """Load a sound file with error checking"""
    try:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds', filename)
        print(f"Attempting to load sound: {filepath}")
        if not os.path.exists(filepath):
            print(f"Sound file not found: {filepath}")
            return None
        sound = mixer.Sound(filepath)
        print(f"Successfully loaded sound: {filename}")
        return sound
    except Exception as e:
        print(f"Error loading sound {filename}: {e}")
        return None

# Load sound effects with better error handling
print("\nLoading sound effects...")
background_music = load_sound('sea_waves.wav')
dice_roll_sound = load_sound('dice_roll.wav')
card_flip_sound = load_sound('card_flip.wav')
collect_card_sound = load_sound('collect_card.wav')
boat_move_sound = load_sound('boat_move.wav')
boat_sand_sound = load_sound('boat_sand.wav')
monster_sound = load_sound('monster.wav')
victory_sound = load_sound('victory.wav')

# Set sound volumes if sounds loaded successfully
if background_music:
    background_music.set_volume(0.3)
if dice_roll_sound:
    dice_roll_sound.set_volume(0.4)
if card_flip_sound:
    card_flip_sound.set_volume(0.4)
if collect_card_sound:
    collect_card_sound.set_volume(0.4)
if boat_move_sound:
    boat_move_sound.set_volume(0.3)
if boat_sand_sound:
    boat_sand_sound.set_volume(0.5)
if monster_sound:
    monster_sound.set_volume(0.4)
if victory_sound:
    victory_sound.set_volume(0.6)

def play_sound(sound):
    """Helper function to play sound effects safely with debug message"""
    if sound is not None:
        try:
            sound.play()
            return True
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False
    return False

def toggle_music():
    """Toggle background music on/off with debug message"""
    global background_music
    if background_music is not None:
        try:
            if mixer.get_busy():
                print("Stopping background music")
                background_music.stop()
            else:
                print("Starting background music")
                background_music.play(-1)
        except Exception as e:
            print(f"Error toggling music: {e}")

# Test sound system at startup
print("\nTesting sound system...")
if background_music:
    success = play_sound(background_music)
    print(f"Background music test: {'Success' if success else 'Failed'}")
else:
    print("Background music not loaded, please check the assets/sounds directory")

def get_hex_center(row, col):
    """Get the center coordinates of a hexagon given its grid position"""
    x = col * HEX_SIZE * math.sqrt(3) + BOARD_OFFSET_X
    y = row * HEX_SIZE * 1.5 + BOARD_OFFSET_Y
    if row % 2 == 1:
        x += HEX_SIZE * math.sqrt(3) / 2
    return x, y

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sea Journey - Reflection Game")

# Load custom fonts
try:
    title_font = pygame.font.Font('assets/fonts/PlayfairDisplay-Bold.ttf', 48)
    game_font = pygame.font.Font('assets/fonts/Roboto-Regular.ttf', 32)
    card_font = pygame.font.Font('assets/fonts/PlayfairDisplay-Regular.ttf', CARD_FONT_SIZE)
    instruction_font = pygame.font.Font('assets/fonts/Roboto-Regular.ttf', INSTRUCTION_FONT_SIZE)
except:
    print("Custom fonts not found, using system fonts")
    title_font = pygame.font.SysFont('arial', 48)
    game_font = pygame.font.SysFont('arial', 32)
    card_font = pygame.font.SysFont('arial', CARD_FONT_SIZE)
    instruction_font = pygame.font.SysFont('arial', INSTRUCTION_FONT_SIZE)

# Load and scale boat image
try:
    print("Attempting to load boat image...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'assets', 'boat.png')
    print(f"Looking for image at: {image_path}")
    boat_image = pygame.image.load(image_path)
    boat_size = int(HEX_SIZE * 0.8)  # Scale boat relative to new hexagon size
    boat_image = pygame.transform.scale(boat_image, (boat_size, boat_size))
    print("Boat image loaded successfully")
except Exception as e:
    print(f"Error loading boat image: {e}")
    print("Make sure 'boat.png' is in the 'assets' folder")
    boat_size = int(HEX_SIZE * 0.8)  # Scale boat relative to new hexagon size
    boat_image = pygame.Surface((boat_size, boat_size))
    boat_image.fill((255, 0, 0))

# Load and scale island image
try:
    print("Attempting to load island image...")
    island_path = os.path.join(current_dir, 'assets', 'island.png')
    print(f"Looking for image at: {island_path}")
    island_image = pygame.image.load(island_path)
    island_size = int(HEX_SIZE * 0.8)  # Scale island relative to new hexagon size
    island_image = pygame.transform.scale(island_image, (island_size, island_size))
    print("Island image loaded successfully")
except Exception as e:
    print(f"Error loading island image: {e}")
    print("Make sure 'island.png' is in the 'assets' folder")
    island_size = int(HEX_SIZE * 0.8)  # Scale island relative to new hexagon size
    island_image = pygame.Surface((island_size, island_size))
    island_image.fill((0, 255, 0))

# Load and scale octopus image
try:
    print("Attempting to load octopus image...")
    octopus_path = os.path.join(current_dir, 'assets', 'octopus.png')
    print(f"Looking for image at: {octopus_path}")
    octopus_image = pygame.image.load(octopus_path)
    octopus_size = int(HEX_SIZE * 0.7)  # Scale octopus relative to new hexagon size
    octopus_image = pygame.transform.scale(octopus_image, (octopus_size, octopus_size))
    print("Octopus image loaded successfully")
except Exception as e:
    print(f"Error loading octopus image: {e}")
    print("Make sure 'octopus.png' is in the 'assets' folder")
    octopus_size = int(HEX_SIZE * 0.7)  # Scale octopus relative to new hexagon size
    octopus_image = pygame.Surface((octopus_size, octopus_size))
    octopus_image.fill((128, 0, 128))

# Load and scale second boat image
try:
    print("Attempting to load boat2 image...")
    boat2_path = os.path.join(current_dir, 'assets', 'boat2.png')
    print(f"Looking for image at: {boat2_path}")
    boat2_image = pygame.image.load(boat2_path)
    boat2_image = pygame.transform.scale(boat2_image, (boat_size, boat_size))
    print("Boat2 image loaded successfully")
except Exception as e:
    print(f"Error loading boat2 image: {e}")
    print("Make sure 'boat2.png' is in the 'assets' folder")
    boat2_image = pygame.Surface((boat_size, boat_size))
    boat2_image.fill((0, 0, 255))  # Blue placeholder for second boat

# After the other image loading sections, add this code to load sign images
try:
    print("Loading sign images for reflection cards...")
    sign_images = {}
    signs_dir = os.path.join(current_dir, 'assets', 'signs')
    
    # Map each reflection symbol to a sign image
    sign_mapping = {
        'anchor': 'anchor.png',
        'life boat': 'life_boat.png',
        'wheel': 'wheel.png',
        'compass': 'compass.png',
        'main sail': 'main_sail.png'
    }
    
    # Load each sign image
    for symbol, filename in sign_mapping.items():
        try:
            image_path = os.path.join(signs_dir, filename)
            print(f"Loading sign image: {image_path}")
            if os.path.exists(image_path):
                sign_image = pygame.image.load(image_path)
                # Scale image to fit on card (slightly smaller than card width)
                image_size = int(LARGE_CARD_SIZE * 0.7)
                sign_images[symbol] = pygame.transform.scale(sign_image, (image_size, image_size))
                print(f"Successfully loaded sign image for {symbol}")
            else:
                print(f"Sign image file not found: {image_path}")
                # Create a placeholder colored rectangle
                placeholder = pygame.Surface((100, 100))
                placeholder.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                sign_images[symbol] = placeholder
        except Exception as e:
            print(f"Error loading sign image {filename}: {e}")
            # Create a placeholder colored rectangle
            placeholder = pygame.Surface((100, 100))
            placeholder.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            sign_images[symbol] = placeholder
except Exception as e:
    print(f"Error setting up sign images: {e}")
    sign_images = {}

# Initialize game state
game_state = GAME_STATE_MENU
num_players = 1
current_player = 1
can_roll = True
current_roll = 0
move_delay = 100  # Reduced from 200 to 100 milliseconds
waiting_for_card_interaction = False
centered_card = None
card_display_state = None
current_card_symbol = None
BOATS_MET = False
EXCHANGE_STATE = None
SELECTED_CARD = None

# Player positions and card tracking
player1_pos = {'row': 0, 'col': 0}  # Start at top-left corner
player2_pos = {'row': ROWS - 1, 'col': COLS - 1}  # Start at bottom-right corner
player_card_counts = {
    1: {'reflection': 0, 'coping': 0},
    2: {'reflection': 0, 'coping': 0}
}
collected_cards = {
    1: {'reflection': [], 'coping': []},
    2: {'reflection': [], 'coping': []}
}
animation_cards = []
collected_reflection_cards = []
collected_coping_cards = []

# Generate island and octopus positions
island_positions = []
while len(island_positions) < 10:  # Reduced from 12 to 10 for 9x9 grid
    pos = {'row': random.randint(0, ROWS-1), 'col': random.randint(0, COLS-1)}
    # Don't place islands at player starting positions
    if pos not in island_positions and pos != player1_pos and pos != player2_pos:
        island_positions.append(pos)

octopus_positions = []
while len(octopus_positions) < 10:  # Reduced from 12 to 10 for 9x9 grid
    pos = {'row': random.randint(0, ROWS-1), 'col': random.randint(0, COLS-1)}
    # Don't place octopuses where there are islands, other octopuses, or at player starting positions
    if (pos not in island_positions and pos not in octopus_positions and 
        pos != player1_pos and pos != player2_pos):
        octopus_positions.append(pos)

# Add this new class for card animations
class MovingCard:
    def __init__(self, card_type, start_pos, end_pos):
        self.card_type = card_type
        self.x, self.y = start_pos
        self.end_x, self.end_y = end_pos
        self.size = 70
        self.moving = True
        
    def update(self):
        # Move towards target position
        dx = self.end_x - self.x
        dy = self.end_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < CARD_SPEED:
            self.x = self.end_x
            self.y = self.end_y
            self.moving = False
            return
        
        # Normalize direction and multiply by speed
        dx = dx / distance * CARD_SPEED
        dy = dy / distance * CARD_SPEED
        
        self.x += dx
        self.y += dy

    def draw(self, screen, label_font):
        # Draw card
        card_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        draw_rounded_rect(screen, card_rect, WHITE, 10)
        pygame.draw.rect(screen, BLACK, card_rect, 2, border_radius=10)
        
        # Draw text
        if self.card_type == 'reflection':
            text1 = label_font.render("Self", True, BLACK)
            text2 = label_font.render("Reflection", True, BLACK)
            text1_rect = text1.get_rect(centerx=card_rect.centerx, centery=card_rect.centery - 10)
            text2_rect = text2.get_rect(centerx=card_rect.centerx, centery=card_rect.centery + 10)
            screen.blit(text1, text1_rect)
            screen.blit(text2, text2_rect)
        else:
            text = label_font.render("Coping", True, BLACK)
            text_rect = text.get_rect(center=card_rect.center)
            screen.blit(text, text_rect)

# Add this new class for the centered card display
class CenteredCard:
    def __init__(self, symbol, card_type, size=LARGE_CARD_SIZE):
        self.symbol = symbol
        self.card_type = card_type
        self.width = min(size, WIDTH - 400)  # Ensure card doesn't overflow
        self.height = int(self.width * 1.5)
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGHT - self.height) // 2
        self.state = 'symbol'
        self.rotation = 0
        self.flip_progress = 0
        self.flipping = False
        self.flip_speed = 0.1
    
    def get_instruction_text(self):
        """Get the instruction text based on card type and symbol"""
        if self.card_type == 'reflection':
            instructions = {
                'wheel': "Your choice point, how do you deal with complex situation, do you face them, run, or something else?",
                'sea currents': "Are you noticing your inner world? Stop and notice what is here and now.",
                'fishing rode': "How do you handle your urges? Can you master them and have patience?",
                'passangers of the boat': "Do I know my inner sides, the child, the adult, the critic?",
                'the holes': "Do I know my downfalls, my challenges?",
                'waves': "Do I know my emotions, am I connected to them?",
                'light house': "Do I make short term goals? What helps me to reach them?",
                'compass': "Where do I aim my energy and focus? How do I spend my time?",
                'stars': "What are my values? What are the qualities in me I wish to emphasize?",
                'other boats': "How do I communicate with others? Can I listen? Forgive? Ask for help? Trust?",
                'diver': "Do I avoid any feelings or sense of discomfort? For what reason?",
                'clouds and weather': "How do you deal with your thoughts? How do you organize which is valuable and which to ignore?",
                'anchor': "What is my safe place? What makes me grounded?",
                'telescope': "Where is my attention going? Can I manage it better?",
                'bell': "Do I pay attention to danger and risk triggers?",
                'sea storm': "How do you cope in time of high stress and pressure?",
                'pirats': "How do I deal with very negative connections in my life?",
                'main sail': "What is my motivation for change? What is my responsibility? What am I willing to do?"
            }
        else:  # coping
            instructions = {
                'stormy clouds': "You have a lot of negative thoughts, what do you do?",
                'tornedo': "You have obsessive thoughts, how do you handle and manage them?",
                'black clouds': "You have what if thoughts, how do you handle?",
                'mutiny': "You are in a conflict within yourself, how do you resolve it?",
                'stack on the rocks': "How do you make decisions?",
                'sea battle': "Do you know how to argue and fight on matters that are important?",
                'counter winds': "Can you handle criticism? Can you give constructive criticism to others?",
                'horricane': "How do you handle high stress risk situations?",
                'bombs away': "How do you handle anger?",
                'no wind': "How do you handle sadness?",
                'turbulance': "How do you handle stress?",
                'mermaids': "How do you handle urges?",
                'wheel broken': "What happens when you lose control?",
                'changing rout': "Can you adapt and make changes on the way?"
            }
        return instructions.get(self.symbol, "Reflect on this moment.")

    def update(self):
        """Update card animation"""
        if self.flipping:
            self.flip_progress += self.flip_speed
            if self.flip_progress >= 1:
                self.flip_progress = 0
                self.flipping = False

    def draw(self, screen):
        try:
            card_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
            # Draw shadow
            shadow_rect = card_rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            draw_rounded_rect(screen, shadow_rect, SHADOW_COLOR, 15)
            
            # Draw card
            color = LIGHT_BLUE if self.card_type == 'reflection' else GOLD
            draw_rounded_rect(screen, card_rect, color, 15)
            pygame.draw.rect(screen, BLACK, card_rect, 2, border_radius=15)
            
            if self.state == 'symbol':
                # For reflection cards, show sign image on front
                if self.card_type == 'reflection' and self.symbol in sign_images:
                    sign_img = sign_images[self.symbol]
                    img_rect = sign_img.get_rect(center=(self.x + self.width//2, 
                                                       self.y + self.height//2 - 30))
                    screen.blit(sign_img, img_rect)
                    
                    # Draw symbol text below image
                    symbol_text = card_font.render(self.symbol, True, BLACK)
                    symbol_rect = symbol_text.get_rect(centerx=self.x + self.width//2,
                                                     centery=self.y + self.height//2 + 80)
                    screen.blit(symbol_text, symbol_rect)
                else:
                    # Draw symbol text in center if no image
                    symbol_text = card_font.render(self.symbol, True, BLACK)
                    symbol_rect = symbol_text.get_rect(centerx=self.x + self.width//2,
                                                     centery=self.y + self.height//2)
                    screen.blit(symbol_text, symbol_rect)
                
                # Draw card type at bottom
                type_text = instruction_font.render(self.card_type.capitalize(), True, BLACK)
                type_rect = type_text.get_rect(centerx=self.x + self.width//2,
                                             bottom=self.y + self.height - 20)
                screen.blit(type_text, type_rect)
            else:
                # For reflection cards, show sign image at the top
                if self.card_type == 'reflection' and self.symbol in sign_images:
                    sign_img = sign_images[self.symbol]
                    img_rect = sign_img.get_rect(centerx=self.x + self.width//2, 
                                               top=self.y + 20)
                    screen.blit(sign_img, img_rect)
                    
                    # Adjust starting position for text to be below the image
                    text_start_y = img_rect.bottom + 20
                else:
                    # For coping cards or if no image, start text higher
                    text_start_y = self.y + 50
                
                # Draw instructions with proper wrapping
                instructions = self.get_instruction_text()
                words = instructions.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_surface = instruction_font.render(test_line, True, BLACK)
                    if test_surface.get_width() <= self.width - 40:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                
                y_offset = text_start_y
                for line in lines:
                    text = instruction_font.render(line, True, BLACK)
                    text_rect = text.get_rect(centerx=self.x + self.width//2, top=y_offset)
                    screen.blit(text, text_rect)
                    y_offset += INSTRUCTION_FONT_SIZE + 10
                
                # Draw continue prompt
                continue_text = instruction_font.render("Press SPACE to continue", True, BLACK)
                continue_rect = continue_text.get_rect(centerx=self.x + self.width//2,
                                                     bottom=self.y + self.height - 20)
                screen.blit(continue_text, continue_rect)
        except Exception as e:
            print(f"Error drawing card: {e}")
            self.state = 'symbol'  # Reset to symbol state if there's an error

# Add this new class for the exchange interface
class ExchangeInterface:
    def __init__(self, other_player_cards):
        self.other_player = 2 if current_player == 1 else 1
        self.cards = []
        
        # Create list of available cards
        for card_type in ['reflection', 'coping']:
            count = player_card_counts[self.other_player][card_type]
            for i in range(count):
                self.cards.append({
                    'type': card_type,
                    'index': i,
                    'rect': pygame.Rect(0, 0, 60, 80)  # Smaller cards
                })
        self.selected_index = None
        
        # Calculate total width needed for cards
        total_width = len(self.cards) * 80  # 80px spacing between cards
        self.start_x = (WIDTH - total_width) // 2
        self.start_y = HEIGHT // 2 - 100  # Move up slightly
    
    def draw(self, screen):
        try:
            # Draw semi-transparent background
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            # Draw title
            text = game_font.render(f"Take a card from Player {self.other_player}", True, WHITE)
            text_rect = text.get_rect(centerx=WIDTH // 2, y=self.start_y - 50)
            screen.blit(text, text_rect)
            
            # Draw available cards
            for i, card in enumerate(self.cards):
                card['rect'].x = self.start_x + i * 80
                card['rect'].y = self.start_y
                
                # Draw card background
                color = LIGHT_BLUE if card['type'] == 'reflection' else GOLD
                draw_rounded_rect(screen, card['rect'], color, 10)
                
                # Draw border (highlighted if selected)
                border_color = GOLD if i == self.selected_index else BLACK
                border_width = 3 if i == self.selected_index else 1
                pygame.draw.rect(screen, border_color, card['rect'], border_width, border_radius=10)
                
                # Draw card text
                if card['type'] == 'reflection':
                    text = card_font.render("R", True, BLACK)
                else:
                    text = card_font.render("C", True, BLACK)
                text_rect = text.get_rect(center=card['rect'].center)
                screen.blit(text, text_rect)
            
            # Draw instruction
            if self.selected_index is not None:
                text = instruction_font.render("Press SPACE to take card", True, WHITE)
                text_rect = text.get_rect(centerx=WIDTH // 2, y=self.start_y + 100)
                screen.blit(text, text_rect)
        
        except Exception as e:
            print(f"Error drawing exchange interface: {e}")
            return

def draw_rounded_rect(surface, rect, color, corner_radius):
    """Draw a rounded rectangle with a gradient effect"""
    if corner_radius < 0:
        corner_radius = 0
    
    # Create gradient colors
    color_top = color
    color_bottom = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
    
    # Draw the main rectangle
    height = rect.height
    gradient_step = height // 2
    for i in range(height):
        progress = i / gradient_step if i < gradient_step else 1.0
        current_color = (
            int(color_top[0] + (color_bottom[0] - color_top[0]) * progress),
            int(color_top[1] + (color_bottom[1] - color_top[1]) * progress),
            int(color_top[2] + (color_bottom[2] - color_top[2]) * progress)
        )
        pygame.draw.rect(surface, current_color, (rect.x, rect.y + i, rect.width, 1))
    
    # Draw the rounded corners
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius - 1, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color_bottom, (rect.left + corner_radius, rect.bottom - corner_radius - 1), corner_radius)
    pygame.draw.circle(surface, color_bottom, (rect.right - corner_radius - 1, rect.bottom - corner_radius - 1), corner_radius)

def create_noise_texture(width, height, alpha=30):
    """Create a noise texture for the parchment effect"""
    texture = pygame.Surface((width, height), pygame.SRCALPHA)
    for x in range(width):
        for y in range(height):
            noise = random.randint(0, alpha)
            texture.set_at((x, y), (0, 0, 0, noise))
    return texture

def draw_compass_rose():
    """Draw a decorative compass rose"""
    compass_size = 50  # Smaller compass
    x, y = WIDTH - compass_size - 15, HEIGHT - compass_size - 15
    
    # Draw compass circle
    pygame.draw.circle(screen, COMPASS_GOLD, (x, y), compass_size//2, 2)
    
    # Draw compass points
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        end_x = x + math.cos(rad) * (compass_size//2 - 5)
        end_y = y + math.sin(rad) * (compass_size//2 - 5)
        pygame.draw.line(screen, COMPASS_GOLD, (x, y), (end_x, end_y), 2)
    
    # Draw N,S,E,W labels with smaller font
    directions = {'N': 0, 'E': 90, 'S': 180, 'W': 270}
    small_font = pygame.font.Font(None, 20)
    for direction, angle in directions.items():
        rad = math.radians(angle)
        text_x = x + math.cos(rad) * (compass_size//2 + 8)
        text_y = y + math.sin(rad) * (compass_size//2 + 8)
        text = small_font.render(direction, True, COMPASS_GOLD)
        text_rect = text.get_rect(center=(text_x, text_y))
        screen.blit(text, text_rect)

def draw_map_border():
    """Draw a decorative border around the game area"""
    border_width = 20
    margin = 10
    
    # Draw main border
    pygame.draw.rect(screen, MAP_BORDER, (margin, margin, 
                    WIDTH - 2*margin, HEIGHT - 2*margin), border_width)
    
    # Draw corner decorations
    corner_size = 30
    corners = [(margin, margin), (WIDTH-margin-corner_size, margin),
              (margin, HEIGHT-margin-corner_size), 
              (WIDTH-margin-corner_size, HEIGHT-margin-corner_size)]
    
    for x, y in corners:
        pygame.draw.rect(screen, MAP_BORDER, (x, y, corner_size, corner_size), 3)
        pygame.draw.line(screen, MAP_BORDER, (x+5, y+5), 
                        (x+corner_size-5, y+corner_size-5), 3)
        pygame.draw.line(screen, MAP_BORDER, (x+corner_size-5, y+5),
                        (x+5, y+corner_size-5), 3)

def draw_waves(x, y, size):
    """Draw animated waves with multiple layers"""
    global wave_offset
    points = []
    wave_surfaces = []
    
    # Create base hexagon points
    for i in range(6):
        angle_deg = 60 * i + 30
        angle_rad = math.pi / 180 * angle_deg
        point_x = x + size * math.cos(angle_rad)
        point_y = y + size * math.sin(angle_rad)
        points.append((point_x, point_y))
    
    # Create mask for waves
    mask = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.polygon(mask, WHITE, points)
    
    # Draw multiple wave layers
    for layer in range(WAVE_COUNT):
        wave_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        wave_points = []
        
        # Create wave points with varying parameters
        wave_segments = 30
        for i in range(wave_segments):
            progress = i / wave_segments
            wave_x = x - size + (size * 2 * progress)
            wave_y = y + math.sin(progress * WAVE_FREQUENCIES[layer] * math.pi + 
                                wave_offset * WAVE_SPEEDS[layer]) * WAVE_AMPLITUDES[layer]
            wave_points.append((wave_x, wave_y))
        
        # Draw waves with fade effect
        for i in range(len(wave_points) - 1):
            alpha = int(255 * (0.3 + layer * 0.2))  # Varying opacity for each layer
            color = (*WAVE_COLOR[:3], alpha)
            pygame.draw.line(wave_surface, color, wave_points[i], wave_points[i + 1], 2)
        
        wave_surfaces.append(wave_surface)
    
    # Combine wave layers
    combined_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    for surface in wave_surfaces:
        combined_surface.blit(surface, (0, 0))
    
    # Apply hexagon mask
    combined_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(combined_surface, (x - size, y - size))

def draw_hexagon(x, y, size, color):
    """Draw a hexagon with multi-layered waves and aged effect"""
    points = []
    shadow_points = []
    
    # Create hexagon points
    for i in range(6):
        angle_deg = 60 * i + 30
        angle_rad = math.pi / 180 * angle_deg
        point_x = x + size * math.cos(angle_rad)
        point_y = y + size * math.sin(angle_rad)
        points.append((point_x, point_y))
        shadow_points.append((point_x + 3, point_y + 3))
    
    # Draw shadow with gradient
    shadow_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.polygon(shadow_surface, SHADOW_COLOR, shadow_points)
    screen.blit(shadow_surface, (x - size, y - size))
    
    # Draw base hexagon with sea blue gradient
    gradient_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    for i in range(size * 2):
        progress = i / (size * 2)
        current_color = (
            int(DARK_BLUE[0] + (BLUE[0] - DARK_BLUE[0]) * progress),
            int(DARK_BLUE[1] + (BLUE[1] - DARK_BLUE[1]) * progress),
            int(DARK_BLUE[2] + (BLUE[2] - DARK_BLUE[2]) * progress)
        )
        pygame.draw.line(gradient_surface, current_color, (0, i), (size * 2, i))
    
    # Apply gradient to hexagon
    hex_mask = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.polygon(hex_mask, (255, 255, 255, 255), points)
    gradient_surface.blit(hex_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(gradient_surface, (x - size, y - size))
    
    # Draw waves with enhanced effect
    draw_waves(x, y, size - 2)
    
    # Draw hexagon border with gradient
    for i in range(2):
        border_color = (255, 255, 255, 100) if i == 0 else (0, 0, 0, 100)
        pygame.draw.polygon(screen, border_color, points, 1)
        gfxdraw.aapolygon(screen, points, border_color)

def draw_boat_with_animation(x, y, boat_image, offset):
    """Draw boat with simple rocking animation"""
    # Calculate boat movement
    boat_y = y + math.sin(animation_time * BOAT_ROCK_SPEED) * BOAT_ROCK_AMPLITUDE
    boat_angle = math.sin(animation_time * BOAT_ROCK_SPEED) * 5  # Rock by 5 degrees
    
    # Draw boat shadow
    shadow_surface = pygame.Surface((boat_size, boat_size), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surface, SHADOW_COLOR, (boat_size//2, boat_size//2), boat_size//2)
    screen.blit(shadow_surface, (x - boat_size//2 + 3, boat_y - boat_size//2 + 3))
    
    # Rotate and draw boat
    rotated_boat = pygame.transform.rotate(boat_image, boat_angle)
    boat_rect = rotated_boat.get_rect(center=(x, boat_y))
    screen.blit(rotated_boat, boat_rect)

def draw_card(surface, rect, color, symbol=None, text=None, selected=False):
    """Draw a modern-looking card with shadow and gradient effects"""
    # Draw card shadow with blur effect
    shadow_rect = rect.copy()
    shadow_rect.x += 5
    shadow_rect.y += 5
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (0, 0, rect.width, rect.height), border_radius=10)
    surface.blit(shadow_surface, (shadow_rect.x - rect.x, shadow_rect.y - rect.y))
    
    # Draw card background with gradient
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        progress = i / rect.height
        current_color = (
            int(color[0] + (255 - color[0]) * progress),
            int(color[1] + (255 - color[1]) * progress),
            int(color[2] + (255 - color[2]) * progress)
        )
        pygame.draw.line(gradient_surface, current_color, (0, i), (rect.width, i))
    
    # Apply gradient to card
    surface.blit(gradient_surface, (rect.x, rect.y))
    
    # Draw border with glow effect if selected
    if selected:
        glow_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*GOLD[:3], 100), (0, 0, rect.width + 10, rect.height + 10), border_radius=15)
        surface.blit(glow_surface, (rect.x - 5, rect.y - 5))
    
    border_color = GOLD if selected else BLACK
    border_width = 3 if selected else 1
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=10)
    
    if symbol:
        # Draw symbol with shadow
        symbol_shadow = card_font.render(symbol, True, (0, 0, 0, 100))
        symbol_text = card_font.render(symbol, True, BLACK)
        symbol_rect = symbol_text.get_rect(center=rect.center)
        surface.blit(symbol_shadow, (symbol_rect.x + 2, symbol_rect.y + 2))
        surface.blit(symbol_text, symbol_rect)
    
    if text:
        # Draw text with shadow
        text_shadow = instruction_font.render(text, True, (0, 0, 0, 100))
        text_surface = instruction_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10)
        surface.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surface, text_rect)

def draw_button(surface, rect, text, color, hover=False):
    """Draw a modern button with hover effect and glow"""
    if hover:
        # Create glow effect
        glow_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color[:3], 100), (0, 0, rect.width + 10, rect.height + 10), border_radius=15)
        surface.blit(glow_surface, (rect.x - 5, rect.y - 5))
        color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
    
    # Draw button background with gradient
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        progress = i / rect.height
        current_color = (
            int(color[0] + (255 - color[0]) * progress),
            int(color[1] + (255 - color[1]) * progress),
            int(color[2] + (255 - color[2]) * progress)
        )
        pygame.draw.line(gradient_surface, current_color, (0, i), (rect.width, i))
    
    surface.blit(gradient_surface, (rect.x, rect.y))
    
    # Draw border
    pygame.draw.rect(surface, BLACK, rect, 1, border_radius=10)
    
    # Draw text with shadow
    text_shadow = game_font.render(text, True, (0, 0, 0, 100))
    text_surface = game_font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
    surface.blit(text_surface, text_rect)

def draw_dice(value):
    """Draw the dice with dots instead of numbers at the bottom of the screen"""
    # Position dice at the bottom center of the screen, moved up by 40 pixels
    dice_rect = pygame.Rect(WIDTH//2 - DICE_SIZE//2, HEIGHT - DICE_SIZE - DICE_MARGIN - 40, 
                          DICE_SIZE, DICE_SIZE)
    
    # Draw dice background with shadow
    shadow_rect = dice_rect.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3
    draw_rounded_rect(screen, shadow_rect, SHADOW_COLOR, 10)
    
    # Draw main dice
    draw_rounded_rect(screen, dice_rect, WHITE, 10)
    pygame.draw.rect(screen, BLACK, dice_rect, 2, border_radius=10)
    
    if value > 0:
        # Calculate dot positions based on dice value
        dot_radius = DICE_SIZE // 10
        dot_positions = []
        
        # Define dot positions for each dice value
        if value == 1:
            dot_positions = [(0.5, 0.5)]
        elif value == 2:
            dot_positions = [(0.25, 0.25), (0.75, 0.75)]
        elif value == 3:
            dot_positions = [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)]
        elif value == 4:
            dot_positions = [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)]
        elif value == 5:
            dot_positions = [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]
        elif value == 6:
            dot_positions = [(0.25, 0.25), (0.5, 0.25), (0.75, 0.25),
                           (0.25, 0.75), (0.5, 0.75), (0.75, 0.75)]
        
        # Draw dots with shadow effect
        for pos_x, pos_y in dot_positions:
            dot_x = int(dice_rect.x + pos_x * DICE_SIZE)
            dot_y = int(dice_rect.y + pos_y * DICE_SIZE)
            # Draw shadow
            pygame.draw.circle(screen, SHADOW_COLOR, (dot_x + 1, dot_y + 1), dot_radius)
            # Draw dot
            pygame.draw.circle(screen, BLACK, (dot_x, dot_y), dot_radius)

def roll_dice():
    """Roll the dice and return a random number between 1 and 6"""
    return random.randint(1, 6)

def draw_card_stacks(screen):
    """Draw the accumulated card stacks on the left side of the board"""
    # Draw player info box
    info_box = pygame.Rect(10, 10, INFO_BOX_WIDTH, INFO_BOX_HEIGHT)
    draw_rounded_rect(screen, info_box, WHITE, 8)
    pygame.draw.rect(screen, BLACK, info_box, 2, border_radius=8)
    
    label_font = pygame.font.Font(None, 20)  # Smaller font
    y_offset = 20
    
    for player in range(1, num_players + 1):
        # Player header
        player_text = f"Player {player}:"
        text = label_font.render(player_text, True, BLACK)
        screen.blit(text, (20, y_offset))
        
        # Card counts
        reflection_text = f"Self: {player_card_counts[player]['reflection']}"
        text = label_font.render(reflection_text, True, BLACK)
        screen.blit(text, (30, y_offset + 15))
        
        coping_text = f"Coping: {player_card_counts[player]['coping']}"
        text = label_font.render(coping_text, True, BLACK)
        screen.blit(text, (30, y_offset + 30))
        
        y_offset += 45
    
    # Draw card stacks with proper spacing and labels
    stack_y = 120
    
    for player in range(1, num_players + 1):
        # Draw player label
        player_label = label_font.render(f"Player {player}", True, BLACK)
        player_rect = player_label.get_rect(x=20, y=stack_y)
        screen.blit(player_label, player_rect)
        
        # Draw reflection pile
        reflection_y = stack_y + 25
        reflection_label = label_font.render("Reflection", True, LIGHT_BLUE)
        screen.blit(reflection_label, (20, reflection_y))
        
        # Draw reflection cards in a stack
        if len(collected_cards[player]['reflection']) > 0:
            pile_rect = pygame.Rect(20, reflection_y + 20, 40, 60)
            draw_rounded_rect(screen, pile_rect, LIGHT_BLUE, 5)
            pygame.draw.rect(screen, BLACK, pile_rect, 1, border_radius=5)
            
            # Draw number of cards on the pile
            count = len(collected_cards[player]['reflection'])
            if count > 0:
                count_text = label_font.render(str(count), True, BLACK)
                count_rect = count_text.get_rect(center=pile_rect.center)
                screen.blit(count_text, count_rect)
        
        # Draw coping pile
        coping_y = reflection_y + 90
        coping_label = label_font.render("Coping", True, GOLD)
        screen.blit(coping_label, (20, coping_y))
        
        # Draw coping cards in a stack
        if len(collected_cards[player]['coping']) > 0:
            pile_rect = pygame.Rect(20, coping_y + 20, 40, 60)
            draw_rounded_rect(screen, pile_rect, GOLD, 5)
            pygame.draw.rect(screen, BLACK, pile_rect, 1, border_radius=5)
            
            # Draw number of cards on the pile
            count = len(collected_cards[player]['coping'])
            if count > 0:
                count_text = label_font.render(str(count), True, BLACK)
                count_rect = count_text.get_rect(center=pile_rect.center)
                screen.blit(count_text, count_rect)
        
        # Move to next player's section
        stack_y += 200

def check_collisions():
    """Check if current player's boat has landed on an island or octopus"""
    global card_display_state, current_card_symbol, centered_card, waiting_for_card_interaction
    current_pos = player1_pos if current_player == 1 else player2_pos
    
    try:
        # Check for island collision
        if current_pos in island_positions:
            if player_card_counts[current_player]['reflection'] < 3:
                play_sound(boat_sand_sound)
                current_card_symbol = random.choice(CARD_SYMBOLS)
                card_display_state = 'symbol'
                centered_card = CenteredCard(current_card_symbol, 'reflection')
                waiting_for_card_interaction = True
                return True, 'reflection'
        
        # Check for octopus collision
        elif current_pos in octopus_positions:
            if player_card_counts[current_player]['reflection'] >= 3:
                play_sound(monster_sound)
                current_card_symbol = random.choice(COPING_SYMBOLS)
                card_display_state = 'symbol'
                centered_card = CenteredCard(current_card_symbol, 'coping')
                waiting_for_card_interaction = True
                return True, 'coping'
        
        return False, None
    except Exception as e:
        print(f"Error in check_collisions: {e}")
        return False, None

def move_boat(steps):
    """Move the current player's boat"""
    global player1_pos, player2_pos, waiting_for_card_interaction, card_display_state, current_player
    
    try:
        current_pos = player1_pos.copy() if current_player == 1 else player2_pos.copy()
        initial_steps = steps
        
        for step in range(steps):
            play_sound(boat_move_sound)
            
            if current_player == 1:
                # Player 1: Moving right and down
                at_row_end = current_pos['col'] == COLS - 1
                
                if at_row_end:
                    if current_pos['row'] < ROWS - 1:
                        current_pos['row'] += 1
                    else:
                        current_pos['row'] = 0
                    current_pos['col'] = 0
                else:
                    current_pos['col'] = min(COLS - 1, current_pos['col'] + 1)
            else:
                # Player 2: Moving left and up
                at_row_end = current_pos['col'] == 0
                
                if at_row_end:
                    if current_pos['row'] > 0:
                        current_pos['row'] -= 1
                    else:
                        current_pos['row'] = ROWS - 1
                    current_pos['col'] = COLS - 1
                else:
                    current_pos['col'] = max(0, current_pos['col'] - 1)
            
            # Update the correct player's position
            if current_player == 1:
                player1_pos = current_pos.copy()
            else:
                player2_pos = current_pos.copy()
            
            # Update display
            screen.fill(WHITE)
            draw_game_state()
            pygame.display.flip()
            pygame.time.delay(move_delay)
        
        # After movement is complete, check for collisions or boat meeting
        if steps == initial_steps:
            # Check for boats meeting first
            if check_boats_meeting():
                return True, 'exchange'
            
            # Then check for island/octopus collisions
            collision_result = check_collisions()
            if collision_result[0]:  # If there was a collision
                return collision_result
            
            # If no collision or meeting, switch players (in 2-player mode)
            if not collision_result[0] and num_players == 2:
                current_player = 2 if current_player == 1 else 1
            
            return False, None
        
        return False, None
    except Exception as e:
        print(f"Error in move_boat: {e}")
        return False, None

def draw_close_button():
    """Draw an X button in the top-right corner"""
    button_size = 30  # Smaller close button
    margin = 15  # Increased margin from 8 to 15 to move it down from the very top
    x = WIDTH - button_size - margin
    y = margin
    
    # Draw button background
    button_rect = pygame.Rect(x, y, button_size, button_size)
    mouse_pos = pygame.mouse.get_pos()
    color = CLOSE_BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else CLOSE_BUTTON_COLOR
    
    draw_rounded_rect(screen, button_rect, color, 8)
    pygame.draw.rect(screen, BLACK, button_rect, 2, border_radius=8)
    
    # Draw X
    padding = 8
    line_width = 3
    pygame.draw.line(screen, WHITE, 
                    (x + padding, y + padding),
                    (x + button_size - padding, y + button_size - padding),
                    line_width)
    pygame.draw.line(screen, WHITE,
                    (x + button_size - padding, y + padding),
                    (x + padding, y + button_size - padding),
                    line_width)
    
    return button_rect

def draw_game_state():
    global wave_offset, animation_time
    
    # Fill background with light green color
    screen.fill(LIGHT_GREEN)
    
    # Update animation
    wave_offset += WAVE_SPEED
    animation_time += 0.1
    
    # Draw hexagonal grid
    for row in range(ROWS):
        for col in range(COLS):
            x, y = get_hex_center(row, col)
            draw_hexagon(x, y, HEX_SIZE, BLUE)  # Keep hexagons blue for sea
            
            pos = {'row': row, 'col': col}
            if pos in island_positions:
                island_x = x - island_size // 2
                island_y = y - island_size // 2
                screen.blit(island_image, (island_x, island_y))
            
            if pos in octopus_positions:
                octopus_x = x - octopus_size // 2
                octopus_y = y - octopus_size // 2
                screen.blit(octopus_image, (octopus_x, octopus_y))
    
    # Draw boats with enhanced animation
    boat1_x, boat1_y = get_hex_center(player1_pos['row'], player1_pos['col'])
    draw_boat_with_animation(boat1_x, boat1_y, boat_image, boat1_offset)
    
    if num_players == 2:
        boat2_x, boat2_y = get_hex_center(player2_pos['row'], player2_pos['col'])
        draw_boat_with_animation(boat2_x, boat2_y, boat2_image, boat2_offset)
    
    # Draw compass rose in bottom right
    draw_compass_rose()
    
    # Draw dice at the bottom center
    draw_dice(current_roll)
    
    # Draw card stacks on the left
    draw_card_stacks(screen)
    
    # Draw current player indicator aligned with dice
    player_text = f"Player {current_player}'s Turn"
    text = game_font.render(player_text, True, BLACK)
    # Position text at the same height as the dice, but on the right side
    text_rect = text.get_rect(right=WIDTH - 20, centery=HEIGHT - DICE_SIZE - DICE_MARGIN - 40)
    
    # Draw background for player indicator
    bg_rect = text_rect.copy()
    bg_rect.inflate_ip(20, 10)
    draw_rounded_rect(screen, bg_rect, PARCHMENT_COLOR, 10)
    pygame.draw.rect(screen, MAP_BORDER, bg_rect, 2, border_radius=10)
    
    screen.blit(text, text_rect)
    
    # Draw close button in top right
    draw_close_button()
    
    if game_state == GAME_STATE_WINNER:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw winner announcement
        winner_text = f"Player {check_winner()} Wins!"
        text = title_font.render(winner_text, True, COMPASS_GOLD)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        # Draw decorative background for winner text
        bg_rect = text_rect.copy()
        bg_rect.inflate_ip(60, 40)
        draw_rounded_rect(screen, bg_rect, MAP_BORDER, 15)
        pygame.draw.rect(screen, COMPASS_GOLD, bg_rect, 4, border_radius=15)
        
        screen.blit(text, text_rect)

# Create a function to draw the menu
def draw_menu():
    # Fill with parchment color
    screen.fill(PARCHMENT_COLOR)
    
    # Draw decorative border with gradient
    border_width = 20
    margin = 10
    
    # Draw main border with gradient
    gradient_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(HEIGHT):
        progress = i / HEIGHT
        current_color = (
            int(MAP_BORDER[0] + (COMPASS_GOLD[0] - MAP_BORDER[0]) * progress),
            int(MAP_BORDER[1] + (COMPASS_GOLD[1] - MAP_BORDER[1]) * progress),
            int(MAP_BORDER[2] + (COMPASS_GOLD[2] - MAP_BORDER[2]) * progress)
        )
        pygame.draw.line(gradient_surface, current_color, (margin, i), (WIDTH - margin, i))
    
    screen.blit(gradient_surface, (0, 0))
    
    # Draw corner decorations with glow effect
    corner_size = 30
    corners = [(margin, margin), (WIDTH-margin-corner_size, margin),
              (margin, HEIGHT-margin-corner_size), 
              (WIDTH-margin-corner_size, HEIGHT-margin-corner_size)]
    
    for x, y in corners:
        glow_surface = pygame.Surface((corner_size + 10, corner_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*COMPASS_GOLD[:3], 100), 
                        (0, 0, corner_size + 10, corner_size + 10), 3)
        screen.blit(glow_surface, (x - 5, y - 5))
        pygame.draw.rect(screen, MAP_BORDER, (x, y, corner_size, corner_size), 3)
        pygame.draw.line(screen, COMPASS_GOLD, (x+5, y+5), 
                        (x+corner_size-5, y+corner_size-5), 3)
        pygame.draw.line(screen, COMPASS_GOLD, (x+corner_size-5, y+5),
                        (x+5, y+corner_size-5), 3)
    
    # Draw compass rose with glow
    draw_compass_rose()
    
    # Draw close button
    draw_close_button()
    
    # Draw title with enhanced effect
    title_shadow = title_font.render("Sea Journey", True, MAP_BORDER)
    title_text = title_font.render("Sea Journey", True, COMPASS_GOLD)
    
    shadow_rect = title_shadow.get_rect(centerx=WIDTH//2 + 4, centery=HEIGHT//4 + 4)
    text_rect = title_text.get_rect(centerx=WIDTH//2, centery=HEIGHT//4)
    
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_text, text_rect)
    
    # Draw game explanation with enhanced styling
    explanation_font = pygame.font.Font(None, 24)
    explanation_text = [
        "Welcome to Sea Journey!",
        "Collect reflection cards from islands and coping cards from octopuses.",
        "You need 4 reflection cards and 4 coping cards to win.",
        "When boats meet, you can trade cards with the other player.",
        "Press SPACE to roll dice and move your boat.",
        "Press M to toggle music."
    ]
    
    y_offset = HEIGHT//4 + 60
    for line in explanation_text:
        # Draw text shadow
        shadow = explanation_font.render(line, True, (0, 0, 0, 100))
        shadow_rect = shadow.get_rect(centerx=WIDTH//2 + 2, centery=y_offset + 2)
        screen.blit(shadow, shadow_rect)
        
        # Draw main text
        text = explanation_font.render(line, True, AGED_BLACK)
        text_rect = text.get_rect(centerx=WIDTH//2, centery=y_offset)
        screen.blit(text, text_rect)
        y_offset += 25
    
    # Draw buttons with enhanced styling
    button1_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60)
    button2_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 170, 300, 60)
    
    for rect in [button1_rect, button2_rect]:
        # Draw button glow
        glow_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*COMPASS_GOLD[:3], 100), 
                        (0, 0, rect.width + 10, rect.height + 10), border_radius=15)
        screen.blit(glow_surface, (rect.x - 5, rect.y - 5))
        
        # Draw button background with gradient
        gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for i in range(rect.height):
            progress = i / rect.height
            current_color = (
                int(PARCHMENT_COLOR[0] + (COMPASS_GOLD[0] - PARCHMENT_COLOR[0]) * progress),
                int(PARCHMENT_COLOR[1] + (COMPASS_GOLD[1] - PARCHMENT_COLOR[1]) * progress),
                int(PARCHMENT_COLOR[2] + (COMPASS_GOLD[2] - PARCHMENT_COLOR[2]) * progress)
            )
            pygame.draw.line(gradient_surface, current_color, (0, i), (rect.width, i))
        
        screen.blit(gradient_surface, (rect.x, rect.y))
        pygame.draw.rect(screen, MAP_BORDER, rect, 2, border_radius=10)
    
    # Draw button text with shadow
    button_texts = ["1. Single Player", "2. Two Players"]
    button_rects = [button1_rect, button2_rect]
    
    for text, rect in zip(button_texts, button_rects):
        # Draw text shadow
        shadow = game_font.render(text, True, (0, 0, 0, 100))
        shadow_rect = shadow.get_rect(center=rect.center)
        shadow_rect.x += 2
        shadow_rect.y += 2
        screen.blit(shadow, shadow_rect)
        
        # Draw main text
        text_surface = game_font.render(text, True, AGED_BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    # Add noise texture for aged look
    noise = create_noise_texture(WIDTH, HEIGHT)
    screen.blit(noise, (0, 0))
    
    pygame.display.flip()

# Add this function to check for boats meeting
def check_boats_meeting():
    """Check if the boats are in the same position"""
    if num_players == 2 and player1_pos == player2_pos:
        return True
    return False

# Update the check_winner function to require 4 reflection and 4 coping cards
def check_winner():
    """Check if either player has won"""
    for player in [1, 2]:
        reflection_cards = player_card_counts[player]['reflection']
        coping_cards = player_card_counts[player]['coping']
        
        # Player needs 4 reflection cards AND 4 coping cards to win
        if reflection_cards >= 4 and coping_cards >= 4:
            play_sound(victory_sound)  # Play victory trumpets
            return player
    return None

# Update the handle_card_interaction function
def handle_card_interaction(event):
    """Handle card interaction events"""
    global waiting_for_card_interaction, card_display_state, current_card_symbol
    global centered_card, can_roll, current_player, game_state, EXCHANGE_STATE, SELECTED_CARD
    
    try:
        if EXCHANGE_STATE == 'moving' and SELECTED_CARD:
            play_sound(card_flip_sound)
            other_player = 2 if current_player == 1 else 1
            card_type = SELECTED_CARD['type']
            
            # Check if player has reached the card limit
            if player_card_counts[current_player][card_type] >= (MAX_REFLECTION_CARDS if card_type == 'reflection' else MAX_COPING_CARDS):
                # Reset states without adding card
                EXCHANGE_STATE = None
                SELECTED_CARD = None
                waiting_for_card_interaction = False
                can_roll = True
                current_player = 2 if current_player == 1 else 1
                return
            
            # Remove card from other player
            if player_card_counts[other_player][card_type] > 0:
                player_card_counts[other_player][card_type] -= 1
                if len(collected_cards[other_player][card_type]) > 0:
                    collected_cards[other_player][card_type].pop()
                
                # Add card to current player
                player_card_counts[current_player][card_type] += 1
                offset_y = len(collected_cards[current_player][card_type]) * CARD_STACK_OFFSET
                start_pos = (WIDTH // 2 - LARGE_CARD_SIZE // 2, HEIGHT // 2 - LARGE_CARD_SIZE // 2)
                base_y = 120 if card_type == 'reflection' else 260
                end_pos = (20, base_y + offset_y)
                new_card = MovingCard(card_type, start_pos, end_pos)
                animation_cards.append(new_card)
                collected_cards[current_player][card_type].append(end_pos)
            
            # Reset states
            EXCHANGE_STATE = None
            SELECTED_CARD = None
            waiting_for_card_interaction = False
            can_roll = True
            
            # Check for winner
            winner = check_winner()
            if winner:
                game_state = GAME_STATE_WINNER
            else:
                current_player = 2 if current_player == 1 else 1
            
        elif waiting_for_card_interaction and centered_card:
            if isinstance(centered_card, ExchangeInterface):
                # Handle exchange interface interaction
                if centered_card.selected_index is not None:
                    SELECTED_CARD = centered_card.cards[centered_card.selected_index]
                    EXCHANGE_STATE = 'moving'
            else:
                # Handle regular card interaction
                if card_display_state == 'symbol':
                    play_sound(card_flip_sound)
                    card_display_state = 'instructions'
                    centered_card.state = 'instructions'
                    centered_card.flipping = True
                
                elif card_display_state == 'instructions':
                    card_type = centered_card.card_type
                    
                    # Check if player has reached the card limit
                    if player_card_counts[current_player][card_type] >= (MAX_REFLECTION_CARDS if card_type == 'reflection' else MAX_COPING_CARDS):
                        # Reset states without adding card
                        card_display_state = None
                        current_card_symbol = None
                        centered_card = None
                        waiting_for_card_interaction = False
                        can_roll = True
                        if num_players == 2:
                            current_player = 2 if current_player == 1 else 1
                        return
                    
                    play_sound(collect_card_sound)
                    
                    # Add card to current player's pile
                    player_card_counts[current_player][card_type] += 1
                    offset_y = len(collected_cards[current_player][card_type]) * CARD_STACK_OFFSET
                    start_pos = (WIDTH // 2 - LARGE_CARD_SIZE // 2, HEIGHT // 2 - LARGE_CARD_SIZE // 2)
                    base_y = 120 if card_type == 'reflection' else 260
                    end_pos = (20, base_y + offset_y)
                    new_card = MovingCard(card_type, start_pos, end_pos)
                    animation_cards.append(new_card)
                    collected_cards[current_player][card_type].append(end_pos)
                    
                    # Reset states
                    card_display_state = None
                    current_card_symbol = None
                    centered_card = None
                    waiting_for_card_interaction = False
                    can_roll = True
                    
                    # Check for winner
                    winner = check_winner()
                    if winner:
                        game_state = GAME_STATE_WINNER
                    elif num_players == 2:
                        current_player = 2 if current_player == 1 else 1
    
    except Exception as e:
        print(f"Error in handle_card_interaction: {e}")
        # Reset to a safe state
        waiting_for_card_interaction = False
        card_display_state = None
        current_card_symbol = None
        centered_card = None
        can_roll = True

# Initialize game state variables
game_state = GAME_STATE_MENU
running = True

# Add battle-related variables
battle_state = None
battle_animation_time = 0
battle_result = None
battle_messages = []
BATTLE_STATE_INTRO = 'intro'
BATTLE_STATE_FIGHTING = 'fighting'
BATTLE_STATE_WIN = 'win'
BATTLE_STATE_LOSE = 'lose'
BOAT_BATTLE_SPEED = 5
ROCK_SPEED = 4
FLOWER_SPEED = 7
MONSTER_HITS_TO_WIN = 20  # Increased from 10 to 20 hits
BOAT_STARTING_HEALTH = 3

class BattleState:
    def __init__(self):
        self.state = BATTLE_STATE_INTRO
        self.boat_x = WIDTH * 0.2
        self.boat_y = HEIGHT * 0.8
        self.monster_x = WIDTH * 0.8
        self.monster_y = HEIGHT * 0.3
        self.monster_size = 200
        self.monster_health = MONSTER_HITS_TO_WIN
        self.boat_health = BOAT_STARTING_HEALTH
        self.rocks = []
        self.flowers = []
        self.rock_spawn_timer = 0
        self.monster_move_timer = 0
        self.intro_timer = 0
        self.monster_visible = True
        self.monster_moving = False
        self.monster_target_x = self.monster_x
        self.boat_rect = pygame.Rect(self.boat_x - boat_size//2, 
                                   self.boat_y - boat_size//2, 
                                   boat_size, boat_size)
        self.monster_rect = pygame.Rect(self.monster_x - self.monster_size//2, 
                                      self.monster_y - self.monster_size//2,
                                      self.monster_size, self.monster_size)

    def update(self):
        if self.state == BATTLE_STATE_INTRO:
            self.intro_timer += 1
            if self.intro_timer > 180:  # 3 seconds at 60 FPS
                self.state = BATTLE_STATE_FIGHTING
        
        elif self.state == BATTLE_STATE_FIGHTING:
            # Update boat position based on keyboard input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.boat_x = max(boat_size//2, self.boat_x - BOAT_BATTLE_SPEED)
            if keys[pygame.K_RIGHT]:
                self.boat_x = min(WIDTH - boat_size//2, self.boat_x + BOAT_BATTLE_SPEED)
            
            # Update boat rect
            self.boat_rect.x = self.boat_x - boat_size//2
            self.boat_rect.y = self.boat_y - boat_size//2
            
            # Monster movement
            if not self.monster_moving and random.random() < 0.02:  # 2% chance to start moving
                self.monster_moving = True
                self.monster_visible = False
                self.monster_target_x = random.randint(int(WIDTH * 0.6), int(WIDTH * 0.9))
                self.monster_y = HEIGHT * 0.3  # Reset height when moving
            
            if self.monster_moving:
                self.monster_move_timer += 1
                if self.monster_move_timer > 60:  # Show monster after 1 second
                    self.monster_visible = True
                    # Move towards target
                    dx = self.monster_target_x - self.monster_x
                    if abs(dx) < 2:
                        self.monster_moving = False
                        self.monster_move_timer = 0
                    else:
                        self.monster_x += dx * 0.1
            
            # Update monster rect
            self.monster_rect.x = self.monster_x - self.monster_size//2
            self.monster_rect.y = self.monster_y - self.monster_size//2
            
            # Spawn rocks with increasing frequency as monster gets smaller
            spawn_rate = max(15, 45 - (MONSTER_HITS_TO_WIN - self.monster_health))  # More aggressive scaling
            self.rock_spawn_timer += 1
            if self.rock_spawn_timer > spawn_rate and self.monster_visible:
                self.rock_spawn_timer = 0
                num_rocks = min(5, 2 + (MONSTER_HITS_TO_WIN - self.monster_health) // 4)  # Increase rocks based on damage
                for _ in range(num_rocks):  # Spawn multiple rocks
                    rock_x = self.monster_x + random.randint(-50, 50)
                    self.rocks.append(Rock(rock_x, self.monster_y + self.monster_size//2))
            
            # Update and check rocks
            for rock in self.rocks[:]:
                rock.update()
                if rock.y > HEIGHT:
                    self.rocks.remove(rock)
                elif rock.rect.colliderect(self.boat_rect):
                    self.rocks.remove(rock)
                    self.boat_health -= 1
                    if self.boat_health <= 0:
                        self.state = BATTLE_STATE_LOSE
            
            # Update and check flowers
            for flower in self.flowers[:]:
                flower.update()
                if flower.y < 0:
                    self.flowers.remove(flower)
                elif self.monster_visible and flower.rect.colliderect(self.monster_rect):
                    self.flowers.remove(flower)
                    self.monster_health -= 1
                    # Make monster smaller but increase attack frequency
                    self.monster_size = max(40, 200 - (MONSTER_HITS_TO_WIN - self.monster_health) * 8)
                    if self.monster_health <= 0:
                        self.state = BATTLE_STATE_WIN

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = ROCK_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.circle(screen, (139, 69, 19), 
                         (self.x + self.width//2, self.y + self.height//2), 
                         self.width//2)

class CompassionFlower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = FLOWER_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        # Draw flower petals
        petal_color = (255, 192, 203)  # Pink
        center_color = (255, 255, 0)   # Yellow
        center = (self.x + self.width//2, self.y + self.height//2)
        
        for i in range(6):
            angle = i * 60
            x = center[0] + math.cos(math.radians(angle)) * 8
            y = center[1] + math.sin(math.radians(angle)) * 8
            pygame.draw.circle(screen, petal_color, (int(x), int(y)), 6)
        
        # Draw flower center
        pygame.draw.circle(screen, center_color, center, 5)

class BattleButton:
    def __init__(self):
        self.width = 200
        self.height = 50
        self.x = 20  # Changed from right side to left side
        self.y = HEIGHT - self.height - 20  # Keep at bottom
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = (220, 20, 60)  # Crimson red
        self.hover_color = (240, 128, 128)  # Light coral
        self.is_hovered = False
        self.text = "Inner Voice Monster"
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with gradient and glow effect
        if self.is_hovered:
            # Draw glow
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color[:3], 100), 
                           (0, 0, self.width + 10, self.height + 10), border_radius=15)
            screen.blit(glow_surface, (self.x - 5, self.y - 5))
        
        # Draw button background with gradient
        gradient_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(self.height):
            progress = i / self.height
            current_color = (
                int(color[0] + (255 - color[0]) * progress * 0.5),
                int(color[1] + (255 - color[1]) * progress * 0.5),
                int(color[2] + (255 - color[2]) * progress * 0.5)
            )
            pygame.draw.line(gradient_surface, current_color, (0, i), (self.width, i))
        
        # Apply gradient to button
        button_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(gradient_surface, color, button_rect, border_radius=10)
        screen.blit(gradient_surface, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        # Draw text with shadow
        text_surface = game_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Draw shadow
        shadow_surface = game_font.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw main text
        screen.blit(text_surface, text_rect)

def draw_battle_screen():
    """Draw the battle screen with the octopus monster and battle mechanics"""
    global battle_state, game_state, player_card_counts, current_player, battle_animation_time
    
    if battle_state is None:
        battle_state = BattleState()
    
    # Update animation time
    battle_animation_time += 0.1
    
    # Fill background with dark sea color
    screen.fill((0, 45, 98))
    
    # Draw animated waves
    wave_height = HEIGHT * 0.85
    for i in range(WIDTH):
        x = i
        y = wave_height + math.sin(battle_animation_time * 0.05 + i * 0.02) * 20
        pygame.draw.line(screen, WAVE_COLOR, (x, y), (x, HEIGHT))
    
    # Draw battle state specific elements
    if battle_state.state == BATTLE_STATE_INTRO:
        # Draw emerging monster animation
        emerge_progress = min(1.0, battle_state.intro_timer / 180)
        monster_y = HEIGHT - (HEIGHT - battle_state.monster_y) * emerge_progress
        
        # Draw monster (octopus)
        draw_octopus(battle_state.monster_x, monster_y, battle_state.monster_size)
        
        # Draw intro text with enhanced readability
        # Create text background
        text = title_font.render("Inner Voice Monster Appears!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//3))
        
        # Draw text background
        bg_rect = text_rect.copy()
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        
        # Draw text with glow
        glow_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        glow_color = (255, 255, 255, 50)
        glow_text = title_font.render("Inner Voice Monster Appears!", True, glow_color)
        for offset in range(0, 10, 2):
            screen.blit(glow_text, (text_rect.x - offset, text_rect.y))
            screen.blit(glow_text, (text_rect.x + offset, text_rect.y))
        screen.blit(text, text_rect)
    
    elif battle_state.state == BATTLE_STATE_FIGHTING:
        # Draw monster if visible
        if battle_state.monster_visible:
            draw_octopus(battle_state.monster_x, battle_state.monster_y, 
                        battle_state.monster_size)
            
            # Show "Critical Thoughts Attack" with enhanced readability
            if len(battle_state.rocks) > 0:
                attack_text = game_font.render("Critical Thoughts Attack!", True, (255, 0, 0))
                text_rect = attack_text.get_rect(centerx=WIDTH//2, y=50)
                
                # Draw text background
                bg_rect = text_rect.copy()
                bg_rect.inflate_ip(20, 10)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                
                # Add glow effect
                glow_surface = pygame.Surface(attack_text.get_size(), pygame.SRCALPHA)
                for i in range(10):
                    alpha = int(150 * (1 - i/10))  # Increased alpha for better visibility
                    color = (255, 0, 0, alpha)
                    glow_text = game_font.render("Critical Thoughts Attack!", True, color)
                    screen.blit(glow_text, (text_rect.x - i, text_rect.y))
                screen.blit(attack_text, text_rect)
        
        # Draw rocks with enhanced effects
        for rock in battle_state.rocks:
            rock.draw(screen)
        
        # Draw flowers
        for flower in battle_state.flowers:
            flower.draw(screen)
            # Show "Compassion Attack" with enhanced readability
            if len(battle_state.flowers) > 0:
                attack_text = game_font.render("Compassion Attack!", True, (255, 192, 203))
                text_rect = attack_text.get_rect(centerx=WIDTH//2, bottom=HEIGHT-50)
                
                # Draw text background
                bg_rect = text_rect.copy()
                bg_rect.inflate_ip(20, 10)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                
                # Add glow effect
                glow_surface = pygame.Surface(attack_text.get_size(), pygame.SRCALPHA)
                for i in range(10):
                    alpha = int(150 * (1 - i/10))  # Increased alpha for better visibility
                    color = (255, 192, 203, alpha)
                    glow_text = game_font.render("Compassion Attack!", True, color)
                    screen.blit(glow_text, (text_rect.x - i, text_rect.y))
                screen.blit(attack_text, text_rect)
        
        # Draw boat with wave effect
        boat_y_offset = math.sin(battle_animation_time * 2) * 5
        rotated_boat = pygame.transform.rotate(boat_image, 
                                            math.sin(battle_animation_time) * 5)
        boat_rect = rotated_boat.get_rect(center=(battle_state.boat_x, 
                                                 battle_state.boat_y + boat_y_offset))
        screen.blit(rotated_boat, boat_rect)
        
        # Draw health bars
        draw_battle_ui(battle_state)
    
    elif battle_state.state == BATTLE_STATE_WIN:
        text = title_font.render("You defeated the Inner Voice Monster!", True, GOLD)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)
        
        text = game_font.render("Press ESC to continue your journey", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        screen.blit(text, text_rect)
        
        # Set game as won
        game_state = GAME_STATE_WINNER
    
    elif battle_state.state == BATTLE_STATE_LOSE:
        text = title_font.render("The Monster overwhelmed you...", True, RED)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)
        
        text = game_font.render("Press ESC to return to your journey", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        screen.blit(text, text_rect)
        
        # Reset player's cards
        player_card_counts[current_player] = {'reflection': 0, 'coping': 0}
        collected_cards[current_player] = {'reflection': [], 'coping': []}

def draw_octopus(x, y, size):
    """Draw the octopus monster with enhanced graphics"""
    # Draw glowing effect
    glow_radius = size * 0.6 + math.sin(battle_animation_time * 0.1) * 10
    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    for r in range(int(glow_radius), 0, -2):
        alpha = int(100 * (r / glow_radius))
        pygame.draw.circle(glow_surface, (128, 0, 128, alpha), 
                         (glow_radius, glow_radius), r)
    screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

    # Draw tentacles with gradient and wave effect
    for i in range(8):  # Increased number of tentacles
        angle = i * 45 + math.sin(battle_animation_time * 0.1) * 20
        length = size * 1.2  # Longer tentacles
        
        # Create multiple segments for each tentacle
        points = []
        segments = 8  # More segments for smoother tentacles
        for j in range(segments + 1):
            progress = j / segments
            segment_length = length * progress
            wave_offset = math.sin(battle_animation_time * 0.2 + progress * 4) * (size * 0.2)
            
            segment_x = x + math.cos(math.radians(angle)) * segment_length
            segment_y = y + math.sin(math.radians(angle)) * segment_length
            
            # Add wave motion
            segment_x += math.cos(math.radians(angle + 90)) * wave_offset
            segment_y += math.sin(math.radians(angle + 90)) * wave_offset
            
            points.append((segment_x, segment_y))
        
        # Draw tentacle with gradient
        if len(points) >= 2:
            for k in range(len(points) - 1):
                progress = k / (len(points) - 1)
                thickness = int((1 - progress) * size * 0.2)
                color = (
                    128 + int(progress * 40),
                    0,
                    128 + int(progress * 40),
                )
                pygame.draw.line(screen, color, points[k], points[k + 1], thickness)

    # Draw body with gradient
    body_radius = int(size * 0.5)
    body_surface = pygame.Surface((body_radius * 2, body_radius * 2), pygame.SRCALPHA)
    for r in range(body_radius, 0, -1):
        progress = r / body_radius
        color = (
            128 + int((1 - progress) * 40),
            0,
            128 + int((1 - progress) * 40),
            255
        )
        pygame.draw.circle(body_surface, color, (body_radius, body_radius), r)
    screen.blit(body_surface, (x - body_radius, y - body_radius))

    # Draw eyes with glow
    eye_size = size * 0.15
    eye_offset = size * 0.2
    
    # Draw eye glow
    for eye_x in [x - eye_offset, x + eye_offset]:
        glow_size = eye_size * 1.5
        eye_glow = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
        for r in range(int(glow_size), 0, -1):
            alpha = int(100 * (r / glow_size))
            pygame.draw.circle(eye_glow, (255, 0, 0, alpha), 
                             (glow_size, glow_size), r)
        screen.blit(eye_glow, (eye_x - glow_size, y - glow_size))
    
    # Draw main eyes
    for eye_x in [x - eye_offset, x + eye_offset]:
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(y)), int(eye_size))
        pygame.draw.circle(screen, (255, 0, 0), (int(eye_x), int(y)), int(eye_size * 0.6))
        pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(y)), int(eye_size * 0.3))
        # Add highlight
        pygame.draw.circle(screen, (255, 255, 255), 
                         (int(eye_x - eye_size * 0.2), int(y - eye_size * 0.2)), 
                         int(eye_size * 0.1))

def draw_battle_ui(battle_state):
    """Draw the battle UI including health bars and instructions"""
    # Draw boat health
    health_width = 200
    health_height = 20
    health_x = 20
    health_y = 20
    
    pygame.draw.rect(screen, (64, 64, 64), (health_x, health_y, health_width, health_height))
    health_percent = battle_state.boat_health / BOAT_STARTING_HEALTH
    pygame.draw.rect(screen, (0, 255, 0), 
                    (health_x, health_y, health_width * health_percent, health_height))
    
    # Draw monster health
    monster_health_x = WIDTH - health_width - 20
    pygame.draw.rect(screen, (64, 64, 64), 
                    (monster_health_x, health_y, health_width, health_height))
    monster_health_percent = battle_state.monster_health / MONSTER_HITS_TO_WIN
    pygame.draw.rect(screen, (255, 0, 0), 
                    (monster_health_x, health_y, health_width * monster_health_percent, 
                     health_height))
    
    # Draw instructions
    instructions = [
        "← → : Move boat",
        "SPACE : Launch compassion flower",
        "ESC : Retreat"
    ]
    
    y = HEIGHT - 100
    for instruction in instructions:
        text = instruction_font.render(instruction, True, WHITE)
        text_rect = text.get_rect(left=20, top=y)
        screen.blit(text, text_rect)
        y += 25

# Initialize battle button
battle_button = BattleButton()

# Start background music when game starts
if background_music is not None:
    background_music.play(-1)

while running:
    # Store the close button rect for click detection
    close_button_rect = None
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Get the current close button rect
                close_button_rect = draw_close_button()
                if close_button_rect and close_button_rect.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()
                
                # Handle battle button click
                if game_state == GAME_STATE_PLAYING and battle_button.rect.collidepoint(event.pos):
                    game_state = GAME_STATE_BATTLE
                    battle_messages = ["The battle begins!",
                                    f"You have {player_card_counts[current_player]['reflection']} reflection cards",
                                    f"and {player_card_counts[current_player]['coping']} coping cards"]
                
                # Handle card selection in exchange state
                if EXCHANGE_STATE == 'selecting' and isinstance(centered_card, ExchangeInterface):
                    for i, card in enumerate(centered_card.cards):
                        if card['rect'].collidepoint(event.pos):
                            centered_card.selected_index = i
                            break
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Add music toggle with 'M' key
                toggle_music()
            
            if game_state == GAME_STATE_MENU:
                if event.key == pygame.K_1:
                    play_sound(collect_card_sound)
                    num_players = 1
                    game_state = GAME_STATE_PLAYING
                elif event.key == pygame.K_2:
                    play_sound(collect_card_sound)
                    num_players = 2
                    game_state = GAME_STATE_PLAYING
            
            elif game_state == GAME_STATE_PLAYING and event.key == pygame.K_SPACE:
                if waiting_for_card_interaction or EXCHANGE_STATE == 'moving':
                    handle_card_interaction(event)
                elif can_roll:
                    play_sound(dice_roll_sound)
                    current_roll = roll_dice()
                    can_roll = False
                    waiting_for_card_interaction, card_type = move_boat(current_roll)
                    
                    if check_boats_meeting():
                        waiting_for_card_interaction = True
                        EXCHANGE_STATE = 'selecting'
                        centered_card = ExchangeInterface(player_card_counts)
                    elif waiting_for_card_interaction and current_card_symbol:
                        centered_card = CenteredCard(current_card_symbol, card_type)
                    else:
                        can_roll = True
            
            elif game_state == GAME_STATE_BATTLE:
                if event.key == pygame.K_ESCAPE:
                    game_state = GAME_STATE_PLAYING
                    battle_state = None
                elif event.key == pygame.K_SPACE and battle_state and battle_state.state == BATTLE_STATE_FIGHTING:
                    # Launch compassion flower
                    battle_state.flowers.append(CompassionFlower(battle_state.boat_x, battle_state.boat_y - boat_size//2))
    
    # Draw current game state
    if game_state == GAME_STATE_MENU:
        draw_menu()
    elif game_state == GAME_STATE_BATTLE:
        if battle_state:
            battle_state.update()
        draw_battle_screen()
    else:
        draw_game_state()
        battle_button.update(pygame.mouse.get_pos())
        battle_button.draw(screen)
        
        if waiting_for_card_interaction and centered_card:
            centered_card.update()
            centered_card.draw(screen)
        
        # Update and draw card animations
        if animation_cards:
            for card in animation_cards[:]:
                card.update()
                card.draw(screen, pygame.font.Font(None, 20))
                if not card.moving:
                    animation_cards.remove(card)
    
    # Always draw the close button last so it's on top
    close_button_rect = draw_close_button()
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
if background_music is not None:
    background_music.stop()
mixer.quit()
sys.exit()  # Make sure the program exits completely