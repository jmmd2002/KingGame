# Monte Carlo AI Improvements

## Current Implementation Analysis

### Strengths ✅
- Solid foundation with simulation-based decision making
- Proper separation of concerns (hand estimation, simulation, scoring)
- Configurable number of simulations
- Respects game rules for valid plays

### Critical Issues 🚨

#### 1. **Missing Trump Suit Support**
The MC AI doesn't account for trump suits in festa positivos rounds. This means it can't properly evaluate:
- When trump cards will win
- Strategic value of holding/playing trump
- Defense against opponents' trump cards

#### 2. **Naive Opponent Hand Estimation**
Current approach: randomly distribute unknown cards
Problems:
- Ignores cards revealed in previous vazas
- Doesn't track suit voids (when opponent can't follow suit)
- No memory of what suits/ranks opponents have shown
- Results in unrealistic simulations

#### 3. **Insufficient Simulations**
50 simulations per card is often too low, especially:
- Early in round (more uncertainty)
- With many valid plays (need more samples)
- In critical situations (last few vazas)

#### 4. **Weak Simulation Rollout Policy**
Always playing lowest card is too simplistic:
- Doesn't model realistic opponent play
- Can lead to optimistic/pessimistic bias
- Better to use heuristic AI for opponent moves

#### 5. **Incomplete Mid-Vaza Handling**
Code comment at line 216: "This is complex - for now, let's start fresh vaza"
- Loses information from current vaza state
- Can't properly evaluate finishing current trick

## Recommended Improvements (Priority Order)

### Priority 1: Trump Suit Support ⚡
**Effort:** Low | **Impact:** Critical

```python
def __init__(self, my_player_index: int, round_type: str = "vazas", 
             num_simulations: int = 50, trump_suit: Suit = None):
    self.trump_suit = trump_suit  # Add this parameter
    # ... rest of init
```

Update `_simulate_game` to pass trump_suit to Round:
```python
sim_round = Round(player_hands_copy, self.round_type, trump_suit=self.trump_suit)
```

Update `_get_valid_plays` to handle trump suit logic (festa rounds).

### Priority 2: Smart Hand Estimation 🧠
**Effort:** Medium | **Impact:** High

Track card information state:
```python
class CardKnowledge:
    def __init__(self):
        self.cards_seen = set()  # Cards played in previous vazas
        self.suit_voids = {i: set() for i in range(4)}  # Known voids per player
        self.possible_cards = {i: set() for i in range(4)}  # Remaining possibilities
```

Improve `_estimate_opponent_hands`:
- Remove cards_seen from unknown pool
- Respect known suit voids when distributing
- Weight distribution by card likelihood

### Priority 3: Adaptive Simulation Count 📊
**Effort:** Low | **Impact:** Medium

```python
def _get_adaptive_sim_count(self, hand_size: int, num_valid_plays: int) -> int:
    """More simulations when uncertainty is high."""
    base = self.num_simulations
    
    # More sims early in round
    if hand_size > 8:
        base = int(base * 1.5)
    
    # More sims with many choices
    if num_valid_plays > 5:
        base = int(base * 1.2)
    
    return min(base, 200)  # Cap at 200
```

### Priority 4: Better Rollout Policy 🎯
**Effort:** Low | **Impact:** Medium

Replace `_choose_card_heuristic` with actual heuristic AI:
```python
def _choose_card_heuristic(self, valid_plays: list[Card], current_vaza) -> Card:
    """Use actual AI heuristics instead of always playing lowest."""
    ai = AIPlayer(valid_plays, self.round_type)
    return ai.choose_card(valid_plays, current_vaza)
```

This models opponents more realistically.

### Priority 5: Mid-Vaza Continuation 🎴
**Effort:** High | **Impact:** Medium

Properly handle vazas in progress:
```python
def _simulate_from_mid_vaza(self, sim_round: Round, current_vaza, 
                            remaining_players: list[int]) -> None:
    """Continue simulation from middle of vaza."""
    for player_index in remaining_players:
        # Simulate opponent moves for rest of vaza
        # Then complete vaza and continue with remaining vazas
```

### Priority 6: Early Game Heuristics 🚀
**Effort:** Medium | **Impact:** Low

For first 2-3 cards in round, fall back to heuristic AI to save time:
```python
def choose_card(self, my_hand, valid_plays, cards_played_this_round, current_vaza):
    # Use heuristics for early game
    if len(cards_played_this_round) < 6:  # First 1-2 vazas
        ai = AIPlayer(my_hand, self.round_type)
        return ai.choose_card(valid_plays, current_vaza)
    
    # Use MC for critical decisions
    # ... rest of MC logic
```

### Priority 7: Endgame Perfect Play 🎯
**Effort:** Medium | **Impact:** Medium

With ≤3 cards remaining, enumerate all possibilities (no simulation needed):
```python
def _solve_endgame(self, my_hand, valid_plays, known_cards):
    """When few cards remain, solve exactly."""
    # Try all possible opponent card combinations
    # Find guaranteed best play
```

## Implementation Plan

### Phase 1: Critical Fixes (1-2 hours)
1. Add trump_suit parameter and support
2. Improve simulation rollout with AIPlayer
3. Increase default simulations to 100

### Phase 2: Smart Estimation (2-3 hours)
4. Implement CardKnowledge tracking
5. Update hand estimation to use void information
6. Track cards seen in previous vazas

### Phase 3: Optimizations (1-2 hours)
7. Add adaptive simulation count
8. Implement early-game heuristics fallback
9. Performance profiling and tuning

### Phase 4: Advanced Features (optional)
10. Mid-vaza continuation
11. Endgame solver
12. UCB-based card selection (ML approach)

## Expected Performance Gains

| Improvement | Win Rate Δ | Speed Δ |
|------------|-----------|---------|
| Trump support | +15-20% (festa) | 0% |
| Smart estimation | +10-15% | -10% |
| Better rollout | +5-10% | 0% |
| Adaptive sims | +3-5% | -20% |
| **Total** | **+30-40%** | **-25%** |

## Testing Strategy

1. **test_mc_vs_heuristic.py** - Already exists, use this
2. Add trump suit test scenarios
3. Create fest rounds test suite
4. Measure win rate improvements
5. Profile performance (cProfile)

## Quick Win: Implementation Now

I can implement Priorities 1-4 immediately (30 min):
- Add trump_suit parameter
- Use AIPlayer for rollouts
- Increase default sims to 100
- Add adaptive simulation count

This should give you **+20-25% win rate improvement** with minimal complexity increase.

Would you like me to implement these improvements now?
