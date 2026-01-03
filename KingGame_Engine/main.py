"""
Real-life King Game Assistant
=============================
Use this when playing King with physical cards.
The program tracks game state and validates plays but doesn't show human player hands.
"""

from game_simulator import Round
from deck import Card, Suit, Rank
from mc_ai_player import MonteCarloAI
from game_player import GamePlayer

# Define the order of rounds in a King game
ROUND_ORDER = ["vazas", "copas", "homens", "mulheres", "king", "last", "festa1", "festa2", "festa3", "festa4"]


def display_card_list(cards: list[Card], sort: bool = True) -> str:
    """Format a list of cards for display"""
    if sort:
        cards = sorted(cards, key=lambda c: (c.suit.value, c.rank.value))
    return ", ".join([str(card) for card in cards])


def get_all_cards() -> list[Card]:
    """Get all 52 cards in the deck"""
    all_cards = []
    for suit in Suit:
        for rank in Rank:
            all_cards.append(Card(suit, rank))
    return all_cards


def setup_players() -> tuple[list[str], list[bool]]:
    """Let user choose player names and types (human vs AI)"""
    players = []
    player_is_ai = [False, False, False, False]
    
    print("=" * 80)
    print("SETUP: Player Configuration")
    print("=" * 80)
    print("Configure each player's name and type:")
    print("  - HUMAN players: You input which card they played")
    print("  - AI players: Computer decides and shows the card\n")
    
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


def configure_festa_round(festa_name: str, players: list[str]) -> tuple[int, bool, Suit]:
    """Configure a festa round: select starting player, nulos/positivos mode, and trump suit"""
    print("=" * 80)
    print(f"CONFIGURE {festa_name.upper()}")
    print("=" * 80)
    
    # Select starting player
    print("Who should start this festa?\n")
    for i, player in enumerate(players):
        print(f"  [{i+1}] {player}")
    
    print()
    starter = 0
    while True:
        choice = input(f"Select starting player (1-4) [default: 1]: ").strip()
        
        if choice == '':
            starter = 0
            break
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < 4:
                starter = idx
                break
        
        print("Invalid choice. Please enter 1, 2, 3, or 4.\n")
    
    print(f"\n✓ {players[starter]} will start\n")
    
    # Select nulos or positivos
    print("Select festa mode:\n")
    print("  [N] NULOS (Negative)")
    print("      - Avoid winning vazas (like the vazas round)")
    print("      - Winning vazas = negative points\n")
    print("  [P] POSITIVOS (Positive)")
    print("      - Try to WIN vazas!")
    print("      - Winning vazas = positive points")
    print("      - Can select a trump suit\n")
    
    is_nulos = True
    while True:
        choice = input("Select mode (N/P) [default: Nulos]: ").strip().upper()
        
        if choice == '' or choice == 'N':
            is_nulos = True
            print("\n✓ NULOS mode selected - Avoid winning vazas!\n")
            break
        elif choice == 'P':
            is_nulos = False
            print("\n✓ POSITIVOS mode selected - Try to WIN vazas!\n")
            break
        else:
            print("Invalid choice. Please enter 'N' or 'P'\n")
    
    # Select trump suit if positivos
    trump_suit = None
    if not is_nulos:
        print("Select trump suit (beats all other suits):\n")
        print("  [H] Hearts (♥)")
        print("  [D] Diamonds (♦)")
        print("  [C] Clubs (♣)")
        print("  [S] Spades (♠)")
        print("  [N] None (no trump suit)\n")
        
        while True:
            choice = input("Select trump suit (H/D/C/S/N) [default: None]: ").strip().upper()
            
            if choice == '' or choice == 'N':
                trump_suit = None
                print("\n✓ No trump suit selected\n")
                break
            elif choice == 'H':
                trump_suit = Suit.HEARTS
                print("\n✓ Hearts (♥) is trump!\n")
                break
            elif choice == 'D':
                trump_suit = Suit.DIAMONDS
                print("\n✓ Diamonds (♦) is trump!\n")
                break
            elif choice == 'C':
                trump_suit = Suit.CLUBS
                print("\n✓ Clubs (♣) is trump!\n")
                break
            elif choice == 'S':
                trump_suit = Suit.SPADES
                print("\n✓ Spades (♠) is trump!\n")
                break
            else:
                print("Invalid choice. Please enter H, D, C, S, or N\n")
    
    return starter, is_nulos, trump_suit

