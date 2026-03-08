from PlayingTheGame import PlayingTheGame

if __name__ == "__main__":
    # Contract parameters:
    # S: "Minimax", "AlphaBetaPruning", "AlphaBetaWithOrdering"
    # T: 1..3
    # P: 5..9

    StrategyName = "AlphaBetaWithOrdering"
    TimeLimitSeconds = 2
    PlyLimit = 7

    Game = PlayingTheGame(
        StrategyName=StrategyName,
        TimeLimitSeconds=TimeLimitSeconds,
        PlyLimit=PlyLimit
    )
    Game.StartGame()