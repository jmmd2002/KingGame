from deck import Card, Deck, Suit, Rank
from game_player import GamePlayer

class Vaza:
    """
    Represents a single trick (vaza) in a card game round.
    
    A vaza consists of 4 cards played by 4 players in sequence. It tracks
    which cards were played, the order of play, the main suit, and the winner.
    
    Attributes
    ----------
    vaza_number : int
        The sequential number of this vaza in the round (1-13).
    starter : int
        Index (0-3) of the player who starts this vaza.
    cards_played : list[Card]
        Cards played in this vaza, in play order.
    play_order : list[int]
        Player indices in the order they played cards.
    main_suit : Suit or None
        The suit of the first card played (determines which suit must be followed).
    winner : int or None
        Index (0-3) of the player who won this vaza.
    """
    
    def __init__(self, vaza_number: int, starter: int) -> None:
        """
        Initialize a new vaza.
        
        Parameters
        ----------
        vaza_number : int
            The sequential number of this vaza in the round (1-13).
        starter : int
            Index (0-3) of the player who starts this vaza.
        """
        self.vaza_number = vaza_number
        self.starter = starter
        self.card_plays: list[tuple[int, Card]] = []  # Merged list of (player, card) tuples
        self.main_suit: Suit = None     # Suit of first card played
        self.winner: int = None
    
    @property
    def cards_played(self) -> list[Card]:
        """Get list of cards played in this vaza (derived from card_plays)"""
        return [card for _, card in self.card_plays]
    
    @property
    def play_order(self) -> list[int]:
        """Get list of player indices in play order (derived from card_plays)"""
        return [player_idx for player_idx, _ in self.card_plays]


