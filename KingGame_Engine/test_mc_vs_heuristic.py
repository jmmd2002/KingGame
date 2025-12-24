"""
Test: Monte Carlo AI vs 3 Heuristic AIs
Compare performance over multiple games
"""

from game import Game
from mc_ai_player import MonteCarloAI
from ai_player import AIPlayer


def run_comparison_game(num_games=5):
    """
    Run multiple games with:
    - Player 0: Monte Carlo AI
    - Players 1-3: Heuristic AIs
    
    Track cumulative points for each player
    """
    
    players = ["MC-AI", "Heuristic-1", "Heuristic-2", "Heuristic-3"]
    cumulative_scores = {i: 0 for i in range(4)}
    game_results = []
    
    print("=" * 80)
    print("MC-AI vs 3 HEURISTIC AIs - COMPARISON TEST")
    print("=" * 80)
    print(f"Running {num_games} games...\n")
    
    for game_num in range(num_games):
        print(f"Game {game_num + 1}/{num_games}:")
        print("-" * 80)
        
        game = Game(players)
        
        # Create AI players
        ai_players = {}
        
        while not game.is_game_over():
            round_type = game.get_current_round_type()
            
            # Create/update AI players for this round
            # Get festa configuration if applicable
            trump_suit = None
            is_nulos = None
            if round_type in ["festa1", "festa2", "festa3", "festa4"]:
                is_nulos_mode = game.festa_modes.get(round_type, 1)  # Default to nulos
                is_nulos = (is_nulos_mode == 1)
                if not is_nulos:
                    # Positivos - get trump suit
                    festa_num = int(round_type[-1]) - 1  # festa1->0, festa2->1, etc
                    trump_suit = game.festa_trump_suits.get(festa_num)
            
            for i in range(4):
                if i == 0:
                    # MC AI with trump_suit and is_nulos for festa
                    ai_players[i] = MonteCarloAI(i, round_type, num_simulations=50, trump_suit=trump_suit, is_nulos=is_nulos)
                else:
                    # Heuristic AI with is_nulos for festa
                    ai_players[i] = AIPlayer(game.get_player_hand(i), round_type, is_nulos=is_nulos)
            
            # Check if round can be played
            if not game.can_play_round():
                print(f"  {round_type.upper():10} - SKIPPED")
                game.skip_round()
                continue
            
            # Play round
            print(f"  {round_type.upper():10} - ", end="")
            vaza_num = 0
            
            while not game.is_round_over():
                vaza_num += 1
                info = game.get_next_vaza_info()
                
                # Start vaza
                game.current_round.start_vaza()
                
                # Get card choices
                card_plays = []
                for player_idx in info['play_order']:
                    hand = game.get_player_hand(player_idx)
                    valid_plays = game.get_valid_plays(player_idx)
                    
                    # Collect cards played so far this round
                    cards_played_this_round = []
                    for card_list in game.current_round.cards_won:
                        cards_played_this_round.extend(card_list)
                    
                    if player_idx == 0:
                        # MC AI decides
                        card = ai_players[player_idx].choose_card(
                            my_hand=hand,
                            valid_plays=valid_plays,
                            cards_played_this_round=cards_played_this_round,
                            current_vaza=game.current_round.current_vaza
                        )
                    else:
                        # Heuristic AI decides
                        # Update heuristic AI hand
                        ai_players[player_idx].hand = hand
                        card = ai_players[player_idx].choose_card(valid_plays, game.current_round.current_vaza)
                    
                    # Add card to current vaza for next player to see
                    game.current_round.current_vaza.cards_played.append(card)
                    game.current_round.current_vaza.play_order.append(player_idx)
                    if game.current_round.current_vaza.main_suit is None:
                        game.current_round.current_vaza.main_suit = card.suit
                    
                    card_plays.append((player_idx, card))
                
                # Play vaza
                game.play_vaza(card_plays)
            
            # Round over - get results
            results = game.get_current_round_results()
            points = results['points']
            print(f"  {points}")
            
            game.advance_to_next_round()
        
        # Game over - get final standings
        print(f"\n  Final standings:")
        for i, player in enumerate(players):
            pts = game.cumulative_points[i]
            print(f"    {player:20} - {pts:4d} points")
            cumulative_scores[i] += pts
        
        game_results.append({
            'game': game_num + 1,
            'scores': game.cumulative_points.copy()
        })
        print()
    
    # Summary across all games
    print("=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    print(f"\nAveraged over {num_games} games:\n")
    
    avg_scores = {}
    for i, player in enumerate(players):
        total = cumulative_scores[i]
        avg = total / num_games
        avg_scores[i] = avg
        print(f"{player:20} - Total: {total:5d} pts  |  Avg: {avg:7.1f} pts/game")
    
    # Rank them
    print("\nRankings (best to worst):")
    sorted_players = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
    for rank, (player_idx, avg_score) in enumerate(sorted_players, 1):
        print(f"  {rank}. {players[player_idx]:20} - {avg_score:7.1f} avg pts/game")
    
    # Show MC-AI advantage
    mc_score = avg_scores[0]
    heuristic_avg = sum(avg_scores[i] for i in range(1, 4)) / 3
    advantage = mc_score - heuristic_avg
    
    print(f"\nMC-AI Advantage: {advantage:+.1f} points vs average heuristic AI")
    
    print("=" * 80)


if __name__ == "__main__":
    run_comparison_game(num_games=10)
