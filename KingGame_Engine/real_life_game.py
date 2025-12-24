"""
Real-life King Game Assistant
=============================
Use this when playing King with physical cards.
The program tracks game state and validates plays but doesn't show human player hands.
"""

from game import Game
from deck import Card, Suit, Rank
from mc_ai_player import MonteCarloAI


def card_from_string(card_str: str) -> Card:
    """
    Parse a card from string format like '1H', '13S', 'AH', 'KS', etc.
    
    Accepted formats:
    - Number + Suit: '2H', '10D', '13C', '14S'
    - Letter + Suit: 'AH' (Ace), 'KS' (King), 'QD' (Queen), 'JC' (Jack)
    
    Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades
    """
    card_str = card_str.strip().upper()
    
    if len(card_str) < 2:
        return None
    
    # Extract suit (last character)
    suit_char = card_str[-1]
    rank_str = card_str[:-1]
    
    # Parse suit
    suit_map = {'H': Suit.HEARTS, 'D': Suit.DIAMONDS, 'C': Suit.CLUBS, 'S': Suit.SPADES}
    if suit_char not in suit_map:
        return None
    suit = suit_map[suit_char]
    
    # Parse rank
    rank = None
    if rank_str.isdigit():
        rank_value = int(rank_str)
        for r in Rank:
            if r.value == rank_value:
                rank = r
                break
    else:
        # Letter format
        letter_map = {'A': Rank.ACE, 'K': Rank.KING, 'Q': Rank.QUEEN, 'J': Rank.JACK}
        rank = letter_map.get(rank_str)
    
    if rank is None:
        return None
    
    return Card(suit, rank)


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


def setup_players():
    """Let user choose player names and types (human vs AI)"""
    players = []
    is_ai = [False, False, False, False]
    
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
        
        # Get player type
        choice = input(f"  {name} - (h)uman or (a)i? [default: human]: ").strip().lower()
        if choice == 'a':
            is_ai[i] = True
            print(f"  -> {name} will be AI\n")
        else:
            print(f"  -> {name} will be HUMAN (real player)\n")
    
    return players, is_ai


def input_ai_hands(players: list[str], is_ai: list[bool], game) -> None:
    """Input the actual cards dealt to AI players in real life"""
    print("=" * 80)
    print("INPUT AI PLAYER HANDS")
    print("=" * 80)
    print("Enter the 13 cards dealt to each AI player in real life.")
    print("This allows the AI to make decisions based on their actual hand.\n")
    
    for player_idx in range(4):
        if not is_ai[player_idx]:
            continue
        
        print(f"{players[player_idx]}'s hand (13 cards):")
        print("  Enter cards separated by spaces (e.g., AH KS 7D 10C ...)")
        print("  Or type 'help' for card format examples\n")
        
        while True:
            cards_input = input(f"  Cards for {players[player_idx]}: ").strip()
            
            if cards_input.lower() == 'help':
                print("\n  Card format examples:")
                print("    - Number + Suit: 2H, 10D, 13C, 14S")
                print("    - Letter + Suit: AH (Ace), KS (King), QD (Queen), JC (Jack)")
                print("    - Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades")
                print("    - Example input: AH KS 7D 10C 2H 3S 9D QH JC 4D 5H 6S 8C\n")
                continue
            
            # Parse the cards
            card_strings = cards_input.split()
            
            if len(card_strings) != 13:
                print(f"  ❌ You must enter exactly 13 cards. You entered {len(card_strings)}.\n")
                continue
            
            # Convert strings to Card objects
            cards = []
            invalid = False
            for card_str in card_strings:
                card = card_from_string(card_str)
                if card is None:
                    print(f"  ❌ Invalid card format: '{card_str}'\n")
                    invalid = True
                    break
                if card in cards:
                    print(f"  ❌ Duplicate card: {card}\n")
                    invalid = True
                    break
                cards.append(card)
            
            if invalid:
                continue
            
            # Update the game's internal hand for this AI player
            game.current_round.player_hands[player_idx] = cards
            print(f"  ✓ Hand set for {players[player_idx]}: {display_card_list(cards)}\n")
            break
    
    print("All AI hands configured!\n")


