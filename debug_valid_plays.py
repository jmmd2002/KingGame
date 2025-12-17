"""
Debug test: Check valid_plays filtering
"""

from game import Game
from mc_ai_player import MonteCarloAI


def test_valid_plays():
    """Test that get_valid_plays works correctly"""
    
    players = ["AI1", "AI2", "AI3", "AI4"]
    game = Game(players)
    
    round_type = game.get_current_round_type()
    
    # Start vaza
    game.current_round.start_vaza()
    print(f"Round type: {round_type}")
    print(f"Starter: {players[0]}")
    
    # AI1 plays a card
    hand1 = game.get_player_hand(0)
    valid1 = game.get_valid_plays(0)
    print(f"\nAI1 hand: {[str(c) for c in hand1]}")
    print(f"AI1 valid plays: {[str(c) for c in valid1]}")
    
    # Simulate AI1 playing first spade
    first_card = None
    for card in hand1:
        if str(card).endswith('S'):  # Spade
            first_card = card
            break
    
    if not first_card:
        first_card = valid1[0]
    
    print(f"AI1 plays: {first_card}")
    game.current_round.current_vaza.cards_played.append(first_card)
    game.current_round.current_vaza.play_order.append(0)
    game.current_round.current_vaza.main_suit = first_card.suit
    hand1.remove(first_card)
    
    # Now check AI2's valid plays
    hand2 = game.get_player_hand(1)
    print(f"\nAI2 hand: {[str(c) for c in hand2]}")
    print(f"Main suit: {game.current_round.current_vaza.main_suit}")
    print(f"Cards played in vaza: {[str(c) for c in game.current_round.current_vaza.cards_played]}")
    
    valid2 = game.get_valid_plays(1)
    print(f"AI2 valid plays: {[str(c) for c in valid2]}")
    
    # Should all be spades!
    for card in valid2:
        if card.suit.name != 'SPADES':
            print(f"ERROR: {card} is not a spade!")


if __name__ == "__main__":
    test_valid_plays()
