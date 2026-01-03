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
                 num_simulations: int = 100, pre_dealt_hand: list[Card] = None):
        """
        Args:
            player: The GamePlayer object representing this AI
            current_round: The Round object being played
            num_simulations: How many simulations to run per card (higher = smarter but slower)
            pre_dealt_hand: Optional pre-dealt hand for automated testing (skips user input)
        """
        self.player = player
        self.my_player_index = player.id
        self.current_round = current_round
        self.round_type = current_round.round_type
        self.num_simulations = num_simulations
        self.point_manager = PointManager()
        
        # Input AI hand from user or use pre-dealt hand
        if pre_dealt_hand is not None:
            self.my_hand: list[Card] = pre_dealt_hand.copy()
        else:
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
        Also removes suits from estimates when a player fails to follow suit.
        
        Parameters
        ----------
        current_vaza : Vaza
            The current vaza with cards_played and play_order information.
        
        Notes
        -----
        When a card is played, it must be removed from ALL players' hand estimates
        since no one else can have that card once it's been played.
        
        Additionally, if a player doesn't follow the main suit, they must be out of
        that suit, so we remove all cards of that suit from their estimates.
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
        
        # Check for players who didn't follow suit (revealing they're out of that suit)
        for player_idx, card in current_vaza.card_plays:
            # Skip the AI player (we know our own hand)
            if player_idx == self.my_player_index:
                continue
            
            # If this player didn't follow the main suit, they must be out of it
            if card.suit != current_vaza.main_suit:
                # Remove all cards of the main suit from this player's estimates
                self.player_hand_estimates[player_idx] = [
                    c for c in self.player_hand_estimates[player_idx]
                    if c.suit != current_vaza.main_suit
                ]
                
                # Handle special penalty round rules
                if self.round_type == "copas":
                    # In copas: if they didn't play hearts, they're also out of hearts
                    if card.suit != Suit.HEARTS:
                        self.player_hand_estimates[player_idx] = [
                            c for c in self.player_hand_estimates[player_idx]
                            if c.suit != Suit.HEARTS
                        ]
                elif self.round_type == "homens":
                    # In homens: if they didn't play J/K, they have no J/K
                    if card.rank not in [Rank.JACK, Rank.KING]:
                        self.player_hand_estimates[player_idx] = [
                            c for c in self.player_hand_estimates[player_idx]
                            if c.rank not in [Rank.JACK, Rank.KING]
                        ]
                elif self.round_type == "mulheres":
                    # In mulheres: if they didn't play a Q, they have no queens
                    if card.rank != Rank.QUEEN:
                        self.player_hand_estimates[player_idx] = [
                            c for c in self.player_hand_estimates[player_idx]
                            if c.rank != Rank.QUEEN
                        ]
                elif self.round_type == "king":
                    # In king: if they didn't play KH, they don't have it
                    if not (card.suit == Suit.HEARTS and card.rank == Rank.KING):
                        self.player_hand_estimates[player_idx] = [
                            c for c in self.player_hand_estimates[player_idx]
                            if not (c.suit == Suit.HEARTS and c.rank == Rank.KING)
                        ]
    
    def choose_card(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Choose which card to play using Monte Carlo simulation.
        
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
        Uses Monte Carlo simulation:
        1. For each valid card, run N simulations
        2. In each simulation, randomly assign unknown cards to opponents
        3. Play out the rest of the round using heuristics
        4. Calculate the score
        5. Choose the card with the best average score
        """
        if len(valid_plays) == 1:
            return valid_plays[0]
        
        # Run simulations for each valid card
        card_scores: dict[Card, float] = {}
        
        for card in valid_plays:
            total_score = 0
            
            for _ in range(self.num_simulations):
                # Simulate playing this card and get the resulting score
                sim_score = self._simulate_card_play(card, current_vaza)
                total_score += sim_score
            
            avg_score = total_score / self.num_simulations
            card_scores[card] = avg_score
        
        # Choose card with best (highest/least negative) average score
        best_card = max(card_scores.keys(), key=lambda c: card_scores[c])
        return best_card
    
    def _simulate_card_play(self, card: Card, current_vaza: Vaza) -> float:
        """
        Simulate playing a specific card and return the expected score.
        
        Parameters
        ----------
        card : Card
            The card to simulate playing.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        float
            Estimated score for the AI player if this card is played.
        """
        # Sample opponent hands from estimates
        sampled_hands = self._sample_opponent_hands()
        sampled_hands[self.my_player_index].remove(card)
        
        # Create a copy of the game state
        sim_round = self._create_simulation_round(current_vaza, card)
        
        # Play out the rest of the round
        final_points = self._play_out_simulation(sim_round, sampled_hands)
        
        # Return AI's score
        return final_points[self.my_player_index]
    
    def _sample_opponent_hands(self) -> dict[int, list[Card]]:
        """
        Sample random hands for opponents based on hand estimates.
        
        Uses a constraint-based approach:
        1. Start with players with smallest hand estimates (most constrained)
        2. Deal cards from their possible cards
        3. Remove dealt cards from other players' estimates to avoid duplicates
        
        Returns
        -------
        dict[int, list[Card]]
            Dictionary mapping player index to their sampled hand.
        """
        sampled_hands: dict[int, list[Card]] = {}
        
        # AI's hand is known
        sampled_hands[self.my_player_index] = self.my_hand.copy()
        
        # Determine who has already played in current vaza
        players_who_played = set()
        if self.current_round.current_vaza and self.current_round.current_vaza.card_plays:
            players_who_played = set(player_idx for player_idx, _ in self.current_round.current_vaza.card_plays)
        
        # AI's current hand size
        ai_hand_size = len(self.my_hand)
        
        # Create working copies of estimates for this simulation
        working_estimates: dict[int, list[Card]] = {
            i: [Card(c.suit, c.rank) for c in self.player_hand_estimates[i]]
            for i in range(4)
        }
        
        # Get opponent indices sorted by constraint (smallest estimate first)
        opponent_indices = [i for i in range(4) if i != self.my_player_index]
        opponent_indices.sort(key=lambda i: len(working_estimates[i]))
        
        # Deal cards to each opponent
        for idx, player_idx in enumerate(opponent_indices):
            available_cards = working_estimates[player_idx]
            
            # Calculate how many cards this player needs
            if player_idx in players_who_played:
                # This player already played a card in current vaza
                cards_needed = ai_hand_size - 1
            else:
                # This player hasn't played yet
                cards_needed = ai_hand_size
            
            # Sample from available cards
            if len(available_cards) < cards_needed:
                # Not enough cards - use what we have
                sampled = available_cards.copy()
            else:
                sampled = random.sample(available_cards, cards_needed)
            
            sampled_hands[player_idx] = sampled
            
            # Remove sampled cards from remaining players' estimates (not yet dealt)
            for other_idx in opponent_indices[idx + 1:]:
                working_estimates[other_idx] = [
                    c for c in working_estimates[other_idx]
                    if not any(c.suit == sc.suit and c.rank == sc.rank for sc in sampled)
                ]
        
        return sampled_hands
    
    def _create_simulation_round(self, current_vaza: Vaza, card_to_play: Card) -> Round:
        """
        Create a simulation round with current game state.
        
        Parameters
        ----------
        sampled_hands : dict[int, list[Card]]
            Sampled hands for all players.
        current_vaza : Vaza
            Current vaza state.
        card_to_play : Card
            The card the AI is testing.
        
        Returns
        -------
        Round
            A round object ready for simulation.
        """
        # Create a fresh round
        sim_round = Round(self.round_type, self.current_round.players)
        sim_round.starting_player = self.current_round.starting_player
        sim_round.vazas_history = [vaza for vaza in self.current_round.vazas_history]
        
        # Copy current vaza state
        if current_vaza and current_vaza.cards_played:
            sim_round.current_vaza = Vaza(current_vaza.vaza_number, current_vaza.starter)
            sim_round.current_vaza.card_plays = current_vaza.card_plays.copy()
            sim_round.current_vaza.main_suit = current_vaza.main_suit
            
            # Add the AI's card to the simulation
            sim_round.play_card(self.my_player_index, card_to_play)
        else:
            # Start new vaza with this card
            sim_round.start_vaza()
            sim_round.play_card(self.my_player_index, card_to_play)
        
        return sim_round
    
    def _play_out_simulation(self, sim_round: Round, 
                            sampled_hands: dict[int, list[Card]]) -> list[int]:
        """
        Play out the rest of the round using heuristics.
        
        Parameters
        ----------
        sim_round : Round
            The simulation round.
        sampled_hands : dict[int, list[Card]]
            Hands for all players in this simulation.
        
        Returns
        -------
        list[int]
            Final points for all players.
        """
        # Create AI players for simulation (simple heuristics)
        sim_ai_players: dict[int, AIPlayer] = {}
        for player_idx in range(4):
            sim_ai_players[player_idx] = AIPlayer(
                sampled_hands[player_idx],
                self.round_type
            )
        
        # Complete current vaza if not done
        if sim_round.current_vaza and len(sim_round.current_vaza.cards_played) < 4:
            play_order = sim_round.get_play_order()
            cards_in_vaza = len(sim_round.current_vaza.cards_played)
            
            for i in range(cards_in_vaza, 4):
                player_idx = play_order[i]
                hand = sampled_hands[player_idx]
                
                if not hand:
                    continue
                
                valid_plays = sim_round.get_valid_plays(hand)
                if not valid_plays:
                    continue
                
                card = sim_ai_players[player_idx].choose_card(valid_plays, sim_round.current_vaza)
                sim_round.play_card(player_idx, card)
                hand.remove(card)
            
            # Determine winner
            sim_round.get_vaza_winner()
        
        # Play remaining vazas
        remaining_vazas = 13 - len(sim_round.vazas_history)
        for _ in range(remaining_vazas):
            if all(len(hand) == 0 for hand in sampled_hands.values()):
                break
            
            sim_round.start_vaza()
            play_order = sim_round.get_play_order()
            
            for player_idx in play_order:
                hand = sampled_hands[player_idx]
                
                if not hand:
                    continue
                
                valid_plays = sim_round.get_valid_plays(hand)
                if not valid_plays:
                    continue
                
                card = sim_ai_players[player_idx].choose_card(valid_plays, sim_round.current_vaza)
                sim_round.play_card(player_idx, card)
                hand.remove(card)
            
            # Determine winner
            if sim_round.current_vaza and len(sim_round.current_vaza.cards_played) == 4:
                sim_round.get_vaza_winner()
        
        # Calculate final points
        return sim_round.calculate_points()

