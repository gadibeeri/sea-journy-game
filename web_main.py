import asyncio
import pygame
import sys
from main import *

async def web_main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sea Journey - Inner Voice Battle")
    
    # Initialize game state variables
    game_state = GAME_STATE_MENU
    running = True
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
        await asyncio.sleep(0)  # Required for web compatibility
    
    pygame.quit()
    if background_music is not None:
        background_music.stop()
    mixer.quit()

if __name__ == '__main__':
    asyncio.run(web_main()) 