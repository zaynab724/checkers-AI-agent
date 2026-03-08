"""
GameBoard.py

Computational representation of a Checkers state.
Includes:
- initial state
- successor function (GetLegalMoves)
- goal test
- applying moves (ApplyMove)
Rules implemented:
- men move forward diagonals
- kings move both directions
- captures are mandatory if any capture exists
- multi-jump captures are supported
"""

from typing import List, Tuple, Optional


class GameBoard:
    """
    Representation:
      0  = empty
      1  = WhiteMan
      2  = WhiteKing
     -1  = BlackMan
     -2  = BlackKing

    Coordinates: (RowIndex, ColIndex) = 0..7.
    WHITE moves upward (RowIndex decreases).
    BLACK moves downward (RowIndex increases).
    """

    def __init__(self) -> None:
        self.BoardMatrix = [[0 for _ in range(8)] for _ in range(8)]
        self.InitializeBoard()

    def InitializeBoard(self) -> None:
        for RowIndex in range(8):
            for ColIndex in range(8):
                self.BoardMatrix[RowIndex][ColIndex] = 0

        # Black on top 3 rows (dark squares)
        for RowIndex in range(3):
            for ColIndex in range(8):
                if (RowIndex + ColIndex) % 2 == 1:
                    self.BoardMatrix[RowIndex][ColIndex] = -1

        # White on bottom 3 rows (dark squares)
        for RowIndex in range(5, 8):
            for ColIndex in range(8):
                if (RowIndex + ColIndex) % 2 == 1:
                    self.BoardMatrix[RowIndex][ColIndex] = 1

    def CopyBoard(self) -> "GameBoard":
        NewBoard = GameBoard()
        NewBoard.BoardMatrix = [Row[:] for Row in self.BoardMatrix]
        return NewBoard

    def PrintBoard(self) -> None:
        PieceMap = {0: ".", 1: "w", 2: "W", -1: "b", -2: "B"}
        print("\n    " + " ".join([str(C + 1) for C in range(8)]))
        for R in range(8):
            RowText = [PieceMap[self.BoardMatrix[R][C]] for C in range(8)]
            print(f"{R + 1:>2}  " + " ".join(RowText))
        WhiteCount, BlackCount = self.CountPieces()
        print(f"\nWhitePieces: {WhiteCount} | BlackPieces: {BlackCount}")

    def CountPieces(self) -> Tuple[int, int]:
        WhiteCount = 0
        BlackCount = 0
        for R in range(8):
            for C in range(8):
                V = self.BoardMatrix[R][C]
                if V > 0:
                    WhiteCount += 1
                elif V < 0:
                    BlackCount += 1
        return WhiteCount, BlackCount

    def IsGoalState(self) -> Optional[str]:
        WhiteCount, BlackCount = self.CountPieces()
        if WhiteCount == 0:
            return "BLACK"
        if BlackCount == 0:
            return "WHITE"
        return None

    # =========================================================
    # Successor function
    # =========================================================

    def GetLegalMoves(self, PlayerSide: str) -> List[List[Tuple[int, int]]]:
        """
        Returns list of move paths.
        Simple: [(r0,c0),(r1,c1)]
        Capture (possibly multi-jump): [(r0,c0),(r2,c2),(r4,c4),...]
        Forced captures: if any capture exists, return only captures.
        """
        CaptureMoves: List[List[Tuple[int, int]]] = []
        SimpleMoves: List[List[Tuple[int, int]]] = []

        for StartRow in range(8):
            for StartCol in range(8):
                PieceValue = self.BoardMatrix[StartRow][StartCol]
                if not self._IsPlayerPiece(PlayerSide, PieceValue):
                    continue

                PieceCaptureMoves = self._GenerateCaptureMovesFrom(StartRow, StartCol, PieceValue)
                if PieceCaptureMoves:
                    CaptureMoves.extend(PieceCaptureMoves)
                else:
                    PieceSimpleMoves = self._GenerateSimpleMovesFrom(StartRow, StartCol, PieceValue)
                    SimpleMoves.extend(PieceSimpleMoves)

        return CaptureMoves if CaptureMoves else SimpleMoves

    def _IsPlayerPiece(self, PlayerSide: str, PieceValue: int) -> bool:
        if PlayerSide == "WHITE":
            return PieceValue > 0
        return PieceValue < 0

    def _GetMoveDirections(self, PieceValue: int) -> List[Tuple[int, int]]:
        # Kings move both directions.
        if abs(PieceValue) == 2:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        # White men move up.
        if PieceValue > 0:
            return [(-1, -1), (-1, 1)]
        # Black men move down.
        return [(1, -1), (1, 1)]

    def _GenerateSimpleMovesFrom(self, StartRow: int, StartCol: int, PieceValue: int) -> List[List[Tuple[int, int]]]:
        Moves: List[List[Tuple[int, int]]] = []
        for (RowStep, ColStep) in self._GetMoveDirections(PieceValue):
            NextRow = StartRow + RowStep
            NextCol = StartCol + ColStep
            if self._InBounds(NextRow, NextCol) and self.BoardMatrix[NextRow][NextCol] == 0:
                Moves.append([(StartRow, StartCol), (NextRow, NextCol)])
        return Moves

    def _GenerateCaptureMovesFrom(self, StartRow: int, StartCol: int, PieceValue: int) -> List[List[Tuple[int, int]]]:
        """
        Multi-jump capture generation via DFS on possible capture continuations.
        """
        AllPaths: List[List[Tuple[int, int]]] = []
        self._CaptureDFS(
            CurrentRow=StartRow,
            CurrentCol=StartCol,
            PieceValue=PieceValue,
            CurrentPath=[(StartRow, StartCol)],
            CurrentBoard=self,
            OutputPaths=AllPaths
        )

        # Keep only paths that actually capture at least once (jump length 2)
        ValidPaths: List[List[Tuple[int, int]]] = []
        for Path in AllPaths:
            if len(Path) >= 2:
                (R0, C0) = Path[0]
                (R1, C1) = Path[1]
                if abs(R1 - R0) == 2 and abs(C1 - C0) == 2:
                    ValidPaths.append(Path)

        return ValidPaths

    def _CaptureDFS(
            self,
            CurrentRow: int,
            CurrentCol: int,
            PieceValue: int,
            CurrentPath: List[Tuple[int, int]],
            CurrentBoard: "GameBoard",
            OutputPaths: List[List[Tuple[int, int]]]
    ) -> None:
        Directions = CurrentBoard._GetMoveDirections(PieceValue)
        FoundExtension = False

        for (RowStep, ColStep) in Directions:
            MidRow = CurrentRow + RowStep
            MidCol = CurrentCol + ColStep
            LandRow = CurrentRow + 2 * RowStep
            LandCol = CurrentCol + 2 * ColStep

            if not CurrentBoard._InBounds(LandRow, LandCol):
                continue

            MiddleValue = CurrentBoard.BoardMatrix[MidRow][MidCol]
            LandingEmpty = (CurrentBoard.BoardMatrix[LandRow][LandCol] == 0)

            if LandingEmpty and CurrentBoard._IsOpponent(PieceValue, MiddleValue):
                FoundExtension = True
                NextBoard = CurrentBoard.CopyBoard()

                # Move piece & remove captured
                NextBoard.BoardMatrix[CurrentRow][CurrentCol] = 0
                NextBoard.BoardMatrix[MidRow][MidCol] = 0

                NextPieceValue = PieceValue

                # Promote immediately if reaching king row (common variant; acceptable for project)
                if NextPieceValue == 1 and LandRow == 0:
                    NextPieceValue = 2
                if NextPieceValue == -1 and LandRow == 7:
                    NextPieceValue = -2

                NextBoard.BoardMatrix[LandRow][LandCol] = NextPieceValue

                NextPath = CurrentPath + [(LandRow, LandCol)]
                self._CaptureDFS(
                    CurrentRow=LandRow,
                    CurrentCol=LandCol,
                    PieceValue=NextPieceValue,
                    CurrentPath=NextPath,
                    CurrentBoard=NextBoard,
                    OutputPaths=OutputPaths
                )

        if not FoundExtension:
            OutputPaths.append(CurrentPath)

    def _IsOpponent(self, PieceValue: int, OtherValue: int) -> bool:
        if PieceValue == 0 or OtherValue == 0:
            return False
        return (PieceValue > 0 and OtherValue < 0) or (PieceValue < 0 and OtherValue > 0)

    def _InBounds(self, RowIndex: int, ColIndex: int) -> bool:
        return 0 <= RowIndex < 8 and 0 <= ColIndex < 8

    # =========================================================
    # Apply Move
    # =========================================================

    def ApplyMove(self, MovePath: List[Tuple[int, int]]) -> "GameBoard":
        NewBoard = self.CopyBoard()

        (StartRow, StartCol) = MovePath[0]
        PieceValue = NewBoard.BoardMatrix[StartRow][StartCol]
        NewBoard.BoardMatrix[StartRow][StartCol] = 0

        # Walk path, remove captured pieces when jump occurs
        for StepIndex in range(1, len(MovePath)):
            (PrevRow, PrevCol) = MovePath[StepIndex - 1]
            (NextRow, NextCol) = MovePath[StepIndex]
            RowDelta = NextRow - PrevRow
            ColDelta = NextCol - PrevCol

            # capture jump
            if abs(RowDelta) == 2 and abs(ColDelta) == 2:
                CapturedRow = PrevRow + (RowDelta // 2)
                CapturedCol = PrevCol + (ColDelta // 2)
                NewBoard.BoardMatrix[CapturedRow][CapturedCol] = 0

        (EndRow, EndCol) = MovePath[-1]

        # Promotion at end
        if PieceValue == 1 and EndRow == 0:
            PieceValue = 2
        if PieceValue == -1 and EndRow == 7:
            PieceValue = -2

        NewBoard.BoardMatrix[EndRow][EndCol] = PieceValue
        return NewBoard