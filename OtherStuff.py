"""
OtherStuff.py

Handles:
- Move analytics
- Cumulative analytics
- Utility timing functions
"""

import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class MoveAnalytics:
    NumberNodesExpanded: int = 0
    NumberCutoffsByTime: int = 0
    NumberPrunedBranches: int = 0
    NumberMoveOrderings: int = 0
    OrderingEstimatedGain: int = 0
    SearchSeconds: float = 0.0
    DepthReached: int = 0


@dataclass
class GameAnalytics:
    WhiteCumulative: MoveAnalytics = field(default_factory=MoveAnalytics)
    BlackCumulative: MoveAnalytics = field(default_factory=MoveAnalytics)


class OtherStuff:
    """Timing + reporting + analytics merge."""

    @staticmethod
    def NowSeconds() -> float:
        return time.perf_counter()

    @staticmethod
    def MergeAnalytics(Target: MoveAnalytics, Source: MoveAnalytics) -> None:
        Target.NumberNodesExpanded += Source.NumberNodesExpanded
        Target.NumberCutoffsByTime += Source.NumberCutoffsByTime
        Target.NumberPrunedBranches += Source.NumberPrunedBranches
        Target.NumberMoveOrderings += Source.NumberMoveOrderings
        Target.OrderingEstimatedGain += Source.OrderingEstimatedGain
        Target.SearchSeconds += Source.SearchSeconds
        Target.DepthReached = max(Target.DepthReached, Source.DepthReached)

    @staticmethod
    def PrintMoveAnalytics(PlayerLabel: str, MoveChosen: List[Tuple[int, int]], AnalyticsObj: MoveAnalytics) -> None:
        HumanReadableMove = [(R + 1, C + 1) for (R, C) in MoveChosen]
        print(f"\n=== Analytics for {PlayerLabel} Move ===")
        print(f"MoveChosenPath: {HumanReadableMove}")
        print(f"DepthReached: {AnalyticsObj.DepthReached}")
        print(f"SearchSeconds: {AnalyticsObj.SearchSeconds:.4f}")
        print(f"NumberNodesExpanded: {AnalyticsObj.NumberNodesExpanded}")
        print(f"NumberPrunedBranches: {AnalyticsObj.NumberPrunedBranches}")
        print(f"NumberCutoffsByTime: {AnalyticsObj.NumberCutoffsByTime}")
        print(f"NumberMoveOrderings: {AnalyticsObj.NumberMoveOrderings}")
        print(f"OrderingEstimatedGain: {AnalyticsObj.OrderingEstimatedGain}")

    @staticmethod
    def PrintCumulativeAnalytics(GameAnalyticsObj: GameAnalytics) -> None:
        print("\n================= CUMULATIVE ANALYTICS =================")
        print("\nWHITE (Human) cumulative:")
        OtherStuff.PrintMoveAnalytics("WHITE", [], GameAnalyticsObj.WhiteCumulative)
        print("\nBLACK (Bot) cumulative:")
        OtherStuff.PrintMoveAnalytics("BLACK", [], GameAnalyticsObj.BlackCumulative)
        print("========================================================\n")