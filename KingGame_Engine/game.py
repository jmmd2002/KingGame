from deck import Deck, Card, Suit
from game_simulator import Round, Rank
from point_manager import PointManager
from game_player import GamePlayer


class Game:
    ROUND_ORDER = ["vazas", "copas", "homens", "mulheres", "king", "last", "festa1", "festa2", "festa3", "festa4"]
    
    def __init__(self, player_names: list[str]):
        # Track festa modes: 1=nulos (negative), 0=positivos (positive)
        self.festa_modes = {"festa1": 1, "festa2": 1, "festa3": 1, "festa4": 1}
        # Track festa starting players
        self.festa_starters = {"festa1": 0, "festa2": 0, "festa3": 0, "festa4": 0}
        # Track festa trump suits (only for positivos mode)
        self.festa_trump_suits = {"festa1": None, "festa2": None, "festa3": None, "festa4": None}
        """
        player_names: list of 4 player names
        starting_player: index of player who starts the first round (0-3)
        """
        self.player_names = player_names
        self.players = [GamePlayer(i, name) for i, name in enumerate(player_names)]
        self.starting_player = 0  # Will be set later
        self.round_index = 0
        self.round_results: list[dict] = []  # Store results of each round
        self.cumulative_points = [0, 0, 0, 0]
        self.current_round = Round(self.ROUND_ORDER[0], self.starting_player)
    
    def start_round(self):
        """Start a new round"""
        if self.round_index < len(self.ROUND_ORDER):
            # Determine starting player
            if self.round_index == 0:
                self.starting_player = self.select_starting_player(self.player_names)
            else:
                self.starting_player = (self.current_round.starting_player + 1) % len(self.player_names)

    def select_starting_player(self, players: list[str]) -> int:
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
    
    def set_festa_config(self, festa_name: str, starter: int, is_nulos: bool, trump_suit: Suit = None):
        """Configure a festa round before it starts"""
        self.festa_starters[festa_name] = starter
        self.festa_modes[festa_name] = 1 if is_nulos else 0
        self.festa_trump_suits[festa_name] = trump_suit if not is_nulos else None
    
    def is_festa_nulos(self, round_type: str) -> bool:
        """Check if a festa round is in nulos mode"""
        if round_type in self.festa_modes:
            return self.festa_modes[round_type] == 1
        return False
    
    def get_current_round_type(self) -> str:
        """Get the current round type"""
        if self.round_index < len(self.ROUND_ORDER):
            return self.ROUND_ORDER[self.round_index]
        return None
    
    def get_player_hand(self, player: int) -> list:
        """Get current hand for a player"""
        return self.current_round.player_hands[player]
    
    def get_valid_plays(self, player: int) -> list[Card]:
        """
        Get valid cards a player can play based on suit-following rules.
        Uses the Round class validation logic.
        """
        hand = self.current_round.player_hands[player]
        
        if not hand:
            return []
        
        # If vaza hasn't started yet or no main suit, all cards are valid
        if self.current_round.current_vaza is None or self.current_round.current_vaza.main_suit is None:
            return hand.copy()
        
        # Check what cards the player has
        has_main_suit = any(c.suit == self.current_round.current_vaza.main_suit for c in hand)
        round_type = self.get_current_round_type()
        
        valid = []
        
        for card in hand:
            # Try to play this card - use Round's validation
            # Create a temporary copy to test
            temp_hands = [h.copy() for h in self.current_round.player_hands]
            temp_round = Round(temp_hands, round_type)
            temp_round.current_vaza = self.current_round.current_vaza
            
            # This is hacky - let's just duplicate the validation logic here
            # to avoid circular dependency
            
            if round_type == "copas":
                if has_main_suit and card.suit != self.current_round.current_vaza.main_suit:
                    continue
                has_hearts = any(c.suit == Suit.HEARTS for c in hand)
                if not has_main_suit and has_hearts and card.suit != Suit.HEARTS:
                    continue
                valid.append(card)
            elif round_type == "homens":
                if has_main_suit and card.suit != self.current_round.current_vaza.main_suit:
                    continue
                has_men = any(c.rank == Rank.JACK or c.rank == Rank.KING for c in hand)
                if not has_main_suit and has_men and card.rank not in [Rank.JACK, Rank.KING]:
                    continue
                valid.append(card)
            elif round_type == "mulheres":
                if has_main_suit and card.suit != self.current_round.current_vaza.main_suit:
                    continue
                has_women = any(c.rank == Rank.QUEEN for c in hand)
                if not has_main_suit and has_women and card.rank != Rank.QUEEN:
                    continue
                valid.append(card)
            else:
                # Default: follow suit
                if has_main_suit and card.suit != self.current_round.current_vaza.main_suit:
                    continue
                valid.append(card)
        
        return valid if valid else hand.copy()  # If no valid by rules, can play anything
    
    def play_vaza(self, card_plays: list[tuple[int, Card]], validate_hands: bool = True) -> int:
        """
        Play one complete vaza with user-provided decisions.
        card_plays: list of (player_index, card) tuples in play order
        validate_hands: if False, skip validation (for real-life mode where cards are dealt externally)
        
        Note: Assumes start_vaza() has already been called and 
        cards have been added to current_vaza already (for AI decision making).
        Returns: player index of vaza winner
        """
        
        # Validate and remove cards from hands
        for player, card in card_plays:
            if validate_hands:
                if card not in self.current_round.player_hands[player]:
                    raise ValueError(f"Invalid play: Player {player} doesn't have {card}")
                self.current_round.player_hands[player].remove(card)
            else:
                # Real-life mode: just try to remove, if not present, skip
                try:
                    self.current_round.player_hands[player].remove(card)
                except ValueError:
                    pass  # Card not in tracked hand, that's OK in real-life mode
        
        winner = self.current_round.complete_vaza()
        return winner
    
    def is_round_over(self) -> bool:
        """Check if current round is finished"""
        return self.current_round.is_round_over()
    
    def can_play_round(self) -> bool:
        #TODO have to redo this
        """Check if current round can be played (required cards are still available)"""
        round_type = self.current_round.round_type
        
        if round_type == "copas":
            # Check if any hearts are left in remaining cards
            for hand in self.current_round.cards_played:
                if any(card.suit == Suit.HEARTS for card in hand):
                    return True
            return False
        elif round_type == "homens":
            # Check if any jacks or kings are left
            for hand in self.current_round.cards_played:
                if any(card.rank == Rank.JACK or card.rank == Rank.KING for card in hand):
                    return True
            return False
        elif round_type == "mulheres":
            # Check if any queens are left
            for hand in self.current_round.cards_played:
                if any(card.rank == Rank.QUEEN for card in hand):
                    return True
            return False
        elif round_type == "king":
            # Check if King of Hearts is left
            for hand in self.current_round.cards_played:
                if any(card.rank == Rank.KING and card.suit == Suit.HEARTS for card in hand):
                    return True
            return False
        
        # Vazas and Last rounds can always be played
        return True
    
    def skip_round(self):
        """Skip current round (no cards available) and advance"""
        round_type = self.get_current_round_type()
        
        # Record empty round with 0 points for all players
        results = {
            'round_type': round_type,
            'players': self.player_names,
            'points': [0, 0, 0, 0],
            'vazas_won': [0, 0, 0, 0],
            'game_history': []
        }
        self.round_results.append(results)
        
        self.round_index += 1
        self._start_round()
    
    def get_next_vaza_info(self) -> dict:
        """Get info about the next vaza to be played"""
        return {
            'vaza_number': len(self.current_round.vazas_history) + 1,
            'starter': self.current_round.vaza_starter,
            'play_order': self.current_round.get_play_order()
        }
    
    def calculate_round_points(self) -> list[int]:
        """
        Calculate points for current round based on round type and what was won.
        Returns: [points_p0, points_p1, points_p2, points_p3]
        """
        round_type = self.get_current_round_type()
        
        if round_type in ["festa1", "festa2", "festa3", "festa4"]:
            # Festa rounds: check if nulos or positivos
            is_nulos = self.festa_modes[round_type]
            return [
                PointManager.get_points_nulos(self.current_round.vazas_won[i], is_nulos)
                for i in range(4)
            ]
        elif round_type == "vazas":
            # Points based on number of vazas won
            return [
                PointManager.get_points(round_type, self.current_round.vazas_won[i])
                for i in range(4)
            ]
        elif round_type == "copas":
            # Points based on number of hearts won
            hearts_won = [self.current_round.count_suit(i, Suit.HEARTS) for i in range(4)]
            return [
                PointManager.get_points(round_type, hearts_won[i])
                for i in range(4)
            ]
        elif round_type == "homens":
            # Points based on number of jacks and kings won
            men_won = [
                self.current_round.count_rank(i, Rank.JACK) + self.current_round.count_rank(i, Rank.KING)
                for i in range(4)
            ]
            return [
                PointManager.get_points(round_type, men_won[i])
                for i in range(4)
            ]
        elif round_type == "mulheres":
            # Points based on number of queens won
            women_won = [self.current_round.count_rank(i, Rank.QUEEN) for i in range(4)]
            return [
                PointManager.get_points(round_type, women_won[i])
                for i in range(4)
            ]
        elif round_type == "king":
            # Points based on having the King of Hearts
            king_points = [0, 0, 0, 0]
            for player_idx in range(4):
                for card in self.current_round.cards_won[player_idx]:
                    if card.rank == Rank.KING and card.suit == Suit.HEARTS:
                        king_points[player_idx] = PointManager.get_points(round_type, 1)
                        break
            return king_points
        elif round_type == "last":
            # Points based on winning the last 2 vazas (12th and 13th)
            last_two_vazas_won = [0, 0, 0, 0]
            
            # Check the last 2 vazas
            history = self.current_round.vazas_history
            if len(history) >= 12:
                # 12th vaza (index 11)
                winner_12 = history[11].winner
                last_two_vazas_won[winner_12] += 1
            
            if len(history) >= 13:
                # 13th vaza (index 12)
                winner_13 = history[12].winner
                last_two_vazas_won[winner_13] += 1
            
            return [
                PointManager.get_points(round_type, last_two_vazas_won[i])
                for i in range(4)
            ]
        else:
            raise NotImplementedError(f"Round type '{round_type}' not implemented yet")
    
    def advance_to_next_round(self):
        """Move to the next round"""
        # Save current round results
        points = self.calculate_round_points()
        round_type = self.get_current_round_type()
        
        # Update GamePlayer stats based on round type
        self._update_player_stats(round_type)
        
        results = {
            'round_type': round_type,
            'players': self.player_names,
            'points': points,
            'vazas_won': self.current_round.vazas_won,
            'game_history': self.current_round.vazas_history
        }
        self.round_results.append(results)
        
        # Update cumulative points
        for i in range(4):
            self.cumulative_points[i] += points[i]
        
        self.round_index += 1
        self._start_round()
    
    def is_game_over(self) -> bool:
        """Check if all rounds are completed"""
        return self.round_index >= len(self.ROUND_ORDER)
    
    def get_current_round_results(self) -> dict:
        """Returns current round results"""
        points = self.calculate_round_points()
        return {
            'round_type': self.get_current_round_type(),
            'players': self.player_names,
            'points': points,
            'vazas_won': self.current_round.vazas_won,
            'total_vazas': len(self.current_round.vazas_history),
            'game_history': self.current_round.vazas_history
        }
    
    def get_season_standings(self) -> dict:
        """Get final season standings"""
        return {
            'players': self.player_names,
            'cumulative_points': self.cumulative_points,
            'round_results': self.round_results,
            'game_players': self.players
        }
    
    def _update_player_stats(self, round_type: str):
        """Update GamePlayer stats based on round results"""
        for player_idx in range(4):
            if round_type in ["festa1", "festa2", "festa3", "festa4"]:
                # Store festa results
                festa_num = int(round_type[-1])  # Extract number from festa1, festa2, etc.
                setattr(self.players[player_idx], f"festa{festa_num}", self.current_round.vazas_won[player_idx])
                # Update nulos_check
                self.players[player_idx].nulos_check[f"Festa{festa_num}"] = self.festa_modes[round_type]
            elif round_type == "vazas":
                self.players[player_idx].vazas = self.current_round.vazas_won[player_idx]
            elif round_type == "copas":
                self.players[player_idx].copas = self.current_round.count_suit(player_idx, Suit.HEARTS)
            elif round_type == "homens":
                # Jacks + Kings
                jacks = self.current_round.count_rank(player_idx, Rank.JACK)
                kings = self.current_round.count_rank(player_idx, Rank.KING)
                self.players[player_idx].homens = jacks + kings
            elif round_type == "mulheres":
                # Queens = rank 12
                self.players[player_idx].mulheres = self.current_round.count_rank(player_idx, Rank.QUEEN)
            elif round_type == "king":
                # Only King of Hearts counts
                has_king_of_hearts = any(
                    card.rank == Rank.KING and card.suit == Suit.HEARTS
                    for card in self.current_round.cards_won[player_idx]
                )
                self.players[player_idx].king = 1 if has_king_of_hearts else 0
            elif round_type == "last":
                # Count how many of the last 2 vazas this player won
                last_count = 0
                history = self.current_round.vazas_history
                
                if len(history) >= 12 and history[11].winner == player_idx:
                    last_count += 1
                if len(history) >= 13 and history[12].winner == player_idx:
                    last_count += 1
                
                self.players[player_idx].last = last_count
