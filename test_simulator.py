from deck import Deck, Card, Suit, Rank
from game_simulator import GameSimulator

# Create and distribute deck
deck = Deck(seed=42)  # Use seed for reproducible results
player_hands = deck.distribute()

print("=" * 60)
print("KING GAME SIMULATOR TEST")
print("=" * 60)

# Show initial hands
print("\nInitial hands:")
for i, hand in enumerate(player_hands):
    print(f"Player {i}: {hand}")

# Initialize simulator
simulator = GameSimulator(player_hands)

print(f"\nStarting player: {simulator.vaza_starter}")
print("=" * 60)

# Simulate first 3 vazas
for vaza_num in range(1, 4):
    print(f"\nVAZA {vaza_num}")
    print("-" * 60)
    
    vaza = simulator.start_vaza()
    play_order = simulator.get_play_order()
    
    print(f"Play order: {play_order}")
    
    # Each player plays a card (first card from their hand for testing)
    for position, player in enumerate(play_order):
        card = player_hands[player][0]  # Just play first card for testing
        simulator.play_card(player, card)
        print(f"Player {player} plays: {card}")
    
    # Complete vaza
    winner = simulator.complete_vaza()
    print(f"\nVaza winner: Player {winner}")
    print(f"Cards played: {vaza.cards_played}")
    
    print(f"Vazas won so far: {simulator.vazas_won}")
    print(f"Next starter: Player {simulator.vaza_starter}")

print("\n" + "=" * 60)
print("REMAINING CARDS:")
print("=" * 60)
for i, hand in enumerate(player_hands):
    print(f"Player {i}: {len(hand)} cards left - {hand}")

print(f"\nTotal vazas in history: {len(simulator.vazas_history)}")
