from deck import Card, Deck, Suit, Rank
from game_player import GamePlayer
from point_manager import PointManager


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
    card_plays : list[tuple[int, Card]]
        List of (player_index, card) tuples representing plays in order.
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
        self.vaza_number: int = vaza_number
        self.starter: int = starter
        self.card_plays: list[tuple[int, Card]] = []
        self.main_suit: Suit = None
        self.winner: int = None
    
    @property
    def cards_played(self) -> list[Card]:
        """
        Get list of cards played in this vaza (derived from card_plays).
        
        Returns
        -------
        list[Card]
            Cards in play order.
        """
        return [card for _, card in self.card_plays]
    
    @property
    def play_order(self) -> list[int]:
        """
        Get list of player indices in play order (derived from card_plays).
        
        Returns
        -------
        list[int]
            Player indices in the order they played cards.
        """
        return [player_idx for player_idx, _ in self.card_plays]


class Round:
    """
    Represents a single round of the King card game.
    
    Manages the state and logic for one complete round (13 vazas). Tracks
    which cards have been won by each player, validates plays, and calculates
    points based on the round type.
    
    Attributes
    ----------
    round_type : str
        Type of round being played ("vazas", "copas", "homens", "mulheres", "king", "last").
    players : list[GamePlayer]
        List of 4 GamePlayer objects.
    vazas_won : list[int]
        Count of vazas won by each player [p0, p1, p2, p3].
    cards_won : list[list[Card]]
        Cards won by each player [[p0_cards], [p1_cards], [p2_cards], [p3_cards]].
    starting_player : int
        Index (0-3) of the player who starts the current vaza.
    vazas_history : list[Vaza]
        History of all completed vazas in this round.
    current_vaza : Vaza or None
        The vaza currently being played (None if no active vaza).
    trump_suit : Suit or None
        Trump suit for festa rounds (None for non-festa rounds).
    """
    
    def __init__(self, round_type: str = "vazas", players: list[GamePlayer] = None) -> None:
        """
        Initialize a new round of the card game.
        
        Parameters
        ----------
        round_type : str, optional
            Type of round being played. Valid values are: "vazas", "copas",
            "homens", "mulheres", "king", "last", "nulos", "festa1", "festa2",
            "festa3", "festa4" (default is "vazas").
        players : list[GamePlayer], optional
            List of 4 GamePlayer objects (default is None).
        
        Notes
        -----
        For festa rounds ("festa1", "festa2", "festa3", "festa4"), the user
        will be prompted to select a trump suit.
        """
        self.round_type: str = round_type
        self.players: list[GamePlayer] = players if players else []
        self.vazas_won: list[int] = [0, 0, 0, 0]
        self.cards_won: list[list[Card]] = [[], [], [], []]
        self.starting_player: int = 0
        self.vazas_history: list[Vaza] = []
        self.current_vaza: Vaza = None
        self.trump_suit: Suit = None
        
        if round_type in ["festa1", "festa2", "festa3", "festa4"]:
            self.trump_suit = self._select_trump_suit(round_type)
    
    def start(self) -> None:
        """
        Start the round by selecting starting player.
        
        Prompts user to select which player will start the round,
        then waits for cards to be dealt in real life.
        """
        self.starting_player = self._select_starting_player()
        input("Press Enter when cards are dealt in real life...")
    
    def _select_starting_player(self) -> int:
        """
        Let user choose which player starts the round.
        
        Returns
        -------
        int
            Index (0-3) of the player who will start the round.
        
        Notes
        -----
        Provides an interactive prompt for player selection with validation.
        """
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
        """
        Start a new vaza.
        
        Returns
        -------
        Vaza
            The newly created vaza object.
        """
        vaza_number = len(self.vazas_history)
        self.current_vaza = Vaza(vaza_number, self.starting_player)
        return self.current_vaza
    
    def play_card(self, player_idx: int, card: Card) -> None:
        """
        Play a card in the current vaza.
        
        Parameters
        ----------
        player_idx : int
            Index (0-3) of the player playing the card.
        card : Card
            The card being played.
        
        Raises
        ------
        ValueError
            If no active vaza exists to play the card in.
        
        Notes
        -----
        Does not enforce suit-following rules - validation should be done externally
        using get_valid_plays(). Sets the main suit from the first card played.
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
            Index (0-3) of the player who won this vaza.
        
        Raises
        ------
        ValueError
            If no active vaza exists to determine winner, or if no cards
            of the main suit were found.
        
        Notes
        -----
        Winner determination follows these rules:
        1. If trump suit exists and trump cards were played, highest trump wins
        2. Otherwise, highest card of the main suit wins
        
        Updates vazas_won, cards_won, starting_player, vazas_history, and
        clears current_vaza after determining the winner.
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
                winner_position, _ = max(trump_cards, key=lambda x: x[1].rank.value)
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
        winner_position, _ = max(main_suit_cards, key=lambda x: x[1].rank.value)
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
        Get the order in which players play this vaza (clockwise from starter).
        
        Returns
        -------
        list[int]
            List of player indices in play order [starter, starter+1, starter+2, starter+3] (mod 4).
        """
        return [(self.starting_player + i) % 4 for i in range(4)]
    
    def get_next_vaza_info(self) -> dict[str, int | list[int]]:
        """
        Get info about the next vaza to be played.
        
        Returns
        -------
        dict[str, int | list[int]]
            Dictionary containing:
            - 'vaza_number': Sequential number of next vaza (1-13)
            - 'starter': Index of player who starts next vaza
            - 'play_order': List of player indices in play order
        """
        return {
            'vaza_number': len(self.vazas_history) + 1,
            'starter': self.starting_player,
            'play_order': self.get_play_order()
        }
    
    def can_end_early(self, cards_played_round: list[Card]) -> tuple[bool, str]:
        """
        Check if the current round can end early because all relevant penalty cards have been played.
        
        Parameters
        ----------
        cards_played_round : list[Card]
            List of all cards played in the round so far.
        
        Returns
        -------
        tuple[bool, str]
            A tuple of (can_end, message) where:
            - can_end (bool): True if the round can end early
            - message (str): Explanation message (empty string if can't end early)
        
        Notes
        -----
        Early termination conditions:
        - "copas": All 13 hearts played
        - "homens": All 8 men (4 jacks + 4 kings) played
        - "mulheres": All 4 queens played
        - "king": King of Hearts played
        """
        if self.round_type == "copas":
            hearts_played = sum(1 for c in cards_played_round if c.suit == Suit.HEARTS)
            if hearts_played == 13:
                return True, "\n✓ All hearts have been played. Ending round early.\n"
        
        elif self.round_type == "homens":
            men_played = sum(1 for c in cards_played_round if c.rank in [Rank.JACK, Rank.KING])
            if men_played == 8:
                return True, "\n✓ All jacks and kings have been played. Ending round early.\n"
        
        elif self.round_type == "mulheres":
            queens_played = sum(1 for c in cards_played_round if c.rank == Rank.QUEEN)
            if queens_played == 4:
                return True, "\n✓ All queens have been played. Ending round early.\n"
        
        elif self.round_type == "king":
            king_of_hearts_played = any(
                c.suit == Suit.HEARTS and c.rank == Rank.KING 
                for c in cards_played_round
            )
            if king_of_hearts_played:
                return True, "\n✓ King of Hearts has been played. Ending round early.\n"
        
        return False, ""
    
    def get_valid_plays(self, hand: list[Card]) -> list[Card]:
        """
        Get valid cards that can be played based on suit-following rules.
        
        Parameters
        ----------
        hand : list[Card]
            The player's current hand of cards.
        
        Returns
        -------
        list[Card]
            List of valid cards that can be played according to the rules.
        
        Notes
        -----
        Validation rules vary by round type:
        - Must follow main suit if possible
        - Special rules for copas (must play hearts if can't follow)
        - Special rules for homens (must play jacks/kings if can't follow)
        - Special rules for mulheres (must play queens if can't follow)
        - If no valid cards by rules, all cards become valid
        """
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
                has_men = any(c.rank in [Rank.JACK, Rank.KING] for c in hand)
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
        
        return valid if valid else hand.copy()
    
    def count_suit(self, player: int, suit: Suit) -> int:
        """
        Count how many cards of a specific suit a player won.
        
        Parameters
        ----------
        player : int
            Index (0-3) of the player.
        suit : Suit
            The suit to count.
        
        Returns
        -------
        int
            Number of cards of the specified suit the player won.
        """
        return sum(1 for card in self.cards_won[player] if card.suit == suit)
    
    def count_rank(self, player: int, rank: Rank) -> int:
        """
        Count how many cards of a specific rank a player won.
        
        Parameters
        ----------
        player : int
            Index (0-3) of the player.
        rank : Rank
            The rank to count.
        
        Returns
        -------
        int
            Number of cards of the specified rank the player won.
        """
        return sum(1 for card in self.cards_won[player] if card.rank == rank)
    
    def calculate_points(self) -> list[int]:
        """
        Calculate points for current round based on round type and what was won.
        
        Returns
        -------
        list[int]
            Points for each player [points_p0, points_p1, points_p2, points_p3].
        
        Notes
        -----
        Point calculation varies by round type:
        - "vazas": Based on number of vazas won
        - "copas": Based on number of hearts won
        - "homens": Based on number of jacks and kings won
        - "mulheres": Based on number of queens won
        - "king": Based on having the King of Hearts
        - "last": Based on winning the last 2 vazas (12th and 13th)
        
        Raises
        ------
        NotImplementedError
            If round_type is not recognized.
        """
        if self.round_type == "vazas":
            return [
                PointManager.get_points(self.round_type, self.vazas_won[i])
                for i in range(4)
            ]
        elif self.round_type == "copas":
            hearts_won = [self.count_suit(i, Suit.HEARTS) for i in range(4)]
            return [
                PointManager.get_points(self.round_type, hearts_won[i])
                for i in range(4)
            ]
        elif self.round_type == "homens":
            men_won = [
                self.count_rank(i, Rank.JACK) + self.count_rank(i, Rank.KING)
                for i in range(4)
            ]
            return [
                PointManager.get_points(self.round_type, men_won[i])
                for i in range(4)
            ]
        elif self.round_type == "mulheres":
            women_won = [self.count_rank(i, Rank.QUEEN) for i in range(4)]
            return [
                PointManager.get_points(self.round_type, women_won[i])
                for i in range(4)
            ]
        elif self.round_type == "king":
            king_points = [0, 0, 0, 0]
            for player_idx in range(4):
                for card in self.cards_won[player_idx]:
                    if card.rank == Rank.KING and card.suit == Suit.HEARTS:
                        king_points[player_idx] = PointManager.get_points(self.round_type, 1)
                        break
            return king_points
        elif self.round_type == "last":
            last_two_vazas_won = [0, 0, 0, 0]
            
            # Check the last 2 vazas
            history = self.vazas_history
            if len(history) >= 12:
                winner_12 = history[11].winner
                last_two_vazas_won[winner_12] += 1
            
            if len(history) >= 13:
                winner_13 = history[12].winner
                last_two_vazas_won[winner_13] += 1
            
            return [
                PointManager.get_points(self.round_type, last_two_vazas_won[i])
                for i in range(4)
            ]
        else:
            raise NotImplementedError(f"Round type '{self.round_type}' not implemented yet")
