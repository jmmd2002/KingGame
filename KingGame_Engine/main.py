"""
Real-life King Game Assistant
==============================

Use this when playing King with physical cards.
The program tracks game state and validates plays but doesn't show human player hands.
"""

from game_simulator import Round
from deck import Card
from mc_ai_player import MonteCarloAI
from game_player import GamePlayer
from game_display import GameDisplay

# Define the order of rounds in a King game
ROUND_ORDER = ["vazas", "copas", "homens", "mulheres", "king", "last"]


def setup_players() -> tuple[list[str], list[bool]]:
    """
    Let user choose player names and types (human vs AI).
    
    Returns
    -------
    tuple[list[str], list[bool]]
        Tuple containing (player_names, player_is_ai flags).
    """
    players = []
    player_is_ai = [False, False, False, False]
    
    GameDisplay.show_setup_header()
    
    for i in range(4):
        # Get player name
        default_name = f"Player {i+1}"
        name = input(f"Player {i+1} name [default: {default_name}]: ").strip()
        if not name:
            name = default_name
        players.append(name)
        
        # Get player type - human or ai
        choice = input(f"  {name} - (h)uman or (a)i? [default: human]: ").strip().lower()
        if choice == 'a':
            player_is_ai[i] = True
            print(f"  -> {name} will be AI\n")
        else:
            print(f"  -> {name} will be HUMAN (real player)\n")
    
    return players, player_is_ai


def start_game():
    """
    Play King with physical cards - track game state and validate plays.
    
    Main game loop that:
    - Sets up players
    - Plays through all rounds
    - Tracks scores
    - Displays final standings
    """
    # Get players - names and types (human vs AI)
    player_names, player_is_ai = setup_players()
    
    # Game state variables
    players: list[GamePlayer] = [GamePlayer(i, name, player_is_ai[i]) for i, name in enumerate(player_names)]
    cumulative_points = [0, 0, 0, 0]
    
    GameDisplay.show_game_header(player_names, player_is_ai)
    
    for round_type in ROUND_ORDER:
        # Create round
        current_round = Round(round_type, players)
        GameDisplay.show_round_header(round_type, GameDisplay.get_round_description(round_type))
        current_round.start() #starting player

        # Create AI players for this round
        ai_players: dict[int, MonteCarloAI] = {}
        ai_indices = [i for i in range(4) if players[i].is_ai]
        
        for idx, i in enumerate(ai_indices):
            ai_players[i] = MonteCarloAI(players[i], current_round,
                                        num_simulations=30)

        cards_played_round: list[Card] = []
        
        # Play all 13 vazas in this round
        for vaza_num in range(13):
            info = current_round.get_next_vaza_info()
            current_round.start_vaza()
            
            play_order_players = [players[p] for p in info['play_order']]
            GameDisplay.show_vaza_header(
                vaza_num + 1,
                players[info['starter']],
                play_order_players,
                len(cards_played_round)
            )
            
            for player_idx in info['play_order']:
                if players[player_idx].is_ai:
                    # AI player turn
                    ai_player = ai_players[player_idx]
                    valid_plays = current_round.get_valid_plays(ai_player.my_hand)
                    
                    if not valid_plays:
                        GameDisplay.show_ai_no_valid_plays(players[player_idx], ai_player.my_hand)
                        continue
                    
                    # Update hand estimates based on cards played in current vaza
                    ai_player.update_hand_estimates(current_round.current_vaza)
                    
                    card = ai_player.choose_card(
                        valid_plays=valid_plays,
                        current_vaza=current_round.current_vaza
                    )
                    
                    # Remove card from AI's hand after playing
                    ai_player.my_hand.remove(card)
                    
                    current_round.play_card(player_idx, card)
                    cards_played_round.append(card)
                    GameDisplay.show_ai_play(players[player_idx], card)
                
                else:
                    # Human player turn
                    GameDisplay.show_human_turn(
                        players[player_idx],
                        current_round.current_vaza.cards_played
                    )
                    
                    while True:
                        choice = input(f"  Which card did {players[player_idx].name} play? (or 'help'): ").strip()
                        
                        if choice.lower() == 'help':
                            GameDisplay.show_card_help()
                            continue
                        
                        card = Card.from_string(choice)
                        
                        if card is None:
                            GameDisplay.show_invalid_card_format()
                            continue
                        
                        if card in cards_played_round:
                            GameDisplay.show_card_already_played(card)
                            override = input(f"      Override and play anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                continue

                        current_round.play_card(player_idx, card)
                        cards_played_round.append(card)
                        GameDisplay.show_card_played(players[player_idx], card)
                        break
            
            # Determine winner
            winner = current_round.get_vaza_winner()
            GameDisplay.show_vaza_winner(players[winner], current_round.vazas_won, players)
            
            # Check if round can end early
            can_end, message = current_round.can_end_early(cards_played_round)
            if can_end:
                print(message)
                break  # Exit the vaza loop
            
            input("Press Enter for next vaza...")
            print()
        
        # Round over - show results
        points = current_round.calculate_points()
        details = [GameDisplay.get_round_detail(round_type, current_round, i) for i in range(4)]
        
        for i in range(4):
            cumulative_points[i] += points[i]
        
        GameDisplay.show_round_results(round_type, players, points, details, cumulative_points)
        input("\nPress Enter to advance to next round...")
    
    # Game over - show final standings
    GameDisplay.show_final_standings(player_names, cumulative_points)


if __name__ == "__main__":
    start_game()
