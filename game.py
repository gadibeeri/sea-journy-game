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
WIDTH, HEIGHT = 900, 700
ROWS, COLS = 9, 9
HEX_SIZE = 40
BOARD_WIDTH = COLS * HEX_SIZE * 1.5
BOARD_HEIGHT = ROWS * HEX_SIZE * 1.732
BOARD_OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PARCHMENT = (255, 253, 208)
DARK_BLUE = (0, 0, 139)
LIGHT_GREEN = (144, 238, 144)
SEA_BLUE = (0, 119, 190)

# Game states
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_BATTLE = "battle"

# Battle states
BATTLE_STATE_INTRO = "intro"
BATTLE_STATE_FIGHTING = "fighting"
BATTLE_STATE_WON = "won"
BATTLE_STATE_LOST = "lost"

# Battle parameters
BOAT_BATTLE_SPEED = 5
ROCK_SPEED = 3
FLOWER_SPEED = 4
MONSTER_HITS_TO_WIN = 3
BOAT_HITS_TO_LOSE = 3

# Card sizes
CARD_WIDTH = 60
CARD_HEIGHT = 80
LARGE_CARD_SIZE = 120

# Initialize Pygame
pygame.init()
mixer.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sea Journey - Inner Voice Battle")

# Load assets
def load_image(filename):
    try:
        return pygame.image.load(os.path.join("assets", filename)).convert_alpha()
    except:
        print(f"Failed to load image: {filename}")
        return None

def load_sound(filename):
    try:
        return mixer.Sound(os.path.join("assets", filename))
    except:
        print(f"Failed to load sound: {filename}")
        return None

# Load images
boat_image = load_image("boat.png")
island_image = load_image("island.png")
octopus_image = load_image("octopus.png")
dice_image = load_image("dice.png")
card_back_image = load_image("card_back.png")

# Load sounds
collect_card_sound = load_sound("collect_card.wav")
dice_roll_sound = load_sound("dice_roll.wav")
background_music = load_sound("background_music.wav")

# Game variables
game_state = GAME_STATE_MENU
running = True
current_player = 0
can_roll = True
waiting_for_card_interaction = False
centered_card = None
animation_cards = []
battle_state = None
battle_messages = []
num_players = 1
current_roll = 1
current_card_symbol = None
EXCHANGE_STATE = 'none'

# Initialize player positions and card counts
player_positions = [(0, 0), (ROWS-1, COLS-1)]
player_card_counts = [
    {'reflection': 0, 'coping': 0},
    {'reflection': 0, 'coping': 0}
]

# Initialize board
board = [[None for _ in range(COLS)] for _ in range(ROWS)]
island_positions = []
octopus_positions = []

# Generate island positions
while len(island_positions) < 10:
    row = random.randint(0, ROWS-1)
    col = random.randint(0, COLS-1)
    if (row, col) not in island_positions and (row, col) not in player_positions:
        island_positions.append((row, col))
        board[row][col] = 'island'

# Generate octopus positions
while len(octopus_positions) < 10:
    row = random.randint(0, ROWS-1)
    col = random.randint(0, COLS-1)
    if (row, col) not in island_positions and (row, col) not in player_positions and (row, col) not in octopus_positions:
        octopus_positions.append((row, col))
        board[row][col] = 'octopus'

# Helper functions
def get_hex_center(row, col):
    x = BOARD_OFFSET_X + col * HEX_SIZE * 1.5
    y = BOARD_OFFSET_Y + row * HEX_SIZE * 1.732
    if col % 2 == 1:
        y += HEX_SIZE * 0.866
    return x, y

def draw_hexagon(x, y, size, color):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.append((px, py))
    pygame.draw.polygon(screen, color, points)

