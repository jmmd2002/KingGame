"""
Test: Full Game - Monte Carlo AI vs 3 Heuristic AIs
Play complete games with all round types:
- vazas, copas, homens, mulheres, king, last
- festa1 (POSITIVOS), festa2 (NULOS), festa3 (POSITIVOS), festa4 (NULOS)

Festa configuration:
- festa1,3: POSITIVOS with random starter and dynamic trump (starter's most common suit)
- festa2,4: NULOS with random starter
"""

import random
from game import Game
from mc_ai_player import MonteCarloAI
from ai_player import AIPlayer
from deck import Suit


def get_most_common_suit(hand):
    """Get the suit with most cards in hand"""
    suit_counts = {suit: 0 for suit in Suit}
    for card in hand:
        suit_counts[card.suit] += 1
    return max(suit_counts, key=suit_counts.get)


def run_full_game(num_games=3):
    """
    Run multiple complete games with all round types
    - Player 0: Monte Carlo AI
    - Players 1-3: Heuristic AIs
    
    All rounds are played (no filtering)
    """
    
    players = ["MC-AI", "Heuristic-1", "Heuristic-2", "Heuristic-3"]
    cumulative_scores = {i: 0 for i in range(4)}
    game_results = []
    
    print("=" * 80)
    print("FULL GAME TEST - MC-AI vs 3 HEURISTIC AIs")
    print("All rounds: vazas, copas, homens, mulheres, king, last, festa1-4")
    print("=" * 80)
    print(f"Running {num_games} games...\n")
    
    for game_num in range(num_games):
        print(f"\nGame {game_num + 1}/{num_games}:")
        print("-" * 80)
        
        game = Game(players)
        
        # Track rounds played
        ai_players = {}
        rounds_played = 0
        round_scores = []
        
        while not game.is_game_over():
            round_type = game.get_current_round_type()
            
            # Handle festa rounds specially
            if round_type.startswith("festa"):
                festa_num = int(round_type[-1])
                is_positivos = (festa_num in [1, 3])
                
                # Random starting player
                starting_player = random.randint(0, 3)
                
                # Get trump suit for positivos
                starting_hand = game.get_player_hand(starting_player)
                trump_suit = get_most_common_suit(starting_hand) if is_positivos else None
                
                # Configure festa
                if is_positivos:
                    game.set_festa_config(round_type, starter=starting_player, is_nulos=False, trump_suit=trump_suit)
                else:
                    game.set_festa_config(round_type, starter=starting_player, is_nulos=True, trump_suit=None)
                
                # Create AI players for festa
                for i in range(4):
                    if i == 0:
                        ai_players[i] = MonteCarloAI(i, round_type, num_simulations=50, trump_suit=trump_suit, is_nulos=(not is_positivos))
                    else:
                        ai_players[i] = AIPlayer(game.get_player_hand(i), round_type, is_nulos=(not is_positivos))
            else:
                # Non-festa rounds
                for i in range(4):
                    if i == 0:
                        ai_players[i] = MonteCarloAI(i, round_type, num_simulations=50)
                    else:
                        ai_players[i] = AIPlayer(game.get_player_hand(i), round_type)
            
            # Check if round can be played
            if not game.can_play_round():
                print(f"  {round_type.upper():10} - SKIPPED")
                game.skip_round()
                continue
            
            # Play round
            print(f"  {round_type.upper():10} - ", end="", flush=True)
            
            while not game.is_round_over():
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
                        ai_players[player_idx].hand = hand
                        card = ai_players[player_idx].choose_card(valid_plays, game.current_round.current_vaza)
                    
                    # Add card to current vaza
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
            round_scores.append((round_type, points))
            
            print(f"Points: {points}")
            rounds_played += 1
            
            game.advance_to_next_round()
        
        # Game over
        print(f"\n  Round-by-round results:")
        print(f"  {'-' * 76}")
        print(f"  {'Round':<12} {'MC-AI':>10} {'Heur-1':>10} {'Heur-2':>10} {'Heur-3':>10}")
        print(f"  {'-' * 76}")
        
        for round_name, points in round_scores:
            print(f"  {round_name:<12} {points[0]:>10} {points[1]:>10} {points[2]:>10} {points[3]:>10}")
        
        print(f"\n  Final standings ({rounds_played} rounds played):")
        for i, player in enumerate(players):
            pts = game.cumulative_points[i]
            print(f"    {player:20} - {pts:4d} points")
            cumulative_scores[i] += pts
        
        game_results.append({
            'game': game_num + 1,
            'scores': game.cumulative_points.copy(),
            'rounds': rounds_played
        })
        print()
    
    # Summary across all games
    print("\n" + "=" * 80)
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
    print(f"Win Rate: {sum(1 for g in game_results if g['scores'][0] > sum(g['scores'][1:4])/3) * 100 // num_games}%")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n\n")
    print("#" * 80)
    print("# FULL GAME TEST - ALL ROUNDS WITH MID-VAZA STATE PRESERVATION")
    print("#" * 80 + "\n")
    
    run_full_game(num_games=3)
