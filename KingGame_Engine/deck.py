import random
from enum import Enum


class Suit(Enum):
    """
    Enumeration of the four card suits in a standard deck.
    
    Attributes
    ----------
    HEARTS : str
        Hearts suit.
    DIAMONDS : str
        Diamonds suit.
    CLUBS : str
        Clubs suit.
    SPADES : str
        Spades suit.
    """
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(Enum):
    """
    Enumeration of the thirteen card ranks in a standard deck.
    
    Attributes
    ----------
    TWO to ACE : int
        Card ranks with integer values from 2 to 14, where face cards
        are Jack (11), Queen (12), King (13), and Ace (14).
    """
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    """
    Represents a single playing card.
    
    A card is defined by its suit and rank. Cards can be compared for
    equality and used in sets/dictionaries via hashing.
    
    Attributes
    ----------
    suit : Suit
        The suit of the card (Hearts, Diamonds, Clubs, or Spades).
    rank : Rank
        The rank of the card (2-10, Jack, Queen, King, or Ace).
    
    Methods
    -------
    __repr__()
        Return a string representation of the card.
    __eq__(other)
        Compare two cards for equality based on suit and rank.
    __hash__()
        Return hash value for use in sets and dictionaries.
    """
    
    def __init__(self, suit: Suit, rank: Rank) -> None:
        """
        Initialize a card with a suit and rank.
        
        Parameters
        ----------
        suit : Suit
            The suit of the card.
        rank : Rank
            The rank of the card.
        """
        self.suit = suit
        self.rank = rank
    
    def __repr__(self) -> str:
        return f"{self.rank.value}{self.suit.name[0]}"
    
    def __eq__(self, other: "Card") -> bool:
        """
        Compare two cards for equality.
        
        Two cards are considered equal if they have the same suit and rank,
        regardless of object identity.
        
        Parameters
        ----------
        other : object
            The object to compare with this card.
        
        Returns
        -------
        bool
            True if other is a Card with the same suit and rank, False otherwise.
        """
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self) -> int:
        """
        Generate a hash value for the card.
        
        This allows Card objects to be used in sets and as dictionary keys.
        The hash is based on the combination of suit and rank, ensuring that
        cards with the same suit and rank have the same hash value.
        
        Returns
        -------
        int
            Hash value computed from the card's suit and rank.
        
        Notes
        -----
        Required when implementing __eq__ to maintain the invariant that
        objects that compare equal must have the same hash value.
        """
        return hash((self.suit, self.rank))
    
    @staticmethod
    def from_string(card_str: str) -> "Card | None":
        """
        Parse a card from string format.
        
        Converts string representations like '1H', '13S', 'AH', 'KS' into Card objects.
        
        Parameters
        ----------
        card_str : str
            String representation of a card. Accepted formats:
            - Number + Suit: '2H', '10D', '13C', '14S' (rank value 2-14 + suit)
            - Letter + Suit: 'AH' (Ace), 'KS' (King), 'QD' (Queen), 'JC' (Jack)
            Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades
        
        Returns
        -------
        Card or None
            Card object if parsing succeeds, None if the string is invalid.
        
        Examples
        --------
        >>> Card.from_string('AH')  # Ace of Hearts
        >>> Card.from_string('10D')  # 10 of Diamonds
        >>> Card.from_string('KS')  # King of Spades
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
        rank: Rank | None = None
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

class Deck:
    """
    A standard 52-card deck for card games.
    
    This class manages a deck of playing cards, providing functionality
    to create, shuffle, reset, and distribute cards to players.
    
    Attributes
    ----------
    cards : list[Card]
        List containing all cards in the deck.
    
    Methods
    -------
    reset()
        Reset the deck by recreating and reshuffling all cards.
    distribute(num_players, distribute_remainder=True)
        Distribute cards to a specified number of players.
    """
    
    def __init__(self, seed: int | None = None) -> None:
        """
        Initialize a new deck of cards.
        
        Parameters
        ----------
        seed : int, optional
            Random seed for reproducible shuffling. If None, shuffling
            will be non-deterministic (default is None).
        
        Notes
        -----
        The deck is automatically created and shuffled during initialization.
        """
        if seed is not None:
            random.seed(seed)
        self.cards = []
        self._create_deck()
    
    def _create_deck(self) -> None:
        """
        Create all 52 cards and shuffle the deck.
        
        This private method generates one card for each combination of
        suit and rank, then shuffles the entire deck randomly.
        
        Notes
        -----
        This method clears any existing cards and creates a fresh deck
        of 52 cards (4 suits × 13 ranks).
        """
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)
    
    def reset(self) -> None:
        """
        Reset the deck by recreating and reshuffling all cards.
        
        This method clears the current deck state and generates a fresh,
        shuffled deck of 52 cards.
        
        Notes
        -----
        Useful for starting a new game without creating a new Deck instance.
        """
        self._create_deck()
    
    def distribute(self, num_players: int, distribute_remainder: bool = True) -> list[list[Card]]:
        """
        Distribute cards to players.
        
        Parameters
        ----------
        num_players : int
            Number of players to distribute cards to.
        distribute_remainder : bool, optional
            If True, distributes remainder cards one per player in round-robin fashion.
            If False, discards remainder cards that don't divide evenly (default is True).
        
        Returns
        -------
        list[list[Card]]
            List of player hands, where each hand is a list of Cards.
        
        Notes
        -----
        When cards don't divide evenly among players, the behavior depends on
        distribute_remainder. For example, with 52 cards and 5 players:
        - If True: 4 players get 11 cards, 1 player gets 8 cards
        - If False: all 5 players get 10 cards, 2 cards are discarded
        """
        hands: list[list[Card]] = [[] for _ in range(num_players)]
        
        if distribute_remainder:
            # Distribute all cards in round-robin fashion
            for i, card in enumerate(self.cards):
                player_index = i % num_players
                hands[player_index].append(card)
        else:
            # Only distribute cards that divide evenly
            cards_per_player = len(self.cards) // num_players
            for i in range(num_players):
                start_idx = i * cards_per_player
                end_idx = start_idx + cards_per_player
                hands[i] = self.cards[start_idx:end_idx]
        
        return hands