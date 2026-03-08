"""
CheckersGUI.py

Stable Tkinter GUI for the Checkers AI project.
Includes:
- Board rendering
- Score display
- Bot analytics
- Illegal move popup
"""

import tkinter as tk
from tkinter import messagebox

from GameBoard import GameBoard
from SearchToolBox import SearchToolBox


class CheckersGUI:

    def __init__(self):

        self.GameBoardObj = GameBoard()
        self.SearchToolBoxObj = SearchToolBox("AlphaBetaWithOrdering", 2, 7)

        self.SelectedPiece = None
        self.CellSize = 70

        self.Window = tk.Tk()
        self.Window.title("Checkers AI Bot")
        self.Window.configure(bg="#1e1e1e")

        self.Canvas = tk.Canvas(
            self.Window,
            width=8 * self.CellSize,
            height=8 * self.CellSize,
            highlightthickness=0
        )

        self.Canvas.grid(row=0, column=0, columnspan=8)
        self.Canvas.bind("<Button-1>", self.HandleClick)

        self.ScoreLabel = tk.Label(
            self.Window,
            text="White: 12 | Black: 12",
            font=("Arial", 14, "bold"),
            bg="#1e1e1e",
            fg="white"
        )

        self.ScoreLabel.grid(row=1, column=0, columnspan=8, pady=6)

        self.AnalyticsLabel = tk.Label(
            self.Window,
            text="Bot Analytics",
            font=("Arial", 12),
            bg="#2c2c2c",
            fg="white",
            width=50,
            height=8,
            justify="left"
        )

        self.AnalyticsLabel.grid(row=2, column=0, columnspan=8, pady=10)

        self.DrawBoard()

    # --------------------------------------------------

    def DrawBoard(self):

        self.Canvas.delete("all")

        for row in range(8):
            for col in range(8):

                x1 = col * self.CellSize
                y1 = row * self.CellSize
                x2 = x1 + self.CellSize
                y2 = y1 + self.CellSize

                color = "#2E7D32" if (row + col) % 2 else "#EEEED2"

                self.Canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="black"
                )

                piece = self.GameBoardObj.BoardMatrix[row][col]

                if piece != 0:
                    self.DrawPiece(row, col, piece)

    # --------------------------------------------------

    def DrawPiece(self, row, col, piece):

        margin = 10

        x1 = col * self.CellSize + margin
        y1 = row * self.CellSize + margin
        x2 = (col + 1) * self.CellSize - margin
        y2 = (row + 1) * self.CellSize - margin

        color = "white" if piece > 0 else "black"

        self.Canvas.create_oval(
            x1, y1, x2, y2,
            fill=color,
            outline="black",
            width=2
        )

        if abs(piece) == 2:
            self.Canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text="K",
                font=("Arial", 16, "bold"),
                fill="red"
            )

    # --------------------------------------------------

    def HandleClick(self, event):

        col = event.x // self.CellSize
        row = event.y // self.CellSize

        # Ignore clicks outside board
        if row < 0 or row > 7 or col < 0 or col > 7:
            return

        # First click (select piece)
        if self.SelectedPiece is None:

            piece = self.GameBoardObj.BoardMatrix[row][col]

            if piece > 0:
                self.SelectedPiece = (row, col)

        # Second click (try move)
        else:

            start = self.SelectedPiece
            target = (row, col)

            legalMoves = self.GameBoardObj.GetLegalMoves("WHITE")

            chosenMove = None

            for move in legalMoves:
                if move[0] == start and move[-1] == target:
                    chosenMove = move
                    break

            if chosenMove is not None:

                self.GameBoardObj = self.GameBoardObj.ApplyMove(chosenMove)

                self.UpdateScore()

                self.DrawBoard()
                self.Window.update()

                winner = self.GameBoardObj.IsGoalState()

                if winner is not None:
                    self.AnalyticsLabel["text"] = f"Winner: {winner}"
                    self.SelectedPiece = None
                    return

                # AI move
                self.BotMove()

            else:

                messagebox.showwarning(
                    "Illegal Move",
                    "That move is not allowed.\nPlease choose a valid move."
                )

            self.SelectedPiece = None

    # --------------------------------------------------

    def BotMove(self):

        bestMove, analytics = self.SearchToolBoxObj.ChooseBestMoveForBlack(self.GameBoardObj)

        if bestMove is None:
            self.AnalyticsLabel["text"] = "Winner: WHITE"
            return

        self.GameBoardObj = self.GameBoardObj.ApplyMove(bestMove)

        self.UpdateScore()

        self.DrawBoard()

        self.AnalyticsLabel["text"] = (
            "Bot Analytics\n\n"
            f"Nodes Expanded : {analytics.NumberNodesExpanded}\n"
            f"Nodes Pruned   : {analytics.NumberPrunedBranches}\n"
            f"Time Cutoffs   : {analytics.NumberCutoffsByTime}\n"
            f"Depth Reached  : {analytics.DepthReached}\n"
            f"Search Time    : {analytics.SearchSeconds:.2f} seconds"
        )

        winner = self.GameBoardObj.IsGoalState()

        if winner is not None:
            self.AnalyticsLabel["text"] += f"\n\nWinner: {winner}"

    # --------------------------------------------------

    def UpdateScore(self):

        whitePieces = 0
        blackPieces = 0

        for row in range(8):
            for col in range(8):

                piece = self.GameBoardObj.BoardMatrix[row][col]

                if piece > 0:
                    whitePieces += 1
                elif piece < 0:
                    blackPieces += 1

        self.ScoreLabel["text"] = f"White: {whitePieces} | Black: {blackPieces}"

    # --------------------------------------------------

    def Start(self):
        self.Window.mainloop()