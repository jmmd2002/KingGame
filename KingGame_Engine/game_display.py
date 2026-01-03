"""
Game Display Module
===================

Handles all console output and user interface for the King card game.
"""

from deck import Card, Suit, Rank
from game_simulator import Round
from game_player import GamePlayer


class GameDisplay:
    """
    Handles all console output and display formatting for the King card game.
    
    This class centralizes all print statements and UI-related functionality,
    making it easier to modify the display or potentially swap to a different
    UI implementation.
    """
    
    DIVIDER = "=" * 80
    
    @staticmethod
    def display_card_list(cards: list[Card], sort: bool = True) -> str:
        """
        Format a list of cards for display.
        
        Parameters
        ----------
        cards : list[Card]
            List of cards to display.
        sort : bool, optional
            Whether to sort cards by suit and rank, by default True.
        
        Returns
        -------
        str
            Comma-separated string representation of cards.
        """
        if sort:
            cards = sorted(cards, key=lambda c: (c.suit.value, c.rank.value))
        return ", ".join([str(card) for card in cards])
    
    @staticmethod
    def show_setup_header():
        """Display the player setup header."""
        print(GameDisplay.DIVIDER)
        print("SETUP: Player Configuration")
        print(GameDisplay.DIVIDER)
        print("Configure each player's name and type:")
        print("  - HUMAN players: You input which card they played")
        print("  - AI players: Computer decides and shows the card\n")
    
    @staticmethod
    def show_game_header(player_names: list[str], player_is_ai: list[bool]):
        """
        Display the game header with instructions.
        
        Parameters
        ----------
        player_names : list[str]
            Names of all players.
        player_is_ai : list[bool]
            Flags indicating if each player is AI.
        """
        print("\n" + GameDisplay.DIVIDER)
        print("REAL-LIFE KING GAME ASSISTANT")
        print(GameDisplay.DIVIDER)
        print("Instructions:")
        print("  1. Shuffle and deal 13 cards to each player in real life")
        print("  2. The program will track plays and calculate scores")
        print("  3. For human players, input which card they played")
        print("  4. For AI players, the computer will show which card to play")
        print("  5. Type 'help' at any time for card format examples")
        print(GameDisplay.DIVIDER)
        player_types = ', '.join([f'{player_names[i]} ({"AI" if player_is_ai[i] else "HUMAN"})' for i in range(4)])
        print(f"\nPlayers: {player_types}\n")
    
    @staticmethod
    def show_round_header(round_type: str, description: str):
        """
        Display the round header.
        
        Parameters
        ----------
        round_type : str
            Type of the round.
        description : str
            Description of the round objective.
        """
        print("\n" + GameDisplay.DIVIDER)
        print(f"ROUND: {round_type.upper()}")
        print(GameDisplay.DIVIDER)
        print(f"Objective: {description}\n")
    
    @staticmethod
    def show_vaza_header(vaza_num: int, starter: GamePlayer, play_order: list[GamePlayer], 
                        cards_played_count: int):
        """
        Display the vaza header.
        
        Parameters
        ----------
        vaza_num : int
            Vaza number (1-13).
        starter : GamePlayer
            Player who starts this vaza.
        play_order : list[GamePlayer]
            List of players in play order.
        cards_played_count : int
            Number of cards already played in the round.
        """
        print(GameDisplay.DIVIDER)
        print(f"VAZA {vaza_num}")
        print(GameDisplay.DIVIDER)
        print(f"Starter: {starter.name}")
        print(f"Play order: {', '.join([p.name for p in play_order])}\n")
        
        if cards_played_count > 0:
            print(f"Cards played in previous vazas: {cards_played_count} cards")
        print()
    
    @staticmethod
    def show_ai_play(player: GamePlayer, card: Card):
        """
        Display AI player's card choice.
        
        Parameters
        ----------
        player : GamePlayer
            AI player.
        card : Card
            Card played by AI.
        """
        print(f">>> {player.name} (AI) plays: {card}")
    
    @staticmethod
    def show_ai_no_valid_plays(player: GamePlayer, hand: list[Card]):
        """
        Display warning when AI has no valid plays.
        
        Parameters
        ----------
        player : GamePlayer
            AI player with no valid plays.
        hand : list[Card]
            Player's current hand.
        """
        print(f"⚠️  WARNING: {player.name} (AI) has no valid plays!")
        print(f"   Hand: {GameDisplay.display_card_list(hand)}")
    
    @staticmethod
    def show_human_turn(player: GamePlayer, cards_played: list[Card]):
        """
        Display human player's turn information.
        
        Parameters
        ----------
        player : GamePlayer
            Human player.
        cards_played : list[Card]
            Cards already played in this vaza.
        """
        print(f"{player.name}'s turn:")
        
        if cards_played:
            print(f"  Cards played this vaza: {GameDisplay.display_card_list(cards_played, sort=False)}")
    
    @staticmethod
    def show_card_help():
        """Display card format help."""
        print("\n  Card format examples:")
        print("    - Number + Suit: 2H, 10D, 13C, 14S")
        print("    - Letter + Suit: AH (Ace), KS (King), QD (Queen), JC (Jack)")
        print("    - Suits: H=Hearts, D=Diamonds, C=Clubs, S=Spades")
        print("    - Examples: 'AH' = Ace of Hearts, 'KH' = King of Hearts")
        print("                '7D' = 7 of Diamonds, '10S' = 10 of Spades\n")
    
    @staticmethod
    def show_invalid_card_format():
        """Display invalid card format message."""
        print(f"  ❌ Invalid card format. Try again (or type 'help')\n")
    
    @staticmethod
    def show_card_already_played(card: Card):
        """
        Display message when card was already played.
        
        Parameters
        ----------
        card : Card
            Card that was already played.
        """
        print(f"  ❌ {card} was already played earlier.")
    
    @staticmethod
    def show_card_played(player: GamePlayer, card: Card):
        """
        Display confirmation of card played.
        
        Parameters
        ----------
        player : GamePlayer
            Player who played the card.
        card : Card
            Card that was played.
        """
        print(f"  ✓ {player.name} plays: {card}\n")
    
    @staticmethod
    def show_vaza_winner(winner: GamePlayer, vazas_won: list[int], players: list[GamePlayer]):
        """
        Display vaza winner and current vaza counts.
        
        Parameters
        ----------
        winner : GamePlayer
            Player who won the vaza.
        vazas_won : list[int]
            Number of vazas won by each player.
        players : list[GamePlayer]
            List of all players.
        """
        print(f"🏆 Vaza won by: {winner.name}")
        print(f"Vazas won so far: {', '.join([f'{players[i].name}: {vazas_won[i]}' for i in range(4)])}\n")
    
    @staticmethod
    def show_round_results(round_type: str, players: list[GamePlayer], points: list[int],
                          details: list[str], cumulative_points: list[int]):
        """
        Display round results.
        
        Parameters
        ----------
        round_type : str
            Type of round.
        players : list[GamePlayer]
            List of all players.
        points : list[int]
            Points earned this round.
        details : list[str]
            Detail strings for each player.
        cumulative_points : list[int]
            Cumulative points for all players.
        """
        print("\n" + GameDisplay.DIVIDER)
        print(f"ROUND {round_type.upper()} - RESULTS")
        print(GameDisplay.DIVIDER)
        
        for i, player in enumerate(players):
            print(f"{player.name:20} - {details[i]:30} Points: {points[i]:+5d}")
        
        print(f"\nCumulative points: {', '.join([f'{players[i].name}: {cumulative_points[i]}' for i in range(4)])}")
    
    @staticmethod
    def show_final_standings(player_names: list[str], cumulative_points: list[int]):
        """
        Display final season standings.
        
        Parameters
        ----------
        player_names : list[str]
            Names of all players.
        cumulative_points : list[int]
            Final cumulative points.
        """
        print("\n" + GameDisplay.DIVIDER)
        print("SEASON OVER!")
        print(GameDisplay.DIVIDER)
        print("\nFINAL STANDINGS:\n")
        
        sorted_players = sorted(
            zip(player_names, cumulative_points),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (player, points) in enumerate(sorted_players, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            print(f"{medal} {i}. {player:20} - {points:+5d} points")
        
        print(GameDisplay.DIVIDER)
    
    @staticmethod
    def get_round_description(round_type: str) -> str:
        """
        Get description of what to avoid/collect in each round.
        
        Parameters
        ----------
        round_type : str
            Type of round (vazas, copas, homens, mulheres, king, last).
        
        Returns
        -------
        str
            Description of round objective.
        """
        descriptions = {
            "vazas": "Avoid winning vazas",
            "copas": "Avoid collecting Hearts (♥)",
            "homens": "Avoid collecting Jacks and Kings",
            "mulheres": "Avoid collecting Queens",
            "king": "Avoid the King of Hearts (K♥)",
            "last": "Avoid winning the last vaza"
        }
        return descriptions.get(round_type, "")
    
    @staticmethod
    def get_round_detail(round_type: str, current_round: Round, player_idx: int) -> str:
        """
        Get detail about what player collected this round.
        
        Parameters
        ----------
        round_type : str
            Type of round.
        current_round : Round
            Current round object.
        player_idx : int
            Player index (0-3).
        
        Returns
        -------
        str
            Description of what the player collected.
        """
        if round_type == "vazas":
            return f"{current_round.vazas_won[player_idx]} vazas"
        elif round_type == "copas":
            hearts = current_round.count_suit(player_idx, Suit.HEARTS)
            return f"{hearts} hearts"
        elif round_type == "homens":
            men = sum(1 for c in current_round.cards_won[player_idx] 
                      if c.rank == Rank.JACK or c.rank == Rank.KING)
            return f"{men} men (J+K)"
        elif round_type == "mulheres":
            queens = sum(1 for c in current_round.cards_won[player_idx]
                         if c.rank == Rank.QUEEN)
            return f"{queens} queens"
        elif round_type == "king":
            has_king = any(c.rank == Rank.KING and c.suit == Suit.HEARTS 
                          for c in current_round.cards_won[player_idx])
            return "King of Hearts!" if has_king else "Safe"
        elif round_type == "last":
            won_last = current_round.vazas_won[player_idx] > 0
            return "Won last vaza!" if won_last else "Safe"
        return ""
