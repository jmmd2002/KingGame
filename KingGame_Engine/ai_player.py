from deck import Card, Suit, Rank


class AIPlayer:
    """
    AI player that makes decisions based on:
    - Own hand
    - Round type
    - Cards already played
    
    Future: Will estimate opponent hands based on play history
    """
    
    def __init__(self, hand, round_type):
        """
        Args:
            hand: List of Card objects player has
            round_type: String ("vazas", "copas", "homens", "mulheres", "king", "last")
        """
        self.hand = hand
        self.round_type = round_type
    
    def choose_card(self, valid_plays, current_vaza):
        """
        Choose which card to play from valid_plays.
        
        Args:
            valid_plays: List of Card objects that are legal to play
            current_vaza: Vaza object with cards already played this trick
        
        Returns:
            Card object to play
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
    
    def _choose_vazas(self, valid_plays, current_vaza):
        """
        Vazas round: Avoid winning tricks.
        Strategy: Play lowest card that won't win, or lose safely.
        """
        if not current_vaza.cards_played:
            # First to play: play lowest card
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Try to play a card lower than highest (won't win)
        safe_cards = [c for c in valid_plays if c.suit == main_suit and c.rank.value < highest_main.rank.value]
        if safe_cards:
            return max(safe_cards, key=lambda c: c.rank.value)  # Play highest safe card
        
        # If can't play safe card of main suit, play lowest overall
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_copas(self, valid_plays, current_vaza):
        """
        Copas round: Avoid hearts.
        Strategy: Play non-heart if possible, otherwise lowest heart.
        """
        non_hearts = [c for c in valid_plays if c.suit != Suit.HEARTS]
        if non_hearts:
            return min(non_hearts, key=lambda c: c.rank.value)
        
        # All valid plays are hearts, play lowest
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_homens(self, valid_plays, current_vaza):
        """
        Homens round: Avoid jacks (11) and kings (13).
        Strategy: Play non-jack/king if possible, otherwise lowest jack/king.
        """
        safe_cards = [c for c in valid_plays if c.rank.value not in [11, 13]]
        if safe_cards:
            return min(safe_cards, key=lambda c: c.rank.value)
        
        # No safe cards, play lowest jack/king
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_mulheres(self, valid_plays, current_vaza):
        """
        Mulheres round: Avoid queens (12).
        Strategy: Play non-queen if possible, otherwise lowest queen.
        """
        safe_cards = [c for c in valid_plays if c.rank.value != 12]
        if safe_cards:
            return min(safe_cards, key=lambda c: c.rank.value)
        
        # No safe cards, play lowest queen
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_king(self, valid_plays, current_vaza):
        """
        King round: Avoid King of Hearts specifically.
        Strategy: Play non-King-of-Hearts if possible.
        """
        king_of_hearts = None
        for card in valid_plays:
            if card.suit == Suit.HEARTS and card.rank == Rank.KING:
                king_of_hearts = card
                break
        
        if king_of_hearts:
            other_cards = [c for c in valid_plays if c != king_of_hearts]
            if other_cards:
                return min(other_cards, key=lambda c: c.rank.value)
        
        # Only King of Hearts available or not in play, play lowest
        return min(valid_plays, key=lambda c: c.rank.value)
    
    def _choose_last(self, valid_plays, current_vaza):
        """
        Last round: Avoid winning the last 2 vazas.
        Strategy: Similar to vazas - avoid winning tricks.
        """
        if not current_vaza.cards_played:
            return min(valid_plays, key=lambda c: c.rank.value)
        
        main_suit = current_vaza.main_suit
        highest_main = max(
            [c for c in current_vaza.cards_played if c.suit == main_suit],
            key=lambda c: c.rank.value
        )
        
        # Try to play card lower than highest
        safe_cards = [c for c in valid_plays if c.suit == main_suit and c.rank.value < highest_main.rank.value]
        if safe_cards:
            return max(safe_cards, key=lambda c: c.rank.value)
        
        return min(valid_plays, key=lambda c: c.rank.value)


