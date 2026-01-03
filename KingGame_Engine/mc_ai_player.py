import random
from copy import deepcopy
from deck import Card, Suit, Rank, Deck
from game_simulator import Vaza, Round
from ai_player import AIPlayer
from point_manager import PointManager
from game_player import GamePlayer


class MonteCarloAI:
    """
    Monte Carlo Tree Search AI for King game.
    
    Strategy:
    1. For each valid card to play
    2. Simulate 100 games where we play that card
    3. In each simulation, randomly estimate opponent hands
    4. Calculate average score for that card
    5. Choose card with best (lowest) average score
    """
    
    def __init__(self, player: GamePlayer, current_round: Round,
                 num_simulations: int = 100):
        """
        Args:
            player: The GamePlayer object representing this AI
            current_round: The Round object being played
            num_simulations: How many simulations to run per card (higher = smarter but slower)
        """
        self.player = player
        self.my_player_index = player.id
        self.current_round = current_round
        self.round_type = current_round.round_type
        self.num_simulations = num_simulations
        self.point_manager = PointManager()
        
        # Input AI hand from user
        self.my_hand: list[Card] = self._input_ai_hand(player.name)
        
        # Initialize hand estimates: list of possible cards for each player
        self.player_hand_estimates: list[list[Card]] = self._initialize_hand_estimates()
    
    def _input_ai_hand(self, player_name: str) -> list[Card]:
        """
        Input the actual cards dealt to this AI player in real life.
        
        Parameters
        ----------
        player_name : str
            Name of the AI player.
        
        Returns
        -------
        list[Card]
            List of 13 cards in the AI's hand.
        """
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
            
            # Sort and display
            sorted_cards = sorted(cards, key=lambda c: (c.suit.value, c.rank.value))
            cards_str = ", ".join([str(card) for card in sorted_cards])
            print(f"  ✓ Hand set for {player_name}: {cards_str}\n")
            return cards
    
    def _initialize_hand_estimates(self) -> list[list[Card]]:
        """
        Initialize hand estimates for all players.
        
        For the AI player (self.my_player_index), use the known hand (self.my_hand).
        For other players, start with all 52 cards minus AI's known hand.
        
        Returns
        -------
        list[list[Card]]
            List of 4 elements, each containing possible cards for that player.
        """
        estimates: list[list[Card]] = [[] for _ in range(4)]
        
        # Get AI's known hand
        estimates[self.my_player_index] = self.my_hand.copy()
        
        # Build my hand as set for exclusion
        my_hand_set: set[tuple[Suit, Rank]] = {(c.suit, c.rank) for c in self.my_hand}
        
        # Get all 52 possible cards
        all_cards = Deck.get_all_cards()
        all_cards_set: set[tuple[Suit, Rank]] = {(c.suit, c.rank) for c in all_cards}
        
        # Unknown cards = all cards - my hand
        unknown_cards_set = all_cards_set - my_hand_set
        unknown_cards = [Card(suit, rank) for suit, rank in unknown_cards_set]
        
        # For other players, they could have any of the unknown cards
        for i in range(4):
            if i != self.my_player_index:
                estimates[i] = unknown_cards.copy()
        
        return estimates
    
    def update_hand_estimates(self, current_vaza: Vaza) -> None:
        """
        Update hand estimates by removing cards that were played in current vaza.
        
        Parameters
        ----------
        current_vaza : Vaza
            The current vaza with cards_played and play_order information.
        
        Notes
        -----
        When a card is played, it must be removed from ALL players' hand estimates
        since no one else can have that card once it's been played.
        """
        if not current_vaza or not current_vaza.cards_played:
            return
        
        # Remove played cards from ALL players' hand estimates
        for card in current_vaza.cards_played:
            for player_idx in range(4):
                if player_idx != self.my_player_index:
                    # Remove the played card from this player's possible cards
                    self.player_hand_estimates[player_idx] = [
                        c for c in self.player_hand_estimates[player_idx]
                        if not (c.suit == card.suit and c.rank == card.rank)
                    ]
    
    def choose_card(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Choose which card to play using heuristic AI strategy.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that are legal to play (already filtered by Round).
        current_vaza : Vaza
            Current vaza with cards played so far.
        
        Returns
        -------
        Card
            The card to play.
        
        Notes
        -----
        Currently uses the heuristic AI from AIPlayer which has built-in
        strategies for each round type. This provides a working baseline
        that can later be enhanced with Monte Carlo simulation.
        """
        # Use heuristic AI for decision making
        ai = AIPlayer(self.my_hand, self.round_type)
        return ai.choose_card(valid_plays, current_vaza)
