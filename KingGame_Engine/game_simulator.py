from deck import Card, Suit, Rank


class Vaza:
    def __init__(self, vaza_number: int, starter: int):
        self.vaza_number = vaza_number
        self.starter = starter
        self.cards_played: list[Card] = []    # Cards in play order
        self.play_order: list[int] = []      # Player indices in play order
        self.main_suit: Suit = None     # Suit of first card played
        self.winner: int = None


class Round:
    def __init__(self, player_hands: list[list[Card]], round_type: str = "vazas", starting_player: int = 0, trump_suit: Suit = None):
        """
        player_hands: list of 4 lists, each containing 13 Cards for that player
        round_type: "vazas", "copas", "homens", "mulheres", "king", "last", "nulos"
        starting_player: index of player who starts the first vaza (0-3)
        trump_suit: optional trump suit that beats all other suits (for festa positivos)
        """
        self.player_hands = player_hands  # Active hands (cards get removed)
        self.round_type = round_type
        self.vazas_won = [0, 0, 0, 0]     # Track vazas won per player
        self.cards_won: list[list[Card]] = [[], [], [], []] # Track cards won per player
        self.vaza_starter = starting_player  # Which player starts current vaza
        self.vazas_history: list[Vaza] = []           # History of all vazas
        self.current_vaza: Vaza = None          # Current vaza being played
        self.trump_suit = trump_suit  # Trump suit for festa positivos
    
    def start_vaza(self) -> Vaza:
        """Start a new vaza"""
        vaza_number = len(self.vazas_history) + 1
        self.current_vaza = Vaza(vaza_number, self.vaza_starter)
        return self.current_vaza
    
    def get_play_order(self) -> list[int]:
        """
        Get the order in which players play this vaza (clockwise from starter)
        Returns: [starter, starter+1, starter+2, starter+3] (mod 4)
        """
        return [(self.vaza_starter + i) % 4 for i in range(4)]
    
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
        self.current_vaza.cards_played.append(card)
        self.current_vaza.play_order.append(player)
        return True
    
    def complete_vaza(self) -> int:
        """
        Completes current vaza. Determines winner, updates vazas_won, 
        sets next vaza_starter, saves vaza to history.
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
                self.vaza_starter = winner_player
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
        
        self.vaza_starter = winner_player
        
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
