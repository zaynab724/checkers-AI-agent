"""
SearchToolBox.py

Implements:
- Minimax
- AlphaBetaPruning
- AlphaBetaWithOrdering
With contract:
- TimeLimitSeconds (T): 1..3
- PlyLimit (P): 5..9
"""

from typing import List, Tuple, Optional

from GameBoard import GameBoard
from OtherStuff import MoveAnalytics, OtherStuff


class SearchToolBox:

    def __init__(self, StrategyName: str, TimeLimitSeconds: int, PlyLimit: int) -> None:
        self.StrategyName = StrategyName  # "Minimax" / "AlphaBetaPruning" / "AlphaBetaWithOrdering"
        self.TimeLimitSeconds = max(1, min(3, int(TimeLimitSeconds)))
        self.PlyLimit = max(5, min(9, int(PlyLimit)))

    def ChooseBestMoveForBlack(self, CurrentBoard: GameBoard) -> Tuple[Optional[List[Tuple[int, int]]], MoveAnalytics]:
        StartTime = OtherStuff.NowSeconds()
        Deadline = StartTime + float(self.TimeLimitSeconds)

        AnalyticsObj = MoveAnalytics()
        BestMoveSoFar: Optional[List[Tuple[int, int]]] = None
        BestScoreSoFar = float("-inf")

        # Iterative deepening from 1..P
        for DepthLimit in range(1, self.PlyLimit + 1):
            if OtherStuff.NowSeconds() >= Deadline:
                AnalyticsObj.NumberCutoffsByTime += 1
                break

            CandidateMove, CandidateScore = self._RootSearch(CurrentBoard, DepthLimit, Deadline, AnalyticsObj)
            if CandidateMove is not None:
                BestMoveSoFar = CandidateMove
                BestScoreSoFar = CandidateScore
                AnalyticsObj.DepthReached = DepthLimit

        AnalyticsObj.SearchSeconds = OtherStuff.NowSeconds() - StartTime
        return BestMoveSoFar, AnalyticsObj

    def _RootSearch(
            self,
            CurrentBoard: GameBoard,
            DepthLimit: int,
            Deadline: float,
            AnalyticsObj: MoveAnalytics
    ) -> Tuple[Optional[List[Tuple[int, int]]], float]:

        LegalMoves = CurrentBoard.GetLegalMoves("BLACK")
        if not LegalMoves:
            return None, float("-inf")

        if self.StrategyName == "AlphaBetaWithOrdering":
            AnalyticsObj.NumberMoveOrderings += 1
            LegalMoves = self._OrderMoves(CurrentBoard, LegalMoves, PlayerSide="BLACK")

        BestMove: Optional[List[Tuple[int, int]]] = None
        BestScore = float("-inf")

        for MovePath in LegalMoves:
            if OtherStuff.NowSeconds() >= Deadline:
                AnalyticsObj.NumberCutoffsByTime += 1
                break

            NextBoard = CurrentBoard.ApplyMove(MovePath)

            if self.StrategyName == "Minimax":
                Score = self._MinValue(NextBoard, DepthLimit - 1, Deadline, AnalyticsObj)
            else:
                Score = self._AlphaBetaMinValue(NextBoard, DepthLimit - 1, float("-inf"), float("inf"), Deadline, AnalyticsObj)

            if Score > BestScore:
                BestScore = Score
                BestMove = MovePath

        return BestMove, BestScore

    # =========================================================
    # Minimax
    # =========================================================

    def _MaxValue(self, CurrentBoard: GameBoard, DepthRemaining: int, Deadline: float, AnalyticsObj: MoveAnalytics) -> float:
        if OtherStuff.NowSeconds() >= Deadline:
            AnalyticsObj.NumberCutoffsByTime += 1
            return self.EvaluateBoard(CurrentBoard)

        Winner = CurrentBoard.IsGoalState()
        if Winner is not None or DepthRemaining == 0:
            return self.EvaluateBoard(CurrentBoard)

        AnalyticsObj.NumberNodesExpanded += 1

        LegalMoves = CurrentBoard.GetLegalMoves("BLACK")
        if not LegalMoves:
            return float("-inf")

        Value = float("-inf")
        for MovePath in LegalMoves:
            Value = max(Value, self._MinValue(CurrentBoard.ApplyMove(MovePath), DepthRemaining - 1, Deadline, AnalyticsObj))
        return Value

    def _MinValue(self, CurrentBoard: GameBoard, DepthRemaining: int, Deadline: float, AnalyticsObj: MoveAnalytics) -> float:
        if OtherStuff.NowSeconds() >= Deadline:
            AnalyticsObj.NumberCutoffsByTime += 1
            return self.EvaluateBoard(CurrentBoard)

        Winner = CurrentBoard.IsGoalState()
        if Winner is not None or DepthRemaining == 0:
            return self.EvaluateBoard(CurrentBoard)

        AnalyticsObj.NumberNodesExpanded += 1

        LegalMoves = CurrentBoard.GetLegalMoves("WHITE")
        if not LegalMoves:
            return float("inf")

        Value = float("inf")
        for MovePath in LegalMoves:
            Value = min(Value, self._MaxValue(CurrentBoard.ApplyMove(MovePath), DepthRemaining - 1, Deadline, AnalyticsObj))
        return Value

    # =========================================================
    # Alpha-Beta
    # =========================================================

    def _AlphaBetaMaxValue(
            self,
            CurrentBoard: GameBoard,
            DepthRemaining: int,
            Alpha: float,
            Beta: float,
            Deadline: float,
            AnalyticsObj: MoveAnalytics
    ) -> float:
        if OtherStuff.NowSeconds() >= Deadline:
            AnalyticsObj.NumberCutoffsByTime += 1
            return self.EvaluateBoard(CurrentBoard)

        Winner = CurrentBoard.IsGoalState()
        if Winner is not None or DepthRemaining == 0:
            return self.EvaluateBoard(CurrentBoard)

        AnalyticsObj.NumberNodesExpanded += 1

        LegalMoves = CurrentBoard.GetLegalMoves("BLACK")
        if self.StrategyName == "AlphaBetaWithOrdering":
            AnalyticsObj.NumberMoveOrderings += 1
            LegalMoves = self._OrderMoves(CurrentBoard, LegalMoves, PlayerSide="BLACK")

        Value = float("-inf")
        for MoveIndex, MovePath in enumerate(LegalMoves):
            Value = max(Value, self._AlphaBetaMinValue(CurrentBoard.ApplyMove(MovePath), DepthRemaining - 1, Alpha, Beta, Deadline, AnalyticsObj))
            if Value >= Beta:
                AnalyticsObj.NumberPrunedBranches += 1
                # gain proxy: how many siblings we didn't explore due to cutoff
                AnalyticsObj.OrderingEstimatedGain += max(0, len(LegalMoves) - MoveIndex - 1)
                return Value
            Alpha = max(Alpha, Value)
        return Value

    def _AlphaBetaMinValue(
            self,
            CurrentBoard: GameBoard,
            DepthRemaining: int,
            Alpha: float,
            Beta: float,
            Deadline: float,
            AnalyticsObj: MoveAnalytics
    ) -> float:
        if OtherStuff.NowSeconds() >= Deadline:
            AnalyticsObj.NumberCutoffsByTime += 1
            return self.EvaluateBoard(CurrentBoard)

        Winner = CurrentBoard.IsGoalState()
        if Winner is not None or DepthRemaining == 0:
            return self.EvaluateBoard(CurrentBoard)

        AnalyticsObj.NumberNodesExpanded += 1

        LegalMoves = CurrentBoard.GetLegalMoves("WHITE")
        if self.StrategyName == "AlphaBetaWithOrdering":
            AnalyticsObj.NumberMoveOrderings += 1
            LegalMoves = self._OrderMoves(CurrentBoard, LegalMoves, PlayerSide="WHITE")

        Value = float("inf")
        for MoveIndex, MovePath in enumerate(LegalMoves):
            Value = min(Value, self._AlphaBetaMaxValue(CurrentBoard.ApplyMove(MovePath), DepthRemaining - 1, Alpha, Beta, Deadline, AnalyticsObj))
            if Value <= Alpha:
                AnalyticsObj.NumberPrunedBranches += 1
                AnalyticsObj.OrderingEstimatedGain += max(0, len(LegalMoves) - MoveIndex - 1)
                return Value
            Beta = min(Beta, Value)
        return Value

    # =========================================================
    # Heuristic
    # =========================================================

    def EvaluateBoard(self, CurrentBoard: GameBoard) -> float:
        """
        Positive => good for BLACK (bot)
        Negative => good for WHITE (human)
        Heuristic features:
        - material (men/kings)
        - mobility (number of legal moves)
        """
        WhiteMen = 0
        WhiteKings = 0
        BlackMen = 0
        BlackKings = 0

        for R in range(8):
            for C in range(8):
                V = CurrentBoard.BoardMatrix[R][C]
                if V == 1:
                    WhiteMen += 1
                elif V == 2:
                    WhiteKings += 1
                elif V == -1:
                    BlackMen += 1
                elif V == -2:
                    BlackKings += 1

        WhiteMoves = len(CurrentBoard.GetLegalMoves("WHITE"))
        BlackMoves = len(CurrentBoard.GetLegalMoves("BLACK"))

        Score = 0.0
        Score += 3.0 * BlackMen + 5.0 * BlackKings
        Score -= 3.0 * WhiteMen + 5.0 * WhiteKings
        Score += 0.2 * (BlackMoves - WhiteMoves)
        return Score

    # =========================================================
    # Ordering
    # =========================================================

    def _OrderMoves(self, CurrentBoard: GameBoard, MovesList: List[List[Tuple[int, int]]], PlayerSide: str) -> List[List[Tuple[int, int]]]:
        """
        High-impact first:
        - captures first (including longer multi-jumps)
        - promotions
        """

        def IsCaptureMove(MovePath: List[Tuple[int, int]]) -> bool:
            if len(MovePath) < 2:
                return False
            (R0, C0) = MovePath[0]
            (R1, C1) = MovePath[1]
            return abs(R1 - R0) == 2 and abs(C1 - C0) == 2

        def IsPromotion(MovePath: List[Tuple[int, int]]) -> bool:
            (SR, SC) = MovePath[0]
            (ER, EC) = MovePath[-1]
            PieceValue = CurrentBoard.BoardMatrix[SR][SC]
            if PlayerSide == "BLACK":
                return PieceValue == -1 and ER == 7
            return PieceValue == 1 and ER == 0

        def MoveKey(MovePath: List[Tuple[int, int]]) -> Tuple[int, int, int]:
            CaptureFlag = 1 if IsCaptureMove(MovePath) else 0
            PromotionFlag = 1 if IsPromotion(MovePath) else 0
            CaptureLength = len(MovePath)
            return (CaptureFlag, PromotionFlag, CaptureLength)

        return sorted(MovesList, key=MoveKey, reverse=True)