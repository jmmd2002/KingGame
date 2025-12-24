"""
Test: Monte Carlo AI vs 3 Heuristic AIs - Mixed Festa Rounds
Half positivos, half nulos with random starting players

Configuration:
- festa1: POSITIVOS mode, random starter, trump = starter's most common suit
- festa2: NULOS mode, random starter
- festa3: POSITIVOS mode, random starter, trump = starter's most common suit
- festa4: NULOS mode, random starter
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


def run_mixed_festa_game(num_games=3):
    """
    Run multiple games with mixed FESTA rounds
    - Player 0: Monte Carlo AI
    - Players 1-3: Heuristic AIs
    
    Configuration:
    - festa1: POSITIVOS, random starter
    - festa2: NULOS, random starter
    - festa3: POSITIVOS, random starter
    - festa4: NULOS, random starter
    """
    
    players = ["MC-AI", "Heuristic-1", "Heuristic-2", "Heuristic-3"]
    cumulative_scores = {i: 0 for i in range(4)}
    
    print("=" * 80)
    print("MC-AI vs 3 HEURISTIC AIs - MIXED FESTA ROUNDS")
    print("(festa1,3=POSITIVOS | festa2,4=NULOS)")
    print("=" * 80)
    print(f"Running {num_games} games...\n")
    
    for game_num in range(num_games):
        print(f"Game {game_num + 1}/{num_games}:")
        print("-" * 80)
        
        game = Game(players)
        
        # Create AI players
        ai_players = {}
        rounds_played = 0
        
        while not game.is_game_over():
            round_type = game.get_current_round_type()
            
            # Skip non-festa rounds
            if not round_type.startswith("festa"):
                game.skip_round()
                continue
            
            # Determine if this festa is positivos or nulos
            festa_num = int(round_type[-1])  # Extract number from festa1/festa2/etc
            is_positivos = (festa_num in [1, 3])  # festa1 and festa3 are positivos
            
            # Random starting player
            starting_player = random.randint(0, 3)
            
            # Get starting player's hand and determine trump suit (for positivos)
            starting_hand = game.get_player_hand(starting_player)
            trump_suit = get_most_common_suit(starting_hand) if is_positivos else None
            
            # Configure this festa
            mode_str = "POSITIVOS" if is_positivos else "NULOS"
            print(f"  {round_type.upper():10} - {mode_str:10} - ", end="")
            
            if is_positivos:
                print(f"Player {starting_player} starts, Trump: {trump_suit.name[0]:1} - ", end="")
                game.set_festa_config(round_type, starter=starting_player, is_nulos=False, trump_suit=trump_suit)
            else:
                print(f"Player {starting_player} starts, NULOS - ", end="")
                game.set_festa_config(round_type, starter=starting_player, is_nulos=True, trump_suit=None)
            
            # Create/update AI players for this round
            for i in range(4):
                if i == 0:
                    # MC AI with appropriate settings
                    ai_players[i] = MonteCarloAI(i, round_type, num_simulations=50, trump_suit=trump_suit, is_nulos=(not is_positivos))
                else:
                    # Heuristic AI with appropriate settings
                    ai_players[i] = AIPlayer(game.get_player_hand(i), round_type, is_nulos=(not is_positivos))
            
            # Check if round can be played
            if not game.can_play_round():
                print("SKIPPED")
                game.skip_round()
                continue
            
            # Play round
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
            print(f"Points: {points}")
            rounds_played += 1
            
            game.advance_to_next_round()
        
        # Game over - get final standings
        print(f"\n  Final standings ({rounds_played} rounds played):")
        for i, player in enumerate(players):
            pts = game.cumulative_points[i]
            print(f"    {player:20} - {pts:4d} points")
            cumulative_scores[i] += pts
        
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
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n\n")
    print("#" * 80)
    print("# RUNNING TESTS ON MIXED FESTA ROUNDS (WITH MID-VAZA FIX)")
    print("#" * 80 + "\n")
    
    run_mixed_festa_game(num_games=3)
