from deck import Card, Suit, Rank
from game_simulator import Vaza


class AIPlayer:
    """
    Heuristic AI player for the King card game.
    
    Makes decisions based on simple rule-based strategies tailored to each
    round type. Used as a baseline AI and for Monte Carlo simulations.
    
    Attributes
    ----------
    hand : list[Card]
        The player's current hand of cards.
    round_type : str
        Type of round being played ("vazas", "copas", "homens", "mulheres", "king", "last").
    """
    
    def __init__(self, hand: list[Card], round_type: str) -> None:
        """
        Initialize the AI player.
        
        Parameters
        ----------
        hand : list[Card]
            List of Card objects in the player's hand.
        round_type : str
            Type of round being played.
        """
        self.hand: list[Card] = hand
        self.round_type: str = round_type
    
    def choose_card(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Choose which card to play from valid options.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that are legal to play (already validated).
        current_vaza : Vaza
            Current vaza with cards already played.
        
        Returns
        -------
        Card
            The card to play.
        
        Raises
        ------
        ValueError
            If no valid plays are available.
        
        Notes
        -----
        Routes to round-specific strategy methods based on round_type.
        """
        if not valid_plays:
            raise ValueError("No valid plays available")
        
        if len(valid_plays) == 1:
            return valid_plays[0]
        
        # Route to round-specific strategy
        if self.round_type == "vazas":
            return self._choose_vazas(valid_plays, current_vaza)
        elif self.round_type == "copas":
            return self._choose_copas(valid_plays, current_vaza)
        elif self.round_type == "homens":
            return self._choose_homens(valid_plays, current_vaza)
        elif self.round_type == "mulheres":
            return self._choose_mulheres(valid_plays, current_vaza)
        elif self.round_type == "king":
            return self._choose_king(valid_plays, current_vaza)
        elif self.round_type == "last":
            return self._choose_last(valid_plays, current_vaza)
        else:
            # Fallback: play lowest card
            return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_vazas(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Strategy for vazas round: Avoid winning tricks.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Card to play - tries to play highest card that won't win,
            or lowest card if all cards would win.
        """
        if not current_vaza.cards_played:
            # First to play: play lowest card
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find all cards that won't win
        safe_cards: list[Card] = []
        for card in valid_plays:
            if card.suit == main_suit:
                # Main suit card - won't win if lower than highest
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                # Off-suit card - won't win (can't take the trick)
                safe_cards.append(card)
        
        if safe_cards:
            # Play highest safe card to get rid of high cards
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_copas(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Strategy for copas round: Avoid hearts.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Prioritizes playing highest heart that won't win, otherwise highest non-heart.
        """
        if not current_vaza.cards_played:
            # First to play: prefer non-hearts, play lowest
            non_hearts = [c for c in valid_plays if c.suit != Suit.HEARTS]
            if non_hearts:
                return min(non_hearts, key=lambda c: c.rank.value)
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find all cards that won't win
        safe_cards = []
        for card in valid_plays:
            if card.suit == main_suit:
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                # Off-suit won't win
                safe_cards.append(card)
        
        if safe_cards:
            # Prioritize hearts among safe cards - play highest safe heart
            safe_hearts = [c for c in safe_cards if c.suit == Suit.HEARTS]
            if safe_hearts:
                return max(safe_hearts, key=lambda c: c.rank.value)
            # No safe hearts - play highest safe card
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_homens(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Strategy for homens round: Avoid jacks and kings.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Prioritizes playing highest jack/king that won't win, otherwise highest safe card.
        """
        if not current_vaza.cards_played:
            # First to play: prefer non-penalty cards, play lowest
            non_men = [c for c in valid_plays if c.rank.value not in [11, 13]]
            if non_men:
                return min(non_men, key=lambda c: c.rank.value)
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find all cards that won't win
        safe_cards = []
        for card in valid_plays:
            if card.suit == main_suit:
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                # Off-suit won't win
                safe_cards.append(card)
        
        if safe_cards:
            # Prioritize jacks/kings among safe cards - play highest safe man
            safe_men = [c for c in safe_cards if c.rank.value in [11, 13]]
            if safe_men:
                return max(safe_men, key=lambda c: c.rank.value)
            # No safe men - play highest safe card
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_mulheres(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Strategy for mulheres round: Avoid queens.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Prioritizes playing highest queen that won't win, otherwise highest safe card.
        """
        if not current_vaza.cards_played:
            # First to play: prefer non-queens, play lowest
            non_queens = [c for c in valid_plays if c.rank.value != 12]
            if non_queens:
                return min(non_queens, key=lambda c: c.rank.value)
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find all cards that won't win
        safe_cards = []
        for card in valid_plays:
            if card.suit == main_suit:
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                # Off-suit won't win
                safe_cards.append(card)
        
        if safe_cards:
            # Prioritize queens among safe cards - play highest safe queen
            safe_queens = [c for c in safe_cards if c.rank.value == 12]
            if safe_queens:
                return max(safe_queens, key=lambda c: c.rank.value)
            # No safe queens - play highest safe card
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_king(self, valid_plays: list[Card], current_vaza: Vaza) -> Card:
        """
        Strategy for king round: Avoid taking King of Hearts.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Tries to avoid winning tricks to avoid taking King of Hearts.
            Plays highest card that won't win if possible.
        
        Notes
        -----
        The penalty is for taking the trick containing King of Hearts,
        so we try to avoid winning any trick (unless KH is already taken).
        """
        # If we have King of Hearts in valid plays and can play something else
        king_of_hearts = None
        for card in valid_plays:
            if card.suit == Suit.HEARTS and card.rank == Rank.KING:
                king_of_hearts = card
                break
        
        non_kh_cards = [c for c in valid_plays if c != king_of_hearts]
        
        # If we can avoid playing King of Hearts, do so
        if king_of_hearts and non_kh_cards:
            # Try to play highest non-KH card that won't win
            if not current_vaza.cards_played:
                # First to play: play lowest non-KH
                return min(non_kh_cards, key=lambda c: c.rank.value)
            
            main_suit = current_vaza.main_suit
            highest_main = max(
                [c for c in current_vaza.cards_played if c.suit == main_suit],
                key=lambda c: c.rank.value
            )
            
            # Find non-KH cards that won't win
            safe_cards: list[Card] = []
            for card in non_kh_cards:
                if card.suit == main_suit:
                    if card.rank.value < highest_main.rank.value:
                        safe_cards.append(card)
                else:
                    # Off-suit won't win
                    safe_cards.append(card)
            
            if safe_cards:
                # Play highest safe card
                return max(safe_cards, key=lambda c: c.rank.value)
            
            # All non-KH cards would win - if last player, dump highest; otherwise play lowest
            is_last_player = len(current_vaza.cards_played) == 3
            if is_last_player:
                return max(non_kh_cards, key=lambda c: c.rank.value)
            return min(non_kh_cards, key=lambda c: c.rank.value)
        
        # Either only KH available or no KH in hand - try not to win
        if not current_vaza.cards_played:
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find cards that won't win
        safe_cards = []
        for card in valid_plays:
            if card.suit == main_suit:
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                safe_cards.append(card)
        
        if safe_cards:
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_last(self, valid_plays: list[Card], current_vaza) -> Card:
        """
        Strategy for last round: Avoid winning the last 2 vazas.
        
        Parameters
        ----------
        valid_plays : list[Card]
            Cards that can be legally played.
        current_vaza : Vaza
            Current vaza state.
        
        Returns
        -------
        Card
            Tries to play highest card that won't win,
            or lowest card if all cards would win.
        
        Notes
        -----
        Uses same strategy as vazas round.
        """
        if not current_vaza.cards_played:
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Find all cards that won't win
        safe_cards = []
        for card in valid_plays:
            if card.suit == main_suit:
                if card.rank.value < highest_main.rank.value:
                    safe_cards.append(card)
            else:
                # Off-suit won't win
                safe_cards.append(card)
        
        if safe_cards:
            # Play highest safe card
            return max(safe_cards, key=lambda c: c.rank.value)
        
        # All cards would win - if last player, dump highest; otherwise play lowest
        is_last_player = len(current_vaza.cards_played) == 3
        if is_last_player:
            return max(valid_plays, key=lambda c: c.rank.value)
        return min(valid_plays, key=lambda c: c.rank.value)


