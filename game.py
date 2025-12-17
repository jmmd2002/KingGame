from deck import Deck, Card, Suit
from game_simulator import Round, Rank
from point_manager import PointManager
from game_player import GamePlayer


class Game:
    ROUND_ORDER = ["vazas", "copas", "homens", "mulheres", "king", "last", "nulos"]
    
    def __init__(self, player_names: list[str]):
        """
        player_names: list of 4 player names
        """
        self.player_names = player_names
        self.players = [GamePlayer(i, name) for i, name in enumerate(player_names)]
        self.round_index = 0
        self.current_round = None
        self.round_results: list[dict] = []  # Store results of each round
        self.cumulative_points = [0, 0, 0, 0]
        
        self._start_round()
    
    def _start_round(self):
        """Start a new round"""
        if self.round_index < len(self.ROUND_ORDER):
            deck = Deck()
            player_hands = deck.distribute()
            round_type = self.ROUND_ORDER[self.round_index]
            self.current_round = Round(player_hands, round_type)
    
    def get_current_round_type(self) -> str:
        """Get the current round type"""
        if self.round_index < len(self.ROUND_ORDER):
            return self.ROUND_ORDER[self.round_index]
        return None
    
    def get_player_hand(self, player: int) -> list:
        """Get current hand for a player"""
        return self.current_round.player_hands[player]
    
    def play_vaza(self, card_plays: list[tuple[int, Card]]) -> int:
        """
        Play one complete vaza with user-provided decisions.
        card_plays: list of (player_index, card) tuples in play order
        Returns: player index of vaza winner
        """
        self.current_round.start_vaza()
        
        for player, card in card_plays:
            if not self.current_round.play_card(player, card):
                raise ValueError(f"Invalid play: Player {player} doesn't have {card}")
        
        winner = self.current_round.complete_vaza()
        return winner
    
    def is_round_over(self) -> bool:
        """Check if current round is finished"""
        return self.current_round.is_round_over()
    
    def can_play_round(self) -> bool:
        """Check if current round can be played (required cards are still available)"""
        round_type = self.get_current_round_type()
        
        if round_type == "copas":
            # Check if any hearts are left in remaining cards
            for hand in self.current_round.player_hands:
                if any(card.suit == Suit.HEARTS for card in hand):
                    return True
            return False
        elif round_type == "homens":
            # Check if any jacks or kings are left
            for hand in self.current_round.player_hands:
                if any(card.rank == Rank.JACK or card.rank == Rank.KING for card in hand):
                    return True
            return False
        elif round_type == "mulheres":
            # Check if any queens are left
            for hand in self.current_round.player_hands:
                if any(card.rank == Rank.QUEEN for card in hand):
                    return True
            return False
        elif round_type == "king":
            # Check if King of Hearts is left
            for hand in self.current_round.player_hands:
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
        
        if round_type == "vazas":
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
            if round_type == "vazas":
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