def draw_boat_with_animation(x, y, boat_image, offset):
    if boat_image:
        boat_size = int(HEX_SIZE * 0.8)
        scaled_boat = pygame.transform.scale(boat_image, (boat_size, boat_size))
        screen.blit(scaled_boat, (x - boat_size//2 + offset, y - boat_size//2))

def draw_card(surface, rect, color, symbol=None, text=None, selected=False):
    # Draw card background
    pygame.draw.rect(surface, color, rect, border_radius=10)
    
    # Draw border
    border_color = (255, 255, 255) if selected else (200, 200, 200)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)
    
    if symbol:
        # Draw symbol
        symbol_font = pygame.font.Font(None, 40)
        symbol_text = symbol_font.render(symbol, True, (255, 255, 255))
        symbol_rect = symbol_text.get_rect(center=rect.center)
        surface.blit(symbol_text, symbol_rect)
    
    if text:
        # Draw text
        text_font = pygame.font.Font(None, 20)
        text_surface = text_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.bottom - 20))
        surface.blit(text_surface, text_rect)

def draw_button(surface, rect, text, color, hover=False):
    # Draw button background
    pygame.draw.rect(surface, color, rect, border_radius=10)
    
    # Draw border
    border_color = (255, 255, 255) if hover else (200, 200, 200)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)
    
    # Draw text
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_dice(value):
    if dice_image:
        dice_size = int(HEX_SIZE * 0.8)
        scaled_dice = pygame.transform.scale(dice_image, (dice_size, dice_size))
        screen.blit(scaled_dice, (WIDTH - dice_size - 20, 20))
        
        # Draw value
        font = pygame.font.Font(None, 36)
        text = font.render(str(value), True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH - dice_size//2, 20 + dice_size//2))
        screen.blit(text, text_rect)

def roll_dice():
    return random.randint(1, 6)

def draw_card_stacks(screen):
    # Draw reflection cards
    reflection_count = player_card_counts[current_player]['reflection']
    for i in range(reflection_count):
        x = 20 + i * 10
        y = HEIGHT - 100
        draw_card(screen, pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), PURPLE, "R")
    
    # Draw coping cards
    coping_count = player_card_counts[current_player]['coping']
    for i in range(coping_count):
        x = 20 + i * 10
        y = HEIGHT - 180
        draw_card(screen, pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), ORANGE, "C")

def check_collisions():
    global current_card_symbol, waiting_for_card_interaction
    row, col = player_positions[current_player]
    
    # Check for island collision
    if (row, col) in island_positions:
        current_card_symbol = "🏝️"
        waiting_for_card_interaction = True
        return True
    
    # Check for octopus collision
    if (row, col) in octopus_positions:
        current_card_symbol = "🐙"
        waiting_for_card_interaction = True
        return True
    
    return False

def move_boat(steps):
    global current_card_symbol, waiting_for_card_interaction
    row, col = player_positions[current_player]
    
    # Move the boat
    for _ in range(steps):
        if col % 2 == 0:  # Even column
            if row > 0:
                row -= 1
        else:  # Odd column
            if row > 0:
                row -= 1
                col += 1
        
        if col < COLS - 1:
            col += 1
    
    player_positions[current_player] = (row, col)
    
    # Check for collisions
    if check_collisions():
        return True, board[row][col]
    
    return False, None

def draw_close_button():
    button_rect = pygame.Rect(WIDTH - 40, 10, 30, 30)
    pygame.draw.rect(screen, RED, button_rect)
    pygame.draw.line(screen, WHITE, (WIDTH - 35, 15), (WIDTH - 15, 25), 2)
    pygame.draw.line(screen, WHITE, (WIDTH - 35, 25), (WIDTH - 15, 15), 2)
    return button_rect

