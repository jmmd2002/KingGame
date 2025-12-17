from game import Game

# Create a game with 4 players
players = ["Alice", "Bob", "Charlie", "Diana"]
game = Game(players)

print("=" * 70)
print(f"KING GAME - Full Round Test")
print("=" * 70)
print(f"Players: {', '.join(players)}\n")

# Play the full game
results = game.play_full_game()

print("=" * 70)
print("GAME RESULTS")
print("=" * 70)

# Display results
for i, player in enumerate(results['players']):
    vazas = results['vazas_won'][i]
    print(f"{player:15} - {vazas} vazas won")

print(f"\nTotal vazas played: {results['total_vazas']}")

# Show first and last vaza as examples
print("\n" + "=" * 70)
print("GAME HISTORY EXAMPLES")
print("=" * 70)

history = results['game_history']

# First vaza
print(f"\nVaza 1:")
first_vaza = history[0]
print(f"  Starter: Player {first_vaza.starter} ({players[first_vaza.starter]})")
print(f"  Play order: {[players[p] for p in first_vaza.play_order]}")
print(f"  Cards played: {first_vaza.cards_played}")
print(f"  Winner: Player {first_vaza.winner} ({players[first_vaza.winner]})")

# Last vaza
print(f"\nVaza 13:")
last_vaza = history[-1]
print(f"  Starter: Player {last_vaza.starter} ({players[last_vaza.starter]})")
print(f"  Play order: {[players[p] for p in last_vaza.play_order]}")
print(f"  Cards played: {last_vaza.cards_played}")
print(f"  Winner: Player {last_vaza.winner} ({players[last_vaza.winner]})")

print("\n" + "=" * 70)