def select_starting_player(players: list[str]) -> int:
    """Let user choose which player starts the first round"""
    print("=" * 80)
    print("SELECT STARTING PLAYER")
    print("=" * 80)
    print("Who should start the first round?\n")
    
    for i, player in enumerate(players):
        print(f"  [{i+1}] {player}")
    
    print()
    while True:
        choice = input(f"Select starting player (1-4) [default: 1]: ").strip()
        
        if choice == '':
            print(f"\n✓ {players[0]} will start the first round\n")
            return 0
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < 4:
                print(f"\n✓ {players[idx]} will start the first round\n")
                return idx
        
        print("Invalid choice. Please enter 1, 2, 3, or 4.\n")


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



def select_game_mode():
    """Let user choose between real-life and virtual mode"""
    print("=" * 80)
    print("GAME MODE SELECTION")
    print("=" * 80)
    print("Choose game mode:\n")
    print("  [R] REAL LIFE MODE")
    print("      - You shuffle and deal physical cards")
    print("      - Input which card each player plays")
    print("      - No validation against computer-dealt hands")
    print("      - Perfect for playing with real cards\n")
    print("  [V] VIRTUAL MODE")
    print("      - Computer deals cards and shows hands")
    print("      - Player input validated against dealt hands")
    print("      - Good for practice or remote play\n")
    
    while True:
        choice = input("Select mode (R/V) [default: Real Life]: ").strip().upper()
        if choice == '' or choice == 'R':
            print("\n✓ REAL LIFE MODE selected\n")
            return 'real_life'
        elif choice == 'V':
            print("\n✓ VIRTUAL MODE selected\n")
            return 'virtual'
        else:
            print("Invalid choice. Please enter 'R' or 'V'\n")


def real_life_game():
    """Play King with physical cards - track game state and validate plays"""
    
    # Select game mode
    game_mode = select_game_mode()
    
    players, is_ai = setup_players()
    
    # Select starting player
    starting_player = select_starting_player(players)
    
    print("\n" + "=" * 80)
    if game_mode == 'real_life':
        print("REAL-LIFE KING GAME ASSISTANT")
        print("=" * 80)
        print("Instructions:")
        print("  1. Shuffle and deal 13 cards to each player in real life")
        print("  2. The program will track plays and calculate scores")
        print("  3. For human players, input which card they played")
        print("  4. For AI players, the computer will show which card to play")
        print("  5. Type 'help' at any time for card format examples")
    else:
        print("VIRTUAL KING GAME ASSISTANT")
        print("=" * 80)
        print("Instructions:")
        print("  1. Computer will deal cards to each player")
        print("  2. Human player hands will be displayed")
        print("  3. Input which card to play (validated against your hand)")
        print("  4. For AI players, the computer decides and plays")
        print("  5. Type 'help' or 'list' at any time for card format/hand")
    print("=" * 80)
    player_types = ', '.join([f'{players[i]} ({"AI" if is_ai[i] else "HUMAN"})' for i in range(4)])
    print(f"\nPlayers: {player_types}\n")
    
    if game_mode == 'real_life':
        input("Press Enter when cards are dealt in real life...")
    else:
        input("Press Enter to deal cards...")
    
    # Create game with custom starting player
    game = Game(players, starting_player=starting_player)
    
    # In real-life mode, input AI player hands
    if game_mode == 'real_life' and any(is_ai):
        input_ai_hands(players, is_ai, game)
    
    # Track which cards have been played (for validation and AI)
    all_cards = get_all_cards()
    
    # Create AI players for AI positions
    ai_players = {}
    for i in range(4):
        if is_ai[i]:
            ai_players[i] = None  # Will be created when round starts
    
    while not game.is_game_over():
        round_type = game.get_current_round_type()
        
        # Reset cards played tracker for each new round (new deck)
        cards_played_overall = []
        
        # Configure festa rounds before they start
        if round_type in ["festa1", "festa2", "festa3", "festa4"]:
            starter, is_nulos, trump_suit = configure_festa_round(round_type, players)
            game.set_festa_config(round_type, starter, is_nulos, trump_suit)
            
            # Need to restart the round with the new configuration
            game.round_index -= 1
            game.advance_to_next_round()
            
            # In real-life mode, input AI hands for festa
            if game_mode == 'real_life' and any(is_ai):
                print(f"\n{round_type.upper()} started. Deal cards in real life.")
                input("Press Enter when cards are dealt...")
                input_ai_hands(players, is_ai, game)
            
            round_type = game.get_current_round_type()
        
        # Get trump suit for this round (if festa positivos)
        trump_suit = None
        festa_round_num = ['festa1', 'festa2', 'festa3', 'festa4'].index(round_type) if round_type in ['festa1', 'festa2', 'festa3', 'festa4'] else -1
        if festa_round_num >= 0 and game.festa_modes.get(festa_round_num) == False:  # positivos
            trump_suit = game.festa_trump_suits.get(festa_round_num)
        
        # Create/update AI players for this round
        for i in range(4):
            if is_ai[i]:
                ai_players[i] = MonteCarloAI(i, round_type, num_simulations=30, trump_suit=trump_suit)
        
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
        print(f"Objective: {get_round_description(round_type, game)}\n")
        
        # Play all 13 vazas in this round
        vaza_num = 0
        
        while not game.is_round_over():
            vaza_num += 1
            info = game.get_next_vaza_info()
            
            # START VAZA
            game.current_round.start_vaza()
            
            print("=" * 80)
            print(f"VAZA {vaza_num}")
            print("=" * 80)
            print(f"Starter: {players[info['starter']]}")
            print(f"Play order: {', '.join([players[p] for p in info['play_order']])}\n")
            
            # In VIRTUAL mode, show all player hands
            if game_mode == 'virtual':
                print("Current hands:")
                for idx in range(4):
                    hand = game.get_player_hand(idx)
                    player_type = "AI" if is_ai[idx] else "HUMAN"
                    print(f"  {players[idx]} ({player_type}): {display_card_list(hand)}")
                print()
            
            # Show cards played so far (for reference)
            if cards_played_overall:
                print(f"Cards played in previous vazas: {len(cards_played_overall)} cards")
            print()
            
            # Get card plays for this vaza
            card_plays = []
            
            for player_idx in info['play_order']:
                hand = game.get_player_hand(player_idx)
                
                if is_ai[player_idx]:
                    # AI decides
                    valid_plays = game.get_valid_plays(player_idx)
                    
                    # Safety check: ensure AI has cards to play
                    if not valid_plays:
                        print(f"⚠️  WARNING: {players[player_idx]} (AI) has no valid plays!")
                        print(f"   Hand: {display_card_list(hand)}")
                        continue
                    
                    # Collect cards played this round
                    cards_played_this_round = []
                    for card_list in game.current_round.cards_won:
                        cards_played_this_round.extend(card_list)
                    
                    card = ai_players[player_idx].choose_card(
                        my_hand=hand,
                        valid_plays=valid_plays,
                        cards_played_this_round=cards_played_this_round,
                        current_vaza=game.current_round.current_vaza
                    )
                    
                    # Safety check: verify AI chose a card from its hand
                    if card not in hand:
                        print(f"❌ ERROR: AI chose {card} but it's not in their hand!")
                        print(f"   Hand: {display_card_list(hand)}")
                        print(f"   This should not happen. Please report this bug.")
                        continue
                    
                    # Add card to current vaza for next player to see
                    game.current_round.current_vaza.cards_played.append(card)
                    game.current_round.current_vaza.play_order.append(player_idx)
                    if game.current_round.current_vaza.main_suit is None:
                        game.current_round.current_vaza.main_suit = card.suit
                    
                    card_plays.append((player_idx, card))
                    cards_played_overall.append(card)
                    
                    print(f">>> {players[player_idx]} (AI) plays: {card}")
                    if game_mode == 'real_life':
                        print(f"    (Play this card in real life for {players[player_idx]})\n")
                    else:
                        print()
                
                else:
                    # Human player - get input for which card they played
                    print(f"{players[player_idx]}'s turn:")
                    
                    # In VIRTUAL mode, show the player's hand
                    if game_mode == 'virtual':
                        print(f"  Your hand: {display_card_list(hand)}")
                    
                    # Show the main suit if already established
                    if game.current_round.current_vaza.main_suit:
                        print(f"  Main suit this vaza: {game.current_round.current_vaza.main_suit.name}")
                    
                    # Show what's been played so far in this vaza (in play order)
                    if game.current_round.current_vaza.cards_played:
                        print(f"  Cards played this vaza: {display_card_list(game.current_round.current_vaza.cards_played, sort=False)}")
                    
                    while True:
                        if game_mode == 'virtual':
                            choice = input(f"  Which card to play? (or 'help'/'list'): ").strip()
                        else:
                            choice = input(f"  Which card did {players[player_idx]} play? (or 'help'): ").strip()
                        
                        if choice.lower() == 'list':
                            print(f"  Your hand: {display_card_list(hand)}\n")
                            continue
                        
                        if choice.lower() == 'help':
                            print("\n  Card format examples:")
                            print("    - Number + Suit: 2H, 10D, 13C, 14S")
                            print("    - Letter + Suit: AH (Ace), KS (King), QD (Queen), JC (Jack)")
                            print("    - Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades")
                            print("    - Examples: 'AH' = Ace of Hearts, 'KH' = King of Hearts")
                            print("                '7D' = 7 of Diamonds, '10S' = 10 of Spades\n")
                            continue
                        
                        card = card_from_string(choice)
                        
                        if card is None:
                            print(f"  ❌ Invalid card format. Try again (or type 'help')\n")
                            continue
                        
                        # Check if card was already played
                        if card in cards_played_overall:
                            print(f"  ❌ {card} was already played earlier.")
                            override = input(f"      Override and play anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                continue
                        
                        # VIRTUAL mode: validate card is in player's hand
                        if game_mode == 'virtual':
                            if card not in hand:
                                print(f"  ❌ {card} is not in your hand.")
                                override = input(f"      Override and play anyway? (y/n): ").strip().lower()
                                if override != 'y':
                                    continue
                        
                        # REAL LIFE mode: trust user input (cards dealt in real life)
                        # No validation against internal hand tracking
                        
                        # Add card to current vaza
                        game.current_round.current_vaza.cards_played.append(card)
                        game.current_round.current_vaza.play_order.append(player_idx)
                        if game.current_round.current_vaza.main_suit is None:
                            game.current_round.current_vaza.main_suit = card.suit
                        
                        card_plays.append((player_idx, card))
                        cards_played_overall.append(card)
                        print(f"  ✓ {players[player_idx]} plays: {card}\n")
                        break
            
            # Play vaza (use appropriate validation based on mode)
            winner = game.play_vaza(card_plays, validate_hands=(game_mode == 'virtual'))
            
            print(f"🏆 Vaza won by: {players[winner]}")
            print(f"Vazas won so far: {', '.join([f'{players[i]}: {game.current_round.vazas_won[i]}' for i in range(4)])}\n")
            
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
            detail = get_round_detail(round_type, game.current_round, i)
            print(f"{player:20} - {detail:30} Points: {points:+5d}")
        
        print(f"\nCumulative points: {', '.join([f'{players[i]}: {game.cumulative_points[i]}' for i in range(4)])}")
        
        if not game.is_game_over():
            input("\nPress Enter to advance to next round...")
            game.advance_to_next_round()
            
            # In real-life mode, input AI hands for the new round
            if game_mode == 'real_life' and any(is_ai):
                print("\nNew round started. Re-deal cards in real life.")
                input("Press Enter when cards are dealt...")
                input_ai_hands(players, is_ai, game)
    
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


def get_round_description(round_type: str, game=None) -> str:
    """Get description of what to avoid/collect in each round"""
    descriptions = {
        "vazas": "Avoid winning vazas",
        "copas": "Avoid collecting Hearts (♥)",
        "homens": "Avoid collecting Jacks and Kings",
        "mulheres": "Avoid collecting Queens",
        "king": "Avoid the King of Hearts (K♥)",
        "last": "Avoid winning the last vaza"
    }
    
    if round_type in ["festa1", "festa2", "festa3", "festa4"]:
        if game and not game.is_festa_nulos(round_type):
            return f"FESTA {round_type[-1]} - POSITIVOS: Try to WIN vazas!"
        else:
            return f"FESTA {round_type[-1]} - NULOS: Avoid winning vazas"
    
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
    real_life_game()