def draw_game_state():
    # Fill screen with background color
    screen.fill(SEA_BLUE)
    
    # Draw hex grid
    for row in range(ROWS):
        for col in range(COLS):
            x, y = get_hex_center(row, col)
            color = LIGHT_GREEN if (row, col) in island_positions else SEA_BLUE
            draw_hexagon(x, y, HEX_SIZE, color)
    
    # Draw islands and octopuses
    for row, col in island_positions:
        x, y = get_hex_center(row, col)
        if island_image:
            island_size = int(HEX_SIZE * 0.8)
            scaled_island = pygame.transform.scale(island_image, (island_size, island_size))
            screen.blit(scaled_island, (x - island_size//2, y - island_size//2))
    
    for row, col in octopus_positions:
        x, y = get_hex_center(row, col)
        if octopus_image:
            octopus_size = int(HEX_SIZE * 0.8)
            scaled_octopus = pygame.transform.scale(octopus_image, (octopus_size, octopus_size))
            screen.blit(scaled_octopus, (x - octopus_size//2, y - octopus_size//2))
    
    # Draw boats
    for i, (row, col) in enumerate(player_positions):
        x, y = get_hex_center(row, col)
        offset = 10 if i == 0 else -10
        draw_boat_with_animation(x, y, boat_image, offset)
    
    # Draw dice
    draw_dice(current_roll)
    
    # Draw card stacks
    draw_card_stacks(screen)
    
    # Draw current player indicator
    font = pygame.font.Font(None, 36)
    text = font.render(f"Player {current_player + 1}'s Turn", True, WHITE)
    screen.blit(text, (20, 20))

def draw_menu():
    # Fill with parchment color
    screen.fill(PARCHMENT)
    
    # Draw title
    font = pygame.font.Font(None, 74)
    title = font.render("Sea Journey", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
    screen.blit(title, title_rect)
    
    # Draw subtitle
    subtitle_font = pygame.font.Font(None, 36)
    subtitle = subtitle_font.render("Inner Voice Battle", True, DARK_BLUE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//3 + 50))
    screen.blit(subtitle, subtitle_rect)
    
    # Draw player selection buttons
    button_width = 200
    button_height = 50
    button_y = HEIGHT//2
    
    # One player button
    one_player_rect = pygame.Rect(WIDTH//2 - button_width - 20, button_y, button_width, button_height)
    draw_button(screen, one_player_rect, "1 Player", BLUE)
    
    # Two players button
    two_player_rect = pygame.Rect(WIDTH//2 + 20, button_y, button_width, button_height)
    draw_button(screen, two_player_rect, "2 Players", BLUE)
    
    # Draw instructions
    instructions_font = pygame.font.Font(None, 24)
    instructions = [
        "Press 1 for One Player",
        "Press 2 for Two Players",
        "Press M to toggle music"
    ]
    
    for i, text in enumerate(instructions):
        instruction = instructions_font.render(text, True, DARK_BLUE)
        instruction_rect = instruction.get_rect(center=(WIDTH//2, HEIGHT//2 + 100 + i*30))
        screen.blit(instruction, instruction_rect)

def check_boats_meeting():
    return player_positions[0] == player_positions[1]

def check_winner():
    for i in range(num_players):
        if player_card_counts[i]['reflection'] >= 3 and player_card_counts[i]['coping'] >= 3:
            return i
    return None

def handle_card_interaction(event):
    global waiting_for_card_interaction, current_card_symbol, EXCHANGE_STATE
    if event.key == pygame.K_SPACE:
        if waiting_for_card_interaction:
            if current_card_symbol == "🏝️":
                player_card_counts[current_player]['reflection'] += 1
            elif current_card_symbol == "🐙":
                player_card_counts[current_player]['coping'] += 1
            waiting_for_card_interaction = False
            current_card_symbol = None
        elif EXCHANGE_STATE == 'moving':
            EXCHANGE_STATE = 'none'

class BattleState:
    def __init__(self):
        self.state = BATTLE_STATE_INTRO
        self.animation_time = 0
        self.monster_x = WIDTH // 2
        self.monster_y = 100
        self.boat_x = WIDTH // 2
        self.boat_y = HEIGHT - 100
        self.monster_health = MONSTER_HITS_TO_WIN
        self.boat_health = BOAT_HITS_TO_LOSE
        self.rocks = []
        self.flowers = []
        self.monster_move_timer = 0
        self.rock_spawn_timer = 0
        self.monster_direction = 1

    def update(self):
        if self.state == BATTLE_STATE_INTRO:
            self.animation_time += 1
            if self.animation_time > 60:  # After 1 second
                self.state = BATTLE_STATE_FIGHTING
                self.animation_time = 0
        
        elif self.state == BATTLE_STATE_FIGHTING:
            # Update monster movement
            self.monster_move_timer += 1
            if self.monster_move_timer >= 30:  # Move every half second
                self.monster_move_timer = 0
                self.monster_direction = random.choice([-1, 1])
                self.monster_x = max(100, min(WIDTH - 100, self.monster_x + self.monster_direction * 50))
            
            # Spawn rocks periodically
            self.rock_spawn_timer += 1
            if self.rock_spawn_timer >= 120:  # Spawn rocks every 2 seconds
                self.rock_spawn_timer = 0
                num_rocks = random.randint(1, 3)
                for _ in range(num_rocks):  # Spawn multiple rocks
                    rock_x = self.monster_x + random.randint(-50, 50)
                    self.rocks.append(Rock(rock_x, self.monster_y + 50))
            
            # Update rocks
            for rock in self.rocks[:]:
                rock.update()
                if rock.y > HEIGHT:
                    self.rocks.remove(rock)
                # Check collision with boat
                if abs(rock.x - self.boat_x) < 30 and abs(rock.y - self.boat_y) < 30:
                    self.boat_health -= 1
                    self.rocks.remove(rock)
                    if self.boat_health <= 0:
                        self.state = BATTLE_STATE_LOST
            
            # Update flowers
            for flower in self.flowers[:]:
                flower.update()
                if flower.y < 0:
                    self.flowers.remove(flower)
                # Check collision with monster
                if abs(flower.x - self.monster_x) < 40 and abs(flower.y - self.monster_y) < 40:
                    self.monster_health -= 1
                    self.flowers.remove(flower)
                    if self.monster_health <= 0:
                        self.state = BATTLE_STATE_WON

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = ROCK_SPEED

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (139, 69, 19), (int(self.x), int(self.y)), 10)

class CompassionFlower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = FLOWER_SPEED

    def update(self):
        self.y -= self.speed

    def draw(self, screen):
        # Draw flower petals
        for i in range(8):
            angle = math.pi / 4 * i
            petal_x = self.x + math.cos(angle) * 15
            petal_y = self.y + math.sin(angle) * 15
            pygame.draw.circle(screen, (255, 192, 203), (int(petal_x), int(petal_y)), 8)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)

class BattleButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 200, 20, 180, 40)
        self.hover = False

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = (200, 0, 0) if self.hover else (255, 0, 0)
        draw_button(screen, self.rect, "Inner Voice Monster", color, self.hover)

def draw_battle_screen():
    # Fill screen with dark blue
    screen.fill(DARK_BLUE)
    
    # Draw animated waves
    for i in range(5):
        wave_y = HEIGHT - 100 + i * 20
        for x in range(0, WIDTH, 40):
            pygame.draw.circle(screen, (0, 100, 255), (x, wave_y), 20)
    
    # Draw monster
    if battle_state:
        draw_octopus(battle_state.monster_x, battle_state.monster_y, 60)
        
        # Draw boat
        boat_size = 40
        screen.blit(pygame.transform.scale(boat_image, (boat_size, boat_size)),
                   (battle_state.boat_x - boat_size//2, battle_state.boat_y - boat_size//2))
        
        # Draw rocks and flowers
        for rock in battle_state.rocks:
            rock.draw(screen)
        for flower in battle_state.flowers:
            flower.draw(screen)
        
        # Draw battle UI
        draw_battle_ui(battle_state)
        
        # Draw battle messages
        if battle_state.state == BATTLE_STATE_INTRO:
            font = pygame.font.Font(None, 36)
            text = font.render("The battle begins!", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        elif battle_state.state == BATTLE_STATE_WON:
            font = pygame.font.Font(None, 48)
            text = font.render("You won the battle!", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            text = font.render("Press ESC to continue", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 50))
        elif battle_state.state == BATTLE_STATE_LOST:
            font = pygame.font.Font(None, 48)
            text = font.render("You lost the battle!", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            text = font.render("Press ESC to continue", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 50))

def draw_octopus(x, y, size):
    # Draw body
    pygame.draw.circle(screen, (128, 0, 128), (int(x), int(y)), size//2)
    
    # Draw tentacles
    for i in range(8):
        angle = math.pi / 4 * i
        tentacle_x = x + math.cos(angle) * size
        tentacle_y = y + math.sin(angle) * size
        pygame.draw.line(screen, (128, 0, 128), (x, y), (tentacle_x, tentacle_y), 10)
    
    # Draw eyes
    eye_size = size//4
    pygame.draw.circle(screen, WHITE, (int(x - size//4), int(y - size//4)), eye_size)
    pygame.draw.circle(screen, WHITE, (int(x + size//4), int(y - size//4)), eye_size)
    pygame.draw.circle(screen, BLACK, (int(x - size//4), int(y - size//4)), eye_size//2)
    pygame.draw.circle(screen, BLACK, (int(x + size//4), int(y - size//4)), eye_size//2)

def draw_battle_ui(battle_state):
    # Draw health bars
    bar_width = 200
    bar_height = 20
    bar_y = 20
    
    # Monster health
    pygame.draw.rect(screen, RED, (20, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (20, bar_y, bar_width * (battle_state.monster_health / MONSTER_HITS_TO_WIN), bar_height))
    
    # Boat health
    pygame.draw.rect(screen, RED, (20, bar_y + 30, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (20, bar_y + 30, bar_width * (battle_state.boat_health / BOAT_HITS_TO_LOSE), bar_height))
    
    # Draw instructions
    font = pygame.font.Font(None, 24)
    instructions = [
        "Use LEFT/RIGHT arrows to move",
        "Press SPACE to shoot flowers",
        "Press ESC to return to game"
    ]
    
    for i, text in enumerate(instructions):
        instruction = font.render(text, True, WHITE)
        screen.blit(instruction, (20, bar_y + 70 + i*25))

async def main():
    global game_state, running, battle_button, background_music
    global current_player, can_roll, waiting_for_card_interaction
    global centered_card, animation_cards, battle_state, battle_messages
    global num_players, current_roll, current_card_symbol, EXCHANGE_STATE
    
    # Initialize Pygame
    pygame.init()
    print("Pygame initialized successfully")
    
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sea Journey - Inner Voice Battle")
    print(f"Display set up with size: {WIDTH}x{HEIGHT}")
    
    # Initialize game state variables
    game_state = GAME_STATE_MENU
    running = True
    battle_button = BattleButton()
    current_player = 0
    can_roll = True
    waiting_for_card_interaction = False
    centered_card = None
    animation_cards = []
    battle_state = None
    battle_messages = []
    num_players = 1
    current_roll = 1
    current_card_symbol = None
    EXCHANGE_STATE = 'none'
    
    print("Game variables initialized")
    
    # Initialize background music
    try:
        if background_music is not None:
            background_music.play(-1)
            print("Background music started")
    except Exception as e:
        print(f"Music error: {str(e)}")
    
    clock = pygame.time.Clock()
    
    while running:
        try:
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
            
            # Fill screen with background color
            screen.fill((200, 200, 200))  # Light gray background
            
            # Draw current game state
            if game_state == GAME_STATE_MENU:
                draw_menu()
                print("Drawing menu")
            elif game_state == GAME_STATE_BATTLE:
                if battle_state:
                    battle_state.update()
                draw_battle_screen()
                print("Drawing battle screen")
            else:
                draw_game_state()
                battle_button.update(pygame.mouse.get_pos())
                battle_button.draw(screen)
                print("Drawing game state")
                
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
            clock.tick(60)  # Limit to 60 FPS
            
            await asyncio.sleep(0)  # Required for web compatibility
            
        except Exception as e:
            print(f"Error in game loop: {str(e)}")
            import traceback
            traceback.print_exc()
    
    pygame.quit()
    if background_music is not None:
        background_music.stop()
    mixer.quit()

if __name__ == '__main__':
    asyncio.run(main()) 