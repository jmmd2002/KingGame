import random
from enum import Enum


class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(Enum):
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
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self) -> str:
        return f"{self.rank.value}{self.suit.name[0]}"


class Deck:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.cards = []
        self._create_deck()
    
    def _create_deck(self):
        """Create all 52 cards and shuffle"""
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)
    
    def reset(self):
        """Reset the deck (recreate and reshuffle)"""
        self._create_deck()
    
    def distribute(self) -> list[list[Card]]:
        """
        Distribute cards evenly to 4 players.
        Returns a list of 4 player hands (each hand is a list of 13 Cards)
        """
        hands = [[] for _ in range(4)]
        
        for i, card in enumerate(self.cards):
            player_index = i % 4
            hands[player_index].append(card)
        
        return hands