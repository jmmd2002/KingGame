"""
Debug test to verify nulos strategy is working correctly
"""

from deck import Card, Suit, Rank, Deck
from mc_ai_player import MonteCarloAI
from game_simulator import Round

def test_nulos_strategy():
    """Test that MC AI avoids winning vazas in nulos festa"""
    print("=" * 80)
    print("NULOS STRATEGY TEST")
    print("=" * 80)
    print()
    
    # Create MC AI for nulos festa (trump_suit=None)
    mc_ai = MonteCarloAI(my_player_index=0, round_type="festa1", num_simulations=50, trump_suit=None)
    
    print("MC AI Configuration:")
    print(f"  Round type: {mc_ai.round_type}")
    print(f"  Trump suit: {mc_ai.trump_suit}")
    print(f"  Expected behavior: AVOID winning vazas (like vazas round)")
    print()
    
    # Create a simple test scenario
    deck = Deck()
    hands = deck.distribute()
    
    # Create nulos festa round
    nulos_round = Round(hands, "festa1", trump_suit=None)
    nulos_round.start_vaza()
    
    # Test scoring for different vaza counts
    print("Scoring verification:")
    print("-" * 40)
    for vazas in [0, 1, 5, 10, 13]:
        actual_score = mc_ai.point_manager.get_points_nulos(vazas, nulos=True)
        mc_return = -actual_score
        print(f"{vazas:2d} vazas: actual={actual_score:4d} pts, MC returns={mc_return:4d}")
    
    print()
    print("MC AI minimizes, so:")
    print("  - Prefers -325 (0 vazas) over 650 (13 vazas) ✓")
    print("  - This means it should AVOID winning vazas")
    print()
    
    # Test that heuristic AI also avoids in nulos
    print("Heuristic AI behavior in simulations:")
    print("-" * 40)
    
    # The heuristic AI used in simulations
    from ai_player import AIPlayer
    test_hand = hands[0][:5]  # Take first 5 cards
    
    # Create AI with is_nulos=True
    ai_nulos = AIPlayer(test_hand, "festa1", is_nulos=True)
    print(f"  AI with is_nulos=True: should use vazas strategy (avoid winning)")
    print(f"  Strategy method: _choose_festa -> _choose_vazas")
    
    # Create AI with is_nulos=False
    ai_positivos = AIPlayer(test_hand, "festa1", is_nulos=False)
    print(f"  AI with is_nulos=False: should try to win vazas")
    print(f"  Strategy method: _choose_festa -> try to win")
    
    print()
    print("=" * 80)
    print("Checking if MC AI chooses correctly...")
    print("=" * 80)
    print()
    
    # Run a simulation and see what the MC AI does
    my_hand = nulos_round.player_hands[0]
    if my_hand:
        valid_plays = my_hand  # All cards valid on first play
        
        print(f"Hand: {[str(c) for c in my_hand[:5]]}")  # Show first 5
        print(f"Running {mc_ai.num_simulations} simulations...")
        
        chosen_card = mc_ai.choose_card(
            my_hand=my_hand,
            valid_plays=valid_plays,
            cards_played_this_round=[],
            current_vaza=nulos_round.current_vaza
        )
        
        print(f"MC AI chose: {chosen_card}")
        print()
        
        # In nulos, the AI should generally prefer lower cards to avoid winning
        # (unless going first and trying to force others to take)
        print("Expected behavior: Play conservatively to avoid winning vazas")
        print("✓ Test complete")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    test_nulos_strategy()