def start_game():
    """Play King with physical cards - track game state and validate plays"""
    
    # Get players - names and types (human vs AI)
    player_names, player_is_ai = setup_players()
    
    # Game state variables
    players: list[GamePlayer] = [GamePlayer(i, name, player_is_ai[i]) for i, name in enumerate(player_names)]
    starting_player = 0  # Will be set later
    round_index = 0
    current_round: Round = None
    round_results: list[dict] = []  # Store results of each round
    cumulative_points = [0, 0, 0, 0]
    
    print("\n" + "=" * 80)
    print("REAL-LIFE KING GAME ASSISTANT")
    print("=" * 80)
    print("Instructions:")
    print("  1. Shuffle and deal 13 cards to each player in real life")
    print("  2. The program will track plays and calculate scores")
    print("  3. For human players, input which card they played")
    print("  4. For AI players, the computer will show which card to play")
    print("  5. Type 'help' at any time for card format examples")
    print("=" * 80)
    player_types = ', '.join([f'{player_names[i]} ({"AI" if player_is_ai[i] else "HUMAN"})' for i in range(4)])
    print(f"\nPlayers: {player_types}\n")
    
    for round_type in ROUND_ORDER:
        
        # Create round
        current_round = Round(round_type, players)
        current_round.start()

        # Create/update AI players for this round
        ai_players: dict[int, MonteCarloAI] = {}
        for i in range(4):
            if players[i].is_ai:
                ai_players[i] = MonteCarloAI(i, round_type, num_simulations=30)

        cards_played_round: list[Card] = []
        
        print("\n" + "=" * 80)
        print(f"ROUND: {round_type.upper()}")
        print("=" * 80)
        print(f"Objective: {get_round_description(round_type)}\n")
        
        # Play all 13 vazas in this round
        for vaza_num in range(13):
            info = current_round.get_next_vaza_info()
            
            # START VAZA
            current_round.start_vaza()
            
            print("=" * 80)
            print(f"VAZA {vaza_num+1}")
            print("=" * 80)
            print(f"Starter: {players[info['starter']]}")
            print(f"Play order: {', '.join([players[p] for p in info['play_order']])}\n")
            
            # Show cards played so far (for reference)
            if cards_played_round:
                print(f"Cards played in previous vazas: {len(cards_played_round)} cards")
            print()
            
            for player_idx in info['play_order']:
                if players[player_idx].is_ai:

                    hand = current_round.get_player_hand(player_idx)
                    valid_plays = current_round.get_valid_plays(player_idx)
                    
                    # Safety check: ensure AI has cards to play
                    if not valid_plays:
                        print(f"⚠️  WARNING: {players[player_idx]} (AI) has no valid plays!")
                        print(f"   Hand: {display_card_list(hand)}")
                        continue
                    
                    
                    card = ai_players[player_idx].choose_card(
                        my_hand=hand,
                        valid_plays=valid_plays,
                        current_vaza=current_round.current_vaza
                    )
                    
                    # Play the card in the vaza
                    current_round.play_card(player_idx, card)
                    cards_played_round.append(card)

                    print(f">>> {players[player_idx]} (AI) plays: {card}")
                
                else:
                    # Human player - get input for which card they played
                    print(f"{players[player_idx]}'s turn:")
                    
                    # Show what's been played so far in this vaza (in play order)
                    if current_round.current_vaza.cards_played:
                        print(f"  Cards played this vaza: {display_card_list(current_round.current_vaza.cards_played, sort=False)}")
                    
                    while True:
                        choice = input(f"  Which card did {players[player_idx]} play? (or 'help'): ").strip()
                        
                        if choice.lower() == 'help':
                            print("\n  Card format examples:")
                            print("    - Number + Suit: 2H, 10D, 13C, 14S")
                            print("    - Letter + Suit: AH (Ace), KS (King), QD (Queen), JC (Jack)")
                            print("    - Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades")
                            print("    - Examples: 'AH' = Ace of Hearts, 'KH' = King of Hearts")
                            print("                '7D' = 7 of Diamonds, '10S' = 10 of Spades\n")
                            continue
                        
                        card = Card.from_string(choice)
                        
                        if card is None:
                            print(f"  ❌ Invalid card format. Try again (or type 'help')\n")
                            continue
                        
                        # Check if card was already played
                        if card in cards_played_round:
                            print(f"  ❌ {card} was already played earlier.")
                            override = input(f"      Override and play anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                continue

                        # Play the card in the vaza
                        current_round.play_card(player_idx, card)
                        cards_played_round.append(card)

                        print(f"  ✓ {players[player_idx]} plays: {card}\n")
                        break
            
            # Determine winner and update round state
            winner = current_round.get_vaza_winner()
            
            print(f"🏆 Vaza won by: {players[winner]}")
            print(f"Vazas won so far: {', '.join([f'{players[i]}: {current_round.vazas_won[i]}' for i in range(4)])}\n")
            
            if not current_round.is_round_over():
                input("Press Enter for next vaza...")
                print()
        
        # Round over - show results
        print("\n" + "=" * 80)
        print(f"ROUND {round_type.upper()} - RESULTS")
        print("=" * 80)
        
        results = game.get_current_round_results()
        for i, player in enumerate(players):
            points = results['points'][i]
            detail = get_round_detail(round_type, game.current_round, i)
            print(f"{player:20} - {detail:30} Points: {points:+5d}")
        
        print(f"\nCumulative points: {', '.join([f'{players[i]}: {game.cumulative_points[i]}' for i in range(4)])}")
        
        if not game.is_game_over():
            input("\nPress Enter to advance to next round...")
            game.advance_to_next_round()
            
            print("\nNew round started. Re-deal cards in real life.")
            input("Press Enter when cards are dealt...")
    
    # Game over
    print("\n" + "=" * 80)
    print("SEASON OVER!")
    print("=" * 80)
    
    standings = game.get_season_standings()
    print("\nFINAL STANDINGS:\n")
    
    # Sort by points (highest first)
    sorted_players = sorted(
        zip(standings['players'], standings['cumulative_points']),
        key=lambda x: x[1],
        reverse=True
    )
    
    for i, (player, points) in enumerate(sorted_players, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
        print(f"{medal} {i}. {player:20} - {points:+5d} points")
    
    print("=" * 80)


def get_round_description(round_type: str) -> str:
    """Get description of what to avoid/collect in each round"""
    descriptions = {
        "vazas": "Avoid winning vazas",
        "copas": "Avoid collecting Hearts (♥)",
        "homens": "Avoid collecting Jacks and Kings",
        "mulheres": "Avoid collecting Queens",
        "king": "Avoid the King of Hearts (K♥)",
        "last": "Avoid winning the last vaza"
    }

    return descriptions.get(round_type, "")


def get_round_detail(round_type: str, current_round, player_idx: int) -> str:
    """Get detail about what player collected this round"""
    if round_type in ["vazas", "festa1", "festa2", "festa3", "festa4"]:
        return f"{current_round.vazas_won[player_idx]} vazas"
    elif round_type == "copas":
        hearts = current_round.count_suit(player_idx, Suit.HEARTS)
        return f"{hearts} hearts"
    elif round_type == "homens":
        men = sum(1 for c in current_round.cards_won[player_idx] 
                  if c.rank == Rank.JACK or c.rank == Rank.KING)
        return f"{men} men (J+K)"
    elif round_type == "mulheres":
        queens = sum(1 for c in current_round.cards_won[player_idx]
                     if c.rank == Rank.QUEEN)
        return f"{queens} queens"
    elif round_type == "king":
        has_king = any(c.rank == Rank.KING and c.suit == Suit.HEARTS 
                      for c in current_round.cards_won[player_idx])
        return "King of Hearts!" if has_king else "Safe"
    elif round_type == "last":
        won_last = current_round.vazas_won[player_idx] > 0  # In "last" round, only last vaza matters
        return "Won last vaza!" if won_last else "Safe"
    return ""


if __name__ == "__main__":
    start_game()
