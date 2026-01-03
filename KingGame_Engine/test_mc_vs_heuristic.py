"""
Test script to compare Monte Carlo AI vs Heuristic AI performance.
Runs 5 games of each round type with 1 MC AI and 3 Heuristic AIs.
"""

import random
from copy import deepcopy
from deck import Deck, Card
from game_simulator import Round, GamePlayer, Vaza
from mc_ai_player import MonteCarloAI
from ai_player import AIPlayer


def run_round(round_type: str, players: list[GamePlayer], deck: Deck, debug: bool = False) -> dict[int, int]:
    """
    Run a single round and return scores.
    
    Parameters
    ----------
    round_type : str
        Type of round to play.
    players : list[GamePlayer]
        List of 4 players.
    deck : Deck
        Shuffled deck to deal from.
    debug : bool
        Whether to print debug information.
    
    Returns
    -------
    dict[int, int]
        Mapping of player_id to round score.
    """
    # Deal cards
    cards = deck.cards.copy()
    random.shuffle(cards)
    
    for i, player in enumerate(players):
        player.hand = cards[i*13:(i+1)*13]
    
    if debug:
        print(f"\n  [DEBUG] Dealt {len(players[0].hand)} cards to each player")
    
    # Create round
    round_obj = Round(round_type, players)
    round_obj.starting_player = 0
    
    # Create Monte Carlo AI instance once per round
    mc_ai_instance = None
    
    # Play all vazas
    for vaza_num in range(13):
        # Start new vaza
        round_obj.start_vaza()
        current_player_idx = round_obj.starting_player
        
        # Play 4 cards in this vaza
        for _ in range(4):
            player = players[current_player_idx]
            valid_plays = round_obj.get_valid_plays(player.hand)
            
            # Choose card based on player type
            if player.id == 0:  # Monte Carlo AI
                # Create instance on first call
                if mc_ai_instance is None:
                    mc_ai_instance = MonteCarloAI(
                        player,
                        round_obj,
                        num_simulations=100,
                        pre_dealt_hand=player.hand.copy()
                    )
                    if debug:
                        print(f"  [DEBUG] MC AI created with {len(mc_ai_instance.my_hand)} cards")
                else:
                    # Update AI's hand
                    mc_ai_instance.my_hand = player.hand.copy()
                
                if debug:
                    est_sizes = [len(mc_ai_instance.player_hand_estimates[i]) for i in range(4) if i != 0]
                    print(f"  [DEBUG] MC choosing from {len(valid_plays)} options. Hand estimates: {est_sizes}")
                
                card = mc_ai_instance.choose_card(valid_plays, round_obj.current_vaza)
                
                if debug:
                    print(f"  [DEBUG] MC chose: {card}")
            else:  # Heuristic AI
                h_ai = AIPlayer(player.hand.copy(), round_type)
                card = h_ai.choose_card(valid_plays, round_obj.current_vaza)
            
            # Play the card
            round_obj.play_card(current_player_idx, card)
            player.hand.remove(card)
            
            # Update MC AI hand estimates after EVERY card played (not just MC's own cards)
            if mc_ai_instance is not None:
                before_sizes = [len(mc_ai_instance.player_hand_estimates[i]) for i in range(4) if i != 0]
                mc_ai_instance.update_hand_estimates(round_obj.current_vaza)
                after_sizes = [len(mc_ai_instance.player_hand_estimates[i]) for i in range(4) if i != 0]
                if debug and before_sizes != after_sizes:
                    print(f"  [DEBUG] Estimates updated: {before_sizes} -> {after_sizes}")
            
            # Print progress
            print(f"    Vaza {vaza_num + 1}, Player {current_player_idx}: {card}", end="", flush=True)
            if (current_player_idx + 1) % 4 == round_obj.starting_player or _ == 3:
                print()  # New line after vaza completes
            else:
                print("  |  ", end="", flush=True)
            
            current_player_idx = (current_player_idx + 1) % 4
        
        # Determine winner and update for next vaza
        winner_idx = round_obj.get_vaza_winner()
        round_obj.starting_player = winner_idx
    
    # Calculate points
    return round_obj.calculate_points()


