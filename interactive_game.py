from game import Game
from deck import Card


def display_hand(hand: list[Card]) -> str:
    """Format hand for display"""
    return ", ".join([str(card) for card in hand])


def get_card_by_display(display: str, hand: list[Card]) -> Card:
    """Find card in hand by its display string (e.g., '1H', '13S')"""
    for card in hand:
        if str(card) == display.upper():
            return card
    return None


def interactive_game():
    """Play King with manual decisions"""
    
    players = ["Player 1", "Player 2", "Player 3", "Player 4"]
    game = Game(players)
    
    print("=" * 80)
    print("KING GAME - INTERACTIVE MODE")
    print("=" * 80)
    print(f"Players: {', '.join(players)}\n")
    
    while not game.is_game_over():
        round_type = game.get_current_round_type()
        
        # Check if round can be played
        if not game.can_play_round():
            print("\n" + "=" * 80)
            print(f"ROUND: {round_type.upper()} - SKIPPED (no cards available)")
            print("=" * 80)
            game.skip_round()
            continue
        
        print("\n" + "=" * 80)
        print(f"ROUND: {round_type.upper()}")
        print("=" * 80)
        print(f"Players: {', '.join(players)}\n")
        
        # Play all 13 vazas in this round
        vaza_num = 0
        
        while not game.is_round_over():
            vaza_num += 1
            info = game.get_next_vaza_info()
            
            print("=" * 80)
            print(f"VAZA {vaza_num}")
            print("=" * 80)
            print(f"Starter: {players[info['starter']]}")
            print(f"Play order: {[players[p] for p in info['play_order']]}\n")
            
            # Display hands
            for player_idx in info['play_order']:
                hand = game.get_player_hand(player_idx)
                print(f"{players[player_idx]}'s hand: {display_hand(hand)}")
            
            print()
            
            # Get card choices from user
            card_plays = []
            for player_idx in info['play_order']:
                hand = game.get_player_hand(player_idx)
                
                while True:
                    choice = input(f"{players[player_idx]}, choose card (or 'list' to see hand): ").strip()
                    
                    if choice.lower() == 'list':
                        print(f"Your hand: {display_hand(hand)}\n")
                        continue
                    
                    card = get_card_by_display(choice, hand)
                    if card:
                        card_plays.append((player_idx, card))
                        print(f"{players[player_idx]} plays: {card}\n")
                        break
                    else:
                        print(f"Invalid card. Try again.\n")
            
            # Play vaza
            winner = game.play_vaza(card_plays)
            
            print(f"Vaza won by: {players[winner]}")
            print(f"Vazas won so far: {dict(zip(players, game.current_round.vazas_won))}\n")
            
            if not game.is_round_over():
                input("Press Enter for next vaza...")
                print()
        
        # Round over - show results
        print("\n" + "=" * 80)
        print(f"ROUND {round_type.upper()} - RESULTS")
        print("=" * 80)
        
        results = game.get_current_round_results()
        for i, player in enumerate(players):
            points = results['points'][i]
            print(f"{player:20} - Points: {points:4d}")
        
        print(f"\nCumulative points: {dict(zip(players, game.cumulative_points))}")
        
        if not game.is_game_over():
            input("\nPress Enter to advance to next round...")
            game.advance_to_next_round()
    
    # Game over
    print("\n" + "=" * 80)
    print("SEASON OVER!")
    print("=" * 80)
    
    standings = game.get_season_standings()
    print("\nFINAL STANDINGS:\n")
    
    # Sort by points
    sorted_players = sorted(
        zip(standings['players'], standings['cumulative_points']),
        key=lambda x: x[1],
        reverse=True
    )
    
    for i, (player, points) in enumerate(sorted_players, 1):
        print(f"{i}. {player:20} - {points:4d} points")
    
    print("=" * 80)


if __name__ == "__main__":
    interactive_game()
