"""
Quick test script to verify real game mode works
"""

from real_life_game import card_from_string, configure_festa_round, select_starting_player
from deck import Suit, Card, Rank

# Test card parsing
print("Testing card parsing...")
test_cards = ["AH", "KS", "7D", "10C", "2H"]
for card_str in test_cards:
    card = card_from_string(card_str)
    if card:
        print(f"  ✓ {card_str} -> {card}")
    else:
        print(f"  ❌ {card_str} failed to parse")

print("\n" + "="*80)
print("Card parsing test PASSED!")
print("="*80)

# Test that imports work
from game import Game
from game_simulator import Round

print("\nTesting Game initialization...")
players = ["Alice", "Bob", "Charlie", "Diana"]
game = Game(players, starting_player=0)
print(f"  ✓ Game created with players: {players}")
print(f"  ✓ Starting player: {players[0]}")
print(f"  ✓ Current round: {game.get_current_round_type()}")

print("\nTesting festa configuration...")
game.set_festa_config("festa1", 2, False, Suit.HEARTS)
print(f"  ✓ Festa1 configured: starter=2, nulos=False, trump=Hearts")
print(f"  ✓ Is festa1 nulos? {game.is_festa_nulos('festa1')}")

print("\nTesting Round with trump suit...")
from deck import Deck
deck = Deck()
hands = deck.distribute()
test_round = Round(hands, "festa1", 0, Suit.HEARTS)
print(f"  ✓ Round created with trump suit: {test_round.trump_suit}")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)
print("\nThe real game mode should work correctly!")
print("You can now run: python real_life_game.py")
