"""
Test script: All AI players (no human input needed)
"""

from game import Game
from mc_ai_player import MonteCarloAI


def run_ai_game():
    """Run a full game with all AI players"""
    
    players = ["AI1", "AI2", "AI3", "AI4"]
    game = Game(players)
    
    print("=" * 80)
    print("KING GAME - ALL AI")
    print("=" * 80)
    print(f"Players: {', '.join(players)}\n")
    
    # Create AI players
    ai_players = {i: None for i in range(4)}
    
    while not game.is_game_over():
        round_type = game.get_current_round_type()
        
        # Create AI players for this round
        for i in range(4):
            ai_players[i] = MonteCarloAI(i, round_type, num_simulations=20)  # Fewer sims for speed
        
        # Check if round can be played
        if not game.can_play_round():
            print(f"\nROUND: {round_type.upper()} - SKIPPED")
            game.skip_round()
            continue
        
        print(f"\nROUND: {round_type.upper()}")
        print("-" * 80)
        
        vaza_num = 0
        
        while not game.is_round_over():
            vaza_num += 1
            info = game.get_next_vaza_info()
            
            # Start vaza
            game.current_round.start_vaza()
            
            print(f"  Vaza {vaza_num}: ", end="")
            
            # Get card choices from AI
            card_plays = []
            for player_idx in info['play_order']:
                hand = game.get_player_hand(player_idx)
                valid_plays = game.get_valid_plays(player_idx)
                
                # Collect cards played so far this round
                cards_played_this_round = []
                for card_list in game.current_round.cards_won:
                    cards_played_this_round.extend(card_list)
                
                # Silent AI decision (no verbose output)
                card = ai_players[player_idx].choose_card(
                    my_hand=hand,
                    valid_plays=valid_plays,
                    cards_played_this_round=cards_played_this_round,
                    current_vaza=game.current_round.current_vaza
                )
                
                # Add card to current vaza for next AI player to see
                game.current_round.current_vaza.cards_played.append(card)
                game.current_round.current_vaza.play_order.append(player_idx)
                if game.current_round.current_vaza.main_suit is None:
                    game.current_round.current_vaza.main_suit = card.suit
                
                card_plays.append((player_idx, card))
                print(f"{players[player_idx]}:{card} ", end="")
            
            # Play vaza
            winner = game.play_vaza(card_plays)
            print(f"-> Won by {players[winner]}")
        
        # Round over - show results
        print(f"\n{round_type.upper()} Results:")
        results = game.get_current_round_results()
        for i, player in enumerate(players):
            points = results['points'][i]
            print(f"  {player:10} {points:4d} pts")
        
        game.advance_to_next_round()
    
    # Game over
    print("\n" + "=" * 80)
    print("SEASON OVER!")
    print("=" * 80)
    
    standings = game.get_season_standings()
    
    # Sort by points
    sorted_players = sorted(
        zip(standings['players'], standings['cumulative_points']),
        key=lambda x: x[1],
        reverse=True
    )
    
    print("\nFINAL STANDINGS:\n")
    for i, (player, points) in enumerate(sorted_players, 1):
        print(f"{i}. {player:10} {points:4d} points")
    
    print("=" * 80)


if __name__ == "__main__":
    run_ai_game()