def main():
    """Run the comparison test."""
    round_types = ["vazas", "copas", "homens", "mulheres", "king", "last"]
    num_games = 10
    debug_first_game = True  # Enable debug for first game of each round type
    
    # Track cumulative scores
    total_scores = {0: 0, 1: 0, 2: 0, 3: 0}
    round_type_scores = {rt: {0: 0, 1: 0, 2: 0, 3: 0} for rt in round_types}
    
    print("=" * 70)
    print("MONTE CARLO AI vs HEURISTIC AI COMPARISON")
    print("=" * 70)
    print("Player 0: Monte Carlo AI (100 simulations)")
    print("Player 1, 2, 3: Heuristic AI")
    print(f"Running {num_games} games per round type (6 types = {num_games * 6} total games)")
    print("=" * 70)
    print()
    
    # Test each round type
    for round_type in round_types:
        print(f"\n{round_type.upper()} ROUND:")
        print("-" * 70)
        
        round_scores = {0: [], 1: [], 2: [], 3: []}
        
        for game_num in range(num_games):
            # Create players
            players = [
                GamePlayer(id=i, name=f"Player{i}", is_ai=True)
                for i in range(4)
            ]
            for player in players:
                player.hand = []
            
            # Create and shuffle deck
            deck = Deck()
            
            # Run round (enable debug for first game of each round)
            enable_debug = debug_first_game and game_num == 0
            scores = run_round(round_type, players, deck, debug=enable_debug)
            
            # Track scores (scores is a list [p0, p1, p2, p3])
            for player_id in range(4):
                round_scores[player_id].append(scores[player_id])
                total_scores[player_id] += scores[player_id]
                round_type_scores[round_type][player_id] += scores[player_id]
            
            print(f"  Game {game_num + 1:2d}: MC={scores[0]:+4d}  H1={scores[1]:+4d}  H2={scores[2]:+4d}  H3={scores[3]:+4d}")
        
        # Print round summary
        print(f"\n  {round_type.capitalize()} Round Summary (after {num_games} games):")
        for player_id in range(4):
            avg = sum(round_scores[player_id]) / num_games
            player_type = "MC" if player_id == 0 else f"H{player_id}"
            print(f"    Player {player_id} ({player_type}): {avg:+6.1f}")
        
        # Best player in this round type
        best_player = min(round_type_scores[round_type].items(), key=lambda x: x[1])
        player_type = "Monte Carlo AI" if best_player[0] == 0 else f"Heuristic AI {best_player[0]}"
        print(f"  Best: Player {best_player[0]} ({player_type}) with {best_player[1]:+d} points")
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS (Total across all rounds)")
    print("=" * 70)
    
    for player_id in range(4):
        player_type = "Monte Carlo AI" if player_id == 0 else f"Heuristic AI {player_id}"
        avg_per_round = total_scores[player_id] / (len(round_types) * num_games)
        print(f"Player {player_id} ({player_type:15s}): {total_scores[player_id]:+5d} total, {avg_per_round:+6.2f} avg/game")
    
    # Determine winner
    print("\n" + "-" * 70)
    winner = min(total_scores.items(), key=lambda x: x[1])
    winner_type = "Monte Carlo AI" if winner[0] == 0 else f"Heuristic AI {winner[0]}"
    print(f"WINNER: Player {winner[0]} ({winner_type}) with {winner[1]:+d} total points")
    print("=" * 70)
    
    # Round-by-round comparison
    print("\n" + "=" * 70)
    print("ROUND-BY-ROUND COMPARISON")
    print("=" * 70)
    for round_type in round_types:
        mc_score = round_type_scores[round_type][0]
        h_scores = [round_type_scores[round_type][i] for i in [1, 2, 3]]
        h_avg = sum(h_scores) / 3
        print(f"{round_type:10s}: MC={mc_score:+4d}  Heuristic Avg={h_avg:+6.1f}  Difference={mc_score - h_avg:+6.1f}")


if __name__ == "__main__":
    main()
