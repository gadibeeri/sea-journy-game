import asyncio
import pygame
import sys
import os
from main import *

async def web_main():
    try:
        # Declare globals
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
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(web_main()) 