class Round:
    def __init__(self, round_type: str = "vazas", players: list[GamePlayer] = None) -> None:
        """
        Initialize a new round of the card game.
        
        Parameters
        ----------
        round_type : str, optional
            Type of round being played. Valid values are: "vazas", "copas",
            "homens", "mulheres", "king", "last", "nulos", "festa1", "festa2",
            "festa3", "festa4" (default is "vazas").
        players : list, optional
            List of 4 GamePlayer objects (default is None).
        
        Notes
        -----
        For festa rounds ("festa1", "festa2", "festa3", "festa4"), the user
        will be prompted to select a trump suit.
        """
        self.deck = Deck()
        self.player_hands = self.deck.distribute(4)  # Active hands (cards get removed)
        self.round_type = round_type
        self.players = players if players else []
        self.vazas_won = [0, 0, 0, 0]     # Track vazas won per player
        self.cards_won: list[list[Card]] = [[], [], [], []] # Track cards won per player
        self.starting_player = 0  # Will be set in start()
        self.vazas_history: list[Vaza] = []           # History of all vazas
        self.current_vaza: Vaza = None          # Current vaza being played
        self.trump_suit = None  # Trump suit for festa positivos
        if round_type in ["festa1", "festa2", "festa3", "festa4"]:
            self.trump_suit = self._select_trump_suit(round_type)
    
    def start(self):
        """
        Start the round by selecting starting player and inputting AI hands.
        """
        # Select starting player
        self.starting_player = self._select_starting_player()
        
        # Input cards dealt in real life
        input("Press Enter when cards are dealt in real life...")
        
        # Input AI hands
        print("=" * 80)
        print("INPUT AI PLAYER HANDS")
        print("=" * 80)
        print("Enter the 13 cards dealt to each AI player in real life.")
        print("This allows the AI to make decisions based on their actual hand.\n")
        
        for player_idx in range(4):
            if self.players[player_idx].is_ai:
                hand = self._input_ai_hand(self.players[player_idx].name)
                self.player_hands[player_idx] = hand
        
        print("All AI hands configured!\n")
    
    def _input_ai_hand(self, player_name: str) -> list[Card]:
        """Input the actual cards dealt to one AI player in real life"""
        print(f"{player_name}'s hand (13 cards):")
        print("  Enter cards separated by spaces (e.g., AH KS 7D 10C ...)")
        print("  Or type 'help' for card format examples\n")
        
        while True:
            cards_input = input(f"  Cards for {player_name}: ").strip()
            
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
            cards: list[Card] = []
            invalid = False
            for card_str in card_strings:
                card = Card.from_string(card_str)
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
            
            print(f"  ✓ Hand set for {player_name}: {self._display_card_list(cards)}\n")
            return cards
    
    def _display_card_list(self, cards: list[Card], sort: bool = True) -> str:
        """Format a list of cards for display"""
        if sort:
            cards = sorted(cards, key=lambda c: (c.suit.value, c.rank.value))
        return ", ".join([str(card) for card in cards])
    
    def _select_starting_player(self) -> int:
        """Let user choose which player starts the round"""
        print("=" * 80)
        print("SELECT STARTING PLAYER")
        print("=" * 80)
        print("Who should start this round?\n")
        
        for i, player in enumerate(self.players):
            print(f"  [{i+1}] {player.name}")
        
        print()
        while True:
            choice = input(f"Select starting player (1-4) [default: 1]: ").strip()
            
            if choice == '':
                print(f"\n✓ {self.players[0].name} will start this round\n")
                return 0
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < 4:
                    print(f"\n✓ {self.players[idx].name} will start this round\n")
                    return idx
            
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")
    
    def _select_trump_suit(self, round_type: str) -> Suit:
        """
        Ask the user to select a trump suit for festa rounds.
        
        Parameters
        ----------
        round_type : str
            The type of round (e.g., "festa1", "festa2", etc.).
        
        Returns
        -------
        Suit
            The selected trump suit.
        
        Notes
        -----
        Prompts the user to enter a suit number (1-4) and validates the input.
        """
        print(f"\n{round_type.upper()}: Select a trump suit:")
        print("1. Hearts")
        print("2. Diamonds")
        print("3. Clubs")
        print("4. Spades")
        
        while True:
            try:
                choice = input("Enter your choice (1-4): ").strip()
                choice_int = int(choice)
                
                if choice_int == 1:
                    return Suit.HEARTS
                elif choice_int == 2:
                    return Suit.DIAMONDS
                elif choice_int == 3:
                    return Suit.CLUBS
                elif choice_int == 4:
                    return Suit.SPADES
                else:
                    print("Invalid choice. Please enter a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 4.")

    
    def start_vaza(self) -> Vaza:
        """Start a new vaza"""
        vaza_number = len(self.vazas_history)
        self.current_vaza = Vaza(vaza_number, self.starting_player)
        return self.current_vaza
    
    def play_card(self, player_idx: int, card: Card) -> None:
        """
        Play a card in the current vaza.
        
        Parameters
        ----------
        player_idx : int
            Index of the player playing the card.
        card : Card
            The card being played.
        """
        if self.current_vaza is None:
            raise ValueError("No active vaza to play card in")
        
        self.current_vaza.card_plays.append((player_idx, card))
        
        # Set main suit from first card
        if self.current_vaza.main_suit is None:
            self.current_vaza.main_suit = card.suit
    
    def get_vaza_winner(self) -> int:
        """
        Determine the winner of the current vaza and update round state.
        
        Returns
        -------
        int
            Index of the player who won this vaza.
        """
        if self.current_vaza is None:
            raise ValueError("No active vaza to determine winner")
        
        # Check for trump suit cards first (if trump suit is defined)
        if self.trump_suit is not None:
            trump_cards = [
                (i, card) for i, card in enumerate(self.current_vaza.cards_played)
                if card.suit == self.trump_suit
            ]
            
            if trump_cards:
                # Trump cards present - highest trump wins
                winner_position, highest_card = max(trump_cards, key=lambda x: x[1].rank.value)
                winner_player = self.current_vaza.play_order[winner_position]
                
                # Update state
                self.current_vaza.winner = winner_player
                self.vazas_won[winner_player] += 1
                self.cards_won[winner_player].extend(self.current_vaza.cards_played)
                self.starting_player = winner_player
                self.vazas_history.append(self.current_vaza)
                self.current_vaza = None
                
                return winner_player
        
        # No trump cards or no trump suit - highest card of main suit wins
        main_suit_cards = [
            (i, card) for i, card in enumerate(self.current_vaza.cards_played)
            if card.suit == self.current_vaza.main_suit
        ]
        
        if not main_suit_cards:
            raise ValueError("No cards of main suit found in vaza - should not happen")
        
        # Get the highest card of the main suit
        winner_position, highest_card = max(main_suit_cards, key=lambda x: x[1].rank.value)
        winner_player = self.current_vaza.play_order[winner_position]
        
        # Update state
        self.current_vaza.winner = winner_player
        self.vazas_won[winner_player] += 1
        self.cards_won[winner_player].extend(self.current_vaza.cards_played)
        self.starting_player = winner_player
        self.vazas_history.append(self.current_vaza)
        self.current_vaza = None
        
        return winner_player
    
    def get_play_order(self) -> list[int]:
        """
        Get the order in which players play this vaza (clockwise from starter)
        Returns: [starter, starter+1, starter+2, starter+3] (mod 4)
        """
        return [(self.starting_player + i) % 4 for i in range(4)]
    
    def get_next_vaza_info(self) -> dict:
        """Get info about the next vaza to be played"""
        return {
            'vaza_number': len(self.vazas_history) + 1,
            'starter': self.starting_player,
            'play_order': self.get_play_order()
        }
    
    def get_player_hand(self, player: int) -> list[Card]:
        """Get current hand for a player"""
        return self.player_hands[player]
    
    def get_valid_plays(self, player: int) -> list[Card]:
        """
        Get valid cards a player can play based on suit-following rules.
        """
        hand = self.player_hands[player]
        
        if not hand:
            return []
        
        # If vaza hasn't started yet or no main suit, all cards are valid
        if self.current_vaza is None or self.current_vaza.main_suit is None:
            return hand.copy()
        
        # Check what cards the player has
        has_main_suit = any(c.suit == self.current_vaza.main_suit for c in hand)
        
        valid = []
        
        for card in hand:
            if self.round_type == "copas":
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    continue
                has_hearts = any(c.suit == Suit.HEARTS for c in hand)
                if not has_main_suit and has_hearts and card.suit != Suit.HEARTS:
                    continue
                valid.append(card)
            elif self.round_type == "homens":
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    continue
                has_men = any(c.rank == Rank.JACK or c.rank == Rank.KING for c in hand)
                if not has_main_suit and has_men and card.rank not in [Rank.JACK, Rank.KING]:
                    continue
                valid.append(card)
            elif self.round_type == "mulheres":
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    continue
                has_women = any(c.rank == Rank.QUEEN for c in hand)
                if not has_main_suit and has_women and card.rank != Rank.QUEEN:
                    continue
                valid.append(card)
            else:
                # Default: follow suit
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    continue
                valid.append(card)
        
        return valid if valid else hand.copy()  # If no valid by rules, can play anything
    
    def _is_man(self, card: Card) -> bool:
        """Check if card is a 'man' (jack or king)"""
        return card.rank == Rank.JACK or card.rank == Rank.KING
    
    def _is_woman(self, card: Card) -> bool:
        """Check if card is a 'woman' (queen)"""
        return card.rank == Rank.QUEEN
    
    def _is_king_of_hearts(self, card: Card) -> bool:
        """Check if card is the King of Hearts"""
        return card.rank == Rank.KING and card.suit == Suit.HEARTS
    
    def play_card(self, player: int, card: Card) -> bool:
        """
        Player plays a card. Returns True if successful, False if invalid.
        Removes card from player's hand and records it in current vaza.
        Enforces suit-following rules based on round type.
        """
        if card not in self.player_hands[player]:
            return False  # Player doesn't have this card
        
        # If main suit is set, check forced play rules
        if self.current_vaza.main_suit is not None:
            # Check what cards player has
            has_main_suit = any(c.suit == self.current_vaza.main_suit for c in self.player_hands[player])
            has_hearts = any(c.suit == Suit.HEARTS for c in self.player_hands[player])
            has_men = any(self._is_man(c) for c in self.player_hands[player])
            has_women = any(self._is_woman(c) for c in self.player_hands[player])
            
            if self.round_type == "copas":
                # In copas: must play main suit, else must play hearts, else anything
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    return False  # Must play main suit
                if not has_main_suit and has_hearts and card.suit != Suit.HEARTS:
                    return False  # Must play hearts if no main suit
            elif self.round_type == "homens":
                # In homens: must play main suit, else must play men (jacks/kings), else anything
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    return False  # Must play main suit
                if not has_main_suit and has_men and not self._is_man(card):
                    return False  # Must play men (jack or king) if no main suit
            elif self.round_type == "mulheres":
                # In mulheres: must play main suit, else must play women (queens), else anything
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    return False  # Must play main suit
                if not has_main_suit and has_women and not self._is_woman(card):
                    return False  # Must play women (queen) if no main suit
            else:
                # Default rule: must play main suit if you have it
                if has_main_suit and card.suit != self.current_vaza.main_suit:
                    return False  # Must follow suit
        
        # Set main suit from first card played in this vaza
        if self.current_vaza.main_suit is None:
            self.current_vaza.main_suit = card.suit
        
        self.player_hands[player].remove(card)
        self.current_vaza.play(player, card)
        return True
    
    def complete_vaza(self) -> int:
        """
        Completes current vaza. Determines winner, updates vazas_won, 
        sets next starting_player, saves vaza to history.
        Winner is the highest trump card (if any), else highest card of main suit.
        Returns: index of the player who won this vaza
        """
        # Check for trump suit cards first (if trump suit is defined)
        if self.trump_suit is not None:
            trump_cards = [
                (i, card) for i, card in enumerate(self.current_vaza.cards_played)
                if card.suit == self.trump_suit
            ]
            
            if trump_cards:
                # Trump cards present - highest trump wins
                winner_position, highest_card = max(trump_cards, key=lambda x: x[1].rank.value)
                winner_player = self.current_vaza.play_order[winner_position]
                
                self.current_vaza.winner = winner_player
                self.vazas_won[winner_player] += 1
                self.cards_won[winner_player].extend(self.current_vaza.cards_played)
                self.starting_player = winner_player
                self.vazas_history.append(self.current_vaza)
                self.current_vaza = None
                
                return winner_player
        
        # No trump cards or no trump suit - highest card of main suit wins
        main_suit_cards = [
            (i, card) for i, card in enumerate(self.current_vaza.cards_played)
            if card.suit == self.current_vaza.main_suit
        ]
        
        if not main_suit_cards:
            raise ValueError("No cards of main suit found in vaza - should not happen")
        
        # Get the highest card of the main suit
        winner_position, highest_card = max(main_suit_cards, key=lambda x: x[1].rank.value)
        winner_player = self.current_vaza.play_order[winner_position]
        
        self.current_vaza.winner = winner_player
        self.vazas_won[winner_player] += 1
        
        # Track cards won by this player
        self.cards_won[winner_player].extend(self.current_vaza.cards_played)
        
        self.starting_player = winner_player
        
        # Save to history
        self.vazas_history.append(self.current_vaza)
        self.current_vaza = None
        
        return winner_player
    
    def is_round_over(self) -> bool:
        """Check if all cards have been played"""
        return all(len(hand) == 0 for hand in self.player_hands)
    
    def count_suit(self, player: int, suit: Suit) -> int:
        """Count how many cards of a specific suit a player won"""
        return sum(1 for card in self.cards_won[player] if card.suit == suit)
    
    def count_rank(self, player: int, rank: Rank) -> int:
        """Count how many cards of a specific rank a player won"""
        return sum(1 for card in self.cards_won[player] if card.rank == rank)
