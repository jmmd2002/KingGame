import random
from copy import deepcopy
from deck import Card, Suit, Rank, Deck
from game_simulator import Round
from ai_player import AIPlayer
from point_manager import PointManager


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
    
    def __init__(self, my_player_index: int, round_type: str = "vazas", num_simulations: int = 100, trump_suit: Suit = None, is_nulos: bool = None):
        """
        Args:
            my_player_index: Which player am I (0-3)
            round_type: Current round type
            num_simulations: How many simulations to run per card (higher = smarter but slower)
            trump_suit: Trump suit for festa positivos rounds (optional)
            is_nulos: True for nulos festa, False for positivos festa, None for non-festa rounds
        """
        self.my_player_index = my_player_index
        self.round_type = round_type
        self.is_nulos = is_nulos
        self.num_simulations = num_simulations
        self.trump_suit = trump_suit
        self.point_manager = PointManager()
    
    def _get_adaptive_sim_count(self, hand_size: int, num_valid_plays: int) -> int:
        """
        Adjust simulation count based on game state.
        More simulations when uncertainty is high or round is critical.
        """
        base = self.num_simulations
        
        # Round-specific: think harder on high-stakes rounds
        if self.round_type == "king":
            base = int(base * 2.0)  # King round is critical (-160 pts)
        elif self.round_type in ["festa1", "festa2", "festa3", "festa4"]:
            base = int(base * 1.5)  # Festa rounds have biggest swings (±300 pts)
        elif self.round_type == "last":
            base = int(base * 1.3)  # Last 2 tricks matter (-180 pts total)
        
        # More simulations early in round (more uncertainty)
        if hand_size > 8:
            base = int(base * 1.3)
        
        # More simulations with many choices
        if num_valid_plays > 5:
            base = int(base * 1.2)
        
        return min(base, 300)  # Cap at 300
    
    def choose_card(self, my_hand: list[Card], valid_plays: list[Card], 
                   cards_played_this_round: list[Card], current_vaza) -> Card:
        """
        Main decision function.
        
        Args:
            my_hand: Cards I currently have
            valid_plays: Cards I'm allowed to play (already filtered by Round)
            cards_played_this_round: All cards played so far this round
            current_vaza: Current Vaza object with cards played this vaza
        
        Returns:
            Best Card to play
        """
        
        # Edge case: only one valid play
        if len(valid_plays) == 1:
            return valid_plays[0]
        
        # Use adaptive simulation count based on game state
        num_sims = self._get_adaptive_sim_count(len(my_hand), len(valid_plays))
        
        # (Verbose output disabled for cleaner testing)
        
        best_card = None
        best_score = float('inf')
        card_scores = {}
        
        # Evaluate each valid play
        for card in valid_plays:
            total_points = 0
            
            # Run multiple simulations for this card
            for sim in range(num_sims):
                # Step 1: Estimate what opponents have
                # Exclude cards played in current vaza as well
                cards_played_in_current_vaza = current_vaza.cards_played if current_vaza else []
                players_who_played = current_vaza.play_order if current_vaza else []
                
                opponent_hands = self._estimate_opponent_hands(
                    my_hand, 
                    cards_played_this_round,
                    cards_played_in_current_vaza,
                    players_who_played
                )
                
                # Step 2: Simulate playing this card and see the outcome
                points = self._simulate_game(
                    card_to_play=card,
                    my_hand=my_hand,
                    cards_played_this_round=cards_played_this_round,
                    opponent_hands=opponent_hands,
                    current_vaza=current_vaza
                )
                
                total_points += points
            
            # Calculate average score for this card
            avg_score = total_points / self.num_simulations
            card_scores[card] = avg_score
            
            # Track best card (lowest score = best, since negative points)
            if avg_score < best_score:
                best_score = avg_score
                best_card = card
        
        return best_card
    
    def _estimate_opponent_hands(self, my_hand: list[Card], cards_played_this_round: list[Card], 
                                cards_played_in_current_vaza: list[Card] = None,
                                players_who_played_in_vaza: list[int] = None) -> dict:
        """
        Estimate what cards opponents have.
        
        Logic:
        1. Create list of all 52 cards
        2. Remove my hand and cards already played
        3. Distribute remaining cards to opponents who haven't played yet
        
        Args:
            my_hand: Cards I'm holding (from actual game)
            cards_played_this_round: All cards played so far in this round
            cards_played_in_current_vaza: Cards already played in current vaza
            players_who_played_in_vaza: List of player indices who have already played this vaza
        
        Returns:
            dict: {player_index: list[Card]}
        """
        
        if cards_played_in_current_vaza is None:
            cards_played_in_current_vaza = []
        if players_who_played_in_vaza is None:
            players_who_played_in_vaza = []
        
        # Build set of (suit, rank) tuples for comparison (object-independent)
        my_hand_set = {(c.suit, c.rank) for c in my_hand}
        cards_played_set = {(c.suit, c.rank) for c in cards_played_this_round}
        current_vaza_set = {(c.suit, c.rank) for c in cards_played_in_current_vaza}
        
        # Get all 52 possible cards as (suit, rank) tuples
        all_card_tuples = set()
        for suit in Suit:
            for rank in Rank:
                all_card_tuples.add((suit, rank))
        
        # Find unknown cards
        unknown_tuples = all_card_tuples - my_hand_set - cards_played_set - current_vaza_set
        unknown_cards = [Card(suit, rank) for suit, rank in unknown_tuples]
        
        # Identify opponents who HAVEN'T played in current vaza yet
        players_who_havent_played = [
            i for i in range(4) 
            if i != self.my_player_index and i not in players_who_played_in_vaza
        ]
        
        # Start distributing to those who haven't played
        opponent_hands = {}
        
        # Initialize all opponents with empty hands first
        for opponent_index in range(4):
            if opponent_index != self.my_player_index:
                opponent_hands[opponent_index] = []
        
        remaining_copy = unknown_cards.copy()
        
        # Calculate distribution for players who haven't played
        if len(players_who_havent_played) > 0:
            total_remaining = len(unknown_cards)
            num_to_distribute_to = len(players_who_havent_played)
            
            cards_per_player = total_remaining // num_to_distribute_to
            remainder = total_remaining % num_to_distribute_to
            
            for i, opponent_index in enumerate(players_who_havent_played):
                cards_to_give = cards_per_player
                if i < remainder:  # Extra cards go to first few in play order
                    cards_to_give += 1
                
                if cards_to_give > 0 and remaining_copy:
                    cards_to_take = min(cards_to_give, len(remaining_copy))
                    opponent_hand = random.sample(remaining_copy, cards_to_take)
                    opponent_hands[opponent_index] = opponent_hand
                    
                    for card in opponent_hand:
                        remaining_copy.remove(card)
        
        return opponent_hands
    
    def _simulate_game(self, card_to_play: Card, my_hand: list[Card], 
                      cards_played_this_round: list[Card], opponent_hands: dict[int, list[Card]],
                      current_vaza) -> float:
        """
        Simulate playing 'card_to_play' for the rest of the round.
        
        Logic:
        1. Create copy of game state
        2. Play the card
        3. Continue round with all remaining cards
        4. Other players play randomly (or via heuristic AI)
        5. Calculate final score
        
        Returns:
            Points I get (negative = bad, better to avoid)
        """
        
        # Create simulated hands: my hand with card removed, plus opponent hands
        sim_my_hand = [c for c in my_hand if c != card_to_play]
        
        # Build all hands for simulation
        player_hands_copy = [[] for _ in range(4)]
        player_hands_copy[self.my_player_index] = sim_my_hand
        
        for opponent_index, opponent_hand in opponent_hands.items():
            player_hands_copy[opponent_index] = opponent_hand.copy()
        
        # Create a Round to simulate from current state
        try:
            # Start fresh round with simulated hands
            sim_round = Round(player_hands_copy, self.round_type, trump_suit=self.trump_suit)
            
            # NOTE: If we're mid-vaza, we lose context about cards already played.
            # This is a limitation - simulations assume fresh vaza start.
            # Future improvement: properly track and continue mid-vaza state.
            
            # Play out the round with simulated players
            self._play_out_round_simulation(sim_round)
            
            # Calculate score for me based on cards I won
            score = self._calculate_round_score(sim_round)
            
            return score
        
        except Exception as e:
            print(f"[ERROR in simulation] {e}")
            return 0.0
    
    def _play_out_round_simulation(self, sim_round: Round):
        """
        Play out remaining vazas in simulation.
        Other players use heuristic AI (simple strategy).
        """
        
        while not sim_round.is_round_over():
            sim_round.start_vaza()
            play_order = sim_round.get_play_order()
            
            for player_index in play_order:
                # Get valid plays
                hand = sim_round.player_hands[player_index]
                
                if not hand:
                    continue
                
                # Determine valid plays based on current vaza state
                valid_plays = self._get_valid_plays(hand, sim_round.current_vaza, sim_round.round_type)
                
                if not valid_plays:
                    valid_plays = hand  # Fallback
                
                # Choose card
                if player_index == self.my_player_index:
                    # It's my turn in simulation
                    card = self._choose_card_heuristic(valid_plays, sim_round.current_vaza)
                else:
                    # Opponent: use simple heuristic
                    card = self._choose_card_heuristic(valid_plays, sim_round.current_vaza)
                
                # Play card
                sim_round.play_card(player_index, card)
            
            # Complete vaza
            sim_round.complete_vaza()
    
    def _get_valid_plays(self, hand: list[Card], current_vaza, round_type: str) -> list[Card]:
        """
        Filter hand to valid plays (respecting suit-following rules).
        This mimics what Round.play_card() checks.
        """
        if not current_vaza.main_suit:
            return hand  # First card, anything is valid
        
        has_main_suit = any(c.suit == current_vaza.main_suit for c in hand)
        
        if round_type == "copas":
            if has_main_suit:
                return [c for c in hand if c.suit == current_vaza.main_suit]
            
            has_hearts = any(c.suit == Suit.HEARTS for c in hand)
            if has_hearts:
                return [c for c in hand if c.suit == Suit.HEARTS]
            
            return hand
        
        elif round_type == "homens":
            if has_main_suit:
                return [c for c in hand if c.suit == current_vaza.main_suit]
            
            has_men = any(c.rank in [Rank.JACK, Rank.KING] for c in hand)
            if has_men:
                return [c for c in hand if c.rank in [Rank.JACK, Rank.KING]]
            
            return hand
        
        elif round_type == "mulheres":
            if has_main_suit:
                return [c for c in hand if c.suit == current_vaza.main_suit]
            
            has_women = any(c.rank == Rank.QUEEN for c in hand)
            if has_women:
                return [c for c in hand if c.rank == Rank.QUEEN]
            
            return hand
        
        else:
            # Default: follow main suit
            if has_main_suit:
                return [c for c in hand if c.suit == current_vaza.main_suit]
            
            return hand
    
    def _choose_card_heuristic(self, valid_plays: list[Card], current_vaza) -> Card:
        """
        Use heuristic AI for more realistic opponent simulation.
        This models actual gameplay better than always playing lowest card.
        """
        # Determine if it's nulos for festa rounds
        is_nulos = None
        if self.round_type in ["festa1", "festa2", "festa3", "festa4"]:
            # If no trump_suit, it's nulos (avoid vazas)
            is_nulos = (self.trump_suit is None)
        
        # Use actual heuristic AI for realistic play
        ai = AIPlayer(valid_plays, self.round_type, is_nulos=is_nulos)
        return ai.choose_card(valid_plays, current_vaza)
    
    def _calculate_round_score(self, sim_round: Round) -> float:
        """
        Calculate my score in this simulated round.
        
        Returns:
            Float: Points (negative values, as per game rules)
        """
        
        if self.round_type == "vazas":
            count = sim_round.vazas_won[self.my_player_index]
            return self.point_manager.get_points("vazas", count)
        
        elif self.round_type == "copas":
            count = sim_round.count_suit(self.my_player_index, Suit.HEARTS)
            return self.point_manager.get_points("copas", count)
        
        elif self.round_type == "homens":
            jacks = sim_round.count_rank(self.my_player_index, Rank.JACK)
            kings = sim_round.count_rank(self.my_player_index, Rank.KING)
            count = jacks + kings
            return self.point_manager.get_points("homens", count)
        
        elif self.round_type == "mulheres":
            count = sim_round.count_rank(self.my_player_index, Rank.QUEEN)
            return self.point_manager.get_points("mulheres", count)
        
        elif self.round_type == "king":
            has_king = any(
                c.rank == Rank.KING and c.suit == Suit.HEARTS 
                for c in sim_round.cards_won[self.my_player_index]
            )
            return self.point_manager.get_points("king", 1 if has_king else 0)
        
        elif self.round_type == "last":
            # Last round: count final 2 vazas (12th and 13th, indices 11-12)
            count = 0
            
            history = sim_round.vazas_history
            
            # Check 12th vaza (index 11)
            if len(history) >= 12:
                if history[11].winner == self.my_player_index:
                    count += 1
            
            # Check 13th vaza (index 12)
            if len(history) >= 13:
                if history[12].winner == self.my_player_index:
                    count += 1
            
            return self.point_manager.get_points("last", count)
        
        elif self.round_type in ["festa1", "festa2", "festa3", "festa4"]:
            # Festa rounds: use actual point values for proper comparison with other rounds
            # This ensures festa decisions have appropriate weight relative to base rounds
            count = sim_round.vazas_won[self.my_player_index]
            
            if self.is_nulos:
                # Nulos: 325 - 75*vazas (lower score with more vazas)
                # Return as-is so MC minimizes = fewer vazas
                return self.point_manager.get_points_nulos(count, nulos=True)
            else:
                # Positivos: 25 points per vaza (positive score)
                # Negate so MC minimizes negative = maximizes vazas
                return -self.point_manager.get_points("positivo", count)
        
        return 0.0
