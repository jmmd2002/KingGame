from game import Game
from deck import Card
from mc_ai_player import MonteCarloAI


def display_hand(hand: list[Card]) -> str:
    """Format hand for display"""
    return ", ".join([str(card) for card in hand])


def get_card_by_display(display: str, hand: list[Card]) -> Card:
    """Find card in hand by its display string (e.g., '1H', '13S')"""
    for card in hand:
        if str(card) == display.upper():
            return card
    return None


def setup_players():
    """Let user choose which players are human vs AI"""
    players = ["Player 1", "Player 2", "Player 3", "Player 4"]
    is_ai = [False, False, False, False]
    
    print("=" * 80)
    print("SETUP: Choose player types")
    print("=" * 80)
    
    for i in range(4):
        choice = input(f"{players[i]} - (h)uman or (a)i? [default: human]: ").strip().lower()
        if choice == 'a':
            is_ai[i] = True
            print(f"  -> {players[i]} will be AI\n")
        else:
            print(f"  -> {players[i]} will be human\n")
    
    return players, is_ai


def interactive_game():
    """Play King with manual decisions and/or AI players"""
    
    players, is_ai = setup_players()
    game = Game(players)
    
    # Create AI players for all positions (they'll be used when needed)
    ai_players = {}
    for i in range(4):
        if is_ai[i]:
            ai_players[i] = None  # Will be created when round starts
    
    print("=" * 80)
    print("KING GAME - INTERACTIVE MODE")
    print("=" * 80)
    print(f"Players: {', '.join([f'{players[i]} (' + ('AI' if is_ai[i] else 'HUMAN') + ')' for i in range(4)])}\n")
    
    while not game.is_game_over():
        round_type = game.get_current_round_type()
        
        # Create/update AI players for this round
        for i in range(4):
            if is_ai[i]:
                ai_players[i] = MonteCarloAI(i, round_type, num_simulations=30)
        
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
        print(f"Players: {', '.join([f'{players[i]} (' + ('AI' if is_ai[i] else 'HUMAN') + ')' for i in range(4)])}\n")
        
        # Play all 13 vazas in this round
        vaza_num = 0
        
        while not game.is_round_over():
            vaza_num += 1
            info = game.get_next_vaza_info()
            
            # START VAZA FIRST
            game.current_round.start_vaza()
            
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
            
            # Get card choices
            card_plays = []
            for player_idx in info['play_order']:
                hand = game.get_player_hand(player_idx)
                
                if is_ai[player_idx]:
                    # AI decides
                    valid_plays = game.get_valid_plays(player_idx)
                    
                    # Collect cards played so far this round
                    cards_played_this_round = []
                    for card_list in game.current_round.cards_won:
                        cards_played_this_round.extend(card_list)
                    
                    # DEBUG
                    if len(game.current_round.current_vaza.cards_played) > 0:
                        print(f"    [{players[player_idx]} deciding] Main suit: {game.current_round.current_vaza.main_suit}, Valid plays: {[str(c) for c in valid_plays]}")
                    
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
                    print(f"{players[player_idx]} (AI) plays: {card}\n")
                
                else:
                    # Human decides
                    while True:
                        choice = input(f"{players[player_idx]}, choose card (or 'list' to see hand): ").strip()
                        
                        if choice.lower() == 'list':
                            print(f"Your hand: {display_hand(hand)}\n")
                            continue
                        
                        card = get_card_by_display(choice, hand)
                        if card:
                            # Add card to current vaza for next player to see
                            game.current_round.current_vaza.cards_played.append(card)
                            game.current_round.current_vaza.play_order.append(player_idx)
                            if game.current_round.current_vaza.main_suit is None:
                                game.current_round.current_vaza.main_suit = card.suit
                            
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
