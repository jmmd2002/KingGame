# King Game Engine

## Overview
The KingGame Engine supports playing the Portuguese card game "King" (Jogo do Rei) in two modes:
- **REAL LIFE MODE**: For playing with physical cards
- **VIRTUAL MODE**: Computer deals and shows hands

## Quick Start

```bash
cd KingGame_Engine
python real_life_game.py
```

## Setup Options

When you start the game, you'll be able to:
1. **Choose game mode** - Real Life or Virtual
2. **Set player names** - Customize each player's name (or use defaults)
3. **Select player types** - Human or AI for each player
4. **Choose starting player** - Pick who starts the first round

## Game Modes

### 🎴 REAL LIFE MODE
**Perfect for playing with physical cards in person!**

- You shuffle and deal physical cards to players
- Input which card each player plays
- No validation against computer hands (trusts your input)
- Only prevents playing the same card twice
- Great for social/in-person play with real cards

**When to use:**
- Playing with friends using a physical deck
- Want authentic card game experience
- Don't want players to see each other's hands on screen

### 💻 VIRTUAL MODE
**Perfect for practice, learning, or remote play!**

- Computer shuffles and deals cards
- Shows each human player's hand on screen
- Validates plays against dealt hands
- Prevents illegal plays
- Great for learning the game rules

**When to use:**
- Learning how to play King
- Practicing strategy
- No physical cards available
- Playing remotely

## Card Input Format

When inputting cards, use these formats:
- **Number + Suit**: `2H`, `10D`, `13C`, `14S`
- **Letter + Suit**: `AH` (Ace), `KH` (King), `QD` (Queen), `JC` (Jack)
- **Suits**: H=Hearts, D=Diamonds, C=Clubs, S=Spades

**Examples:**
- `AH` or `14H` = Ace of Hearts
- `KH` or `13H` = King of Hearts  
- `7D` = 7 of Diamonds
- `10S` = 10 of Spades

Type `help` during play for card format reminders.
In Virtual mode, type `list` to see your hand again.

## Player Types

For each of the 4 players, choose:
- **HUMAN**: Real player (you input their card plays)
- **AI**: Computer player (uses Monte Carlo simulation for intelligent play)

You can mix human and AI players in any combination!

## Game Rounds

The game consists of 6 rounds (each round uses all 52 cards):

1. **VAZAS** - Avoid winning tricks (vazas)
2. **COPAS** - Avoid collecting Hearts (♥)
3. **HOMENS** - Avoid collecting Jacks and Kings (men)
4. **MULHERES** - Avoid collecting Queens (women)
5. **KING** - Avoid the King of Hearts (K♥)
6. **LAST** - Avoid winning the last vaza

## Comparison: Real Life vs Virtual Mode

| Feature | Real Life Mode | Virtual Mode |
|---------|---------------|--------------|
| Card dealing | You deal physical cards | Computer deals |
| Hand visibility | Hidden (as in real game) | Shown on screen |
| Input validation | Only checks duplicates | Validates against hand |
| Best for | Social/in-person play | Learning/practice |
| Physical cards needed | Yes | No |

## Features

✅ **Automatic scoring** - No calculation errors  
✅ **Rule enforcement** - Ensures legal plays  
✅ **Smart AI** - Monte Carlo simulation for intelligent play  
✅ **Track history** - Never lose count of what's been played  
✅ **Two modes** - Real life or virtual play  
✅ **Flexible setup** - Mix human and AI players  

## Tips

### Real Life Mode Tips
- Make sure everyone agrees on which card was played before entering it
- The program only tracks that cards aren't played twice
- Perfect for keeping score in physical games
- AI players can still participate (program tells you which card to play for them)

### Virtual Mode Tips
- Use `list` command to see your hand anytime
- Good for learning which cards are legal to play
- Watch AI strategy to improve your play
- Practice before playing in real life

## Files

- **`real_life_game.py`** - Main program (supports both modes)
- **`interactive_game.py`** - Original version (legacy)
- **`game.py`** - Core game logic
- **`deck.py`** - Card and deck classes
- **`mc_ai_player.py`** - Monte Carlo AI implementation
- **`ai_player.py`** - Heuristic AI implementation
- **`point_manager.py`** - Scoring system
- **`game_simulator.py`** - Round and vaza simulation

## Example Session

```
GAME MODE SELECTION
Choose game mode:
  [R] REAL LIFE MODE - You shuffle and deal physical cards
  [V] VIRTUAL MODE - Computer deals cards and shows hands
Select mode (R/V) [default: Real Life]: R

✓ REAL LIFE MODE selected

Player 1 - (h)uman or (a)i? [default: human]: h
Player 2 - (h)uman or (a)i? [default: human]: h
Player 3 - (h)uman or (a)i? [default: human]: a
Player 4 - (h)uman or (a)i? [default: human]: h

[Game proceeds with human input and AI suggestions...]
```

## Requirements

```bash
pip install -r requirements.txt
```

(Currently no external dependencies beyond Python standard library)

## Troubleshooting

**Q: In Real Life mode, can I play any card?**  
A: Yes! The program trusts your input and only prevents duplicate plays.

**Q: In Virtual mode, why can't I play a certain card?**  
A: The game enforces suit-following rules. You must follow the main suit if you have it.

**Q: Can all 4 players be AI?**  
A: Yes! You can watch AI vs AI games to learn strategies.

**Q: Can I switch between modes?**  
A: Restart the program and select the other mode.

**Q: What if I make a mistake entering a card?**  
A: In Real Life mode, correct it in your physical game. In Virtual mode, the validation prevents most mistakes.

## Have fun playing King! 🎴👑
