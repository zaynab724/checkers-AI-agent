"""
PlayingTheGame.py

Runs the game loop:
- Human (WHITE) starts
- Bot (BLACK) responds
- Prints analytics per move and cumulative
"""

from typing import List, Tuple, Optional

from GameBoard import GameBoard
from SearchToolBox import SearchToolBox
from OtherStuff import MoveAnalytics, GameAnalytics, OtherStuff


class PlayingTheGame:

    def __init__(self, StrategyName: str = "AlphaBetaWithOrdering", TimeLimitSeconds: int = 2, PlyLimit: int = 6) -> None:
        self.GameBoardObj = GameBoard()
        self.SearchToolBoxObj = SearchToolBox(StrategyName, TimeLimitSeconds, PlyLimit)
        self.GameAnalyticsObj = GameAnalytics()

    def StartGame(self) -> None:
        print("\nCheckers Bot (CSC-3309 Project 2)")
        print("Human = WHITE (starts first) | Bot = BLACK\n")
        print("Input: StartingMoveLocation(X,Y) then TargetingMoveLocation(X,Y)")
        print("For multi-jump capture: keep entering targets, then type 'q' to finish.")
        print("Forced captures are enforced.\n")

        CurrentPlayer = "WHITE"
        TurnNumber = 0

        while True:
            self.GameBoardObj.PrintBoard()

            Winner = self.GameBoardObj.IsGoalState()
            if Winner is not None:
                print(f"\nGAME OVER! Winner: {Winner}")
                OtherStuff.PrintCumulativeAnalytics(self.GameAnalyticsObj)
                return

            TurnNumber += 1
            print(f"\n----------------- TURN {TurnNumber} ({CurrentPlayer}) -----------------")

            if CurrentPlayer == "WHITE":
                MovePath, HumanAnalytics = self._HumanTurn()
                if MovePath is None:
                    print("\nNo legal moves for WHITE. BLACK wins.")
                    OtherStuff.PrintCumulativeAnalytics(self.GameAnalyticsObj)
                    return

                self.GameBoardObj = self.GameBoardObj.ApplyMove(MovePath)
                OtherStuff.MergeAnalytics(self.GameAnalyticsObj.WhiteCumulative, HumanAnalytics)
                OtherStuff.PrintMoveAnalytics("WHITE (Human)", MovePath, HumanAnalytics)
                CurrentPlayer = "BLACK"

            else:
                BotMovePath, BotAnalytics = self._BotTurn()
                if BotMovePath is None:
                    print("\nNo legal moves for BLACK. WHITE wins.")
                    OtherStuff.PrintCumulativeAnalytics(self.GameAnalyticsObj)
                    return

                self.GameBoardObj = self.GameBoardObj.ApplyMove(BotMovePath)
                OtherStuff.MergeAnalytics(self.GameAnalyticsObj.BlackCumulative, BotAnalytics)
                OtherStuff.PrintMoveAnalytics("BLACK (Bot)", BotMovePath, BotAnalytics)
                CurrentPlayer = "WHITE"

    def _HumanTurn(self) -> Tuple[Optional[List[Tuple[int, int]]], MoveAnalytics]:
        AnalyticsObj = MoveAnalytics()  # human has 0 nodes expanded, etc.
        LegalMoves = self.GameBoardObj.GetLegalMoves("WHITE")
        if not LegalMoves:
            return None, AnalyticsObj

        print("\nYour move (WHITE).")
        print("Enter two integers: Line Column (1..8).")

        # Required identifier label (Python-safe): variable named StartingMoveLocation
        StartingMoveLocation = self._ReadLineCol("StartingMoveLocation(X,Y)")  # StartingMoveLocation(X,Y)
        StartingRow = StartingMoveLocation[0] - 1
        StartingCol = StartingMoveLocation[1] - 1

        MovePath: List[Tuple[int, int]] = [(StartingRow, StartingCol)]

        while True:
            TargetingMoveLocation = self._ReadLineCol("TargetingMoveLocation(X,Y) or 'q' to finish", AllowQuit=True)  # TargetingMoveLocation(X,Y)
            if TargetingMoveLocation is None:
                break
            TargetRow = TargetingMoveLocation[0] - 1
            TargetCol = TargetingMoveLocation[1] - 1
            MovePath.append((TargetRow, TargetCol))

        # Must match exactly one legal path
        if MovePath in LegalMoves:
            return MovePath, AnalyticsObj

        # If invalid, show samples and retry
        print("\n❌ Invalid move path. Some legal moves (up to 12):")
        for Index, LM in enumerate(LegalMoves[:12], start=1):
            HR = [(R + 1, C + 1) for (R, C) in LM]
            print(f"{Index}. {HR}")
        print("Try again.\n")
        return self._HumanTurn()

    def _BotTurn(self) -> Tuple[Optional[List[Tuple[int, int]]], MoveAnalytics]:
        print(f"\nBot thinking: {self.SearchToolBoxObj.StrategyName} (T={self.SearchToolBoxObj.TimeLimitSeconds}s, P={self.SearchToolBoxObj.PlyLimit}) ...")
        MovePath, AnalyticsObj = self.SearchToolBoxObj.ChooseBestMoveForBlack(self.GameBoardObj)
        return MovePath, AnalyticsObj

    def _ReadLineCol(self, PromptLabel: str, AllowQuit: bool = False) -> Optional[Tuple[int, int]]:
        while True:
            UserInput = input(f"{PromptLabel}: ").strip().lower()
            if AllowQuit and UserInput == "q":
                return None
            Parts = UserInput.split()
            if len(Parts) != 2:
                print("Enter two integers: Line Column (example: 6 1).")
                continue
            try:
                LineValue = int(Parts[0])
                ColumnValue = int(Parts[1])
                if not (1 <= LineValue <= 8 and 1 <= ColumnValue <= 8):
                    print("Line and Column must be between 1 and 8.")
                    continue
                return (LineValue, ColumnValue)
            except ValueError:
                print("Invalid input. Enter integers like: 6 1")