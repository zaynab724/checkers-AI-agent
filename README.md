# Checkers AI Agent

Artificial Intelligence project implementing a Checkers-playing agent using **adversarial search algorithms**.
The agent uses **Minimax with Alpha-Beta pruning** to choose optimal moves against a human player.

This project was developed as part of **CSC-3309 – Artificial Intelligence**.

---

## Project Overview

The goal of this project is to design an intelligent Checkers agent capable of playing against a human opponent.
The agent analyzes possible future board states and selects moves that maximize its chances of winning.

The system includes:

* A **graphical interface** for playing the game
* A **game board representation**
* An **AI agent using adversarial search**
* A **heuristic evaluation function**

---

## Algorithms Used

### Minimax

The AI uses the **Minimax algorithm**, which models the game as a search tree.

* The AI tries to **maximize** the board evaluation score.
* The opponent tries to **minimize** the score.

The algorithm evaluates possible future moves and chooses the best decision assuming both players play optimally.

---

### Alpha-Beta Pruning

Alpha-Beta pruning improves Minimax efficiency by **eliminating branches of the search tree that cannot affect the final decision**.

Benefits:

* Reduces the number of explored states
* Allows deeper search within the same time limit
* Maintains the same optimal decision as Minimax

---

## Project Structure

```
CheckersGUI.py      → Graphical interface of the game
GameBoard.py        → Board representation and game rules
SearchToolBox.py    → Minimax and Alpha-Beta implementation
PlayingTheGame.py   → Game logic and player interaction
RunGUI.py           → Launches the GUI
main.py             → Main entry point of the application
OtherStuff.py       → Helper functions
screenshots/        → Gameplay screenshots
```

---

## Example Gameplay

### Start of the Game

![Start Game](screenshots/start%20game.jpg)

### Mid Game

![Mid Game](screenshots/mid%20game.jpg)

### End of the Game

![End Game](screenshots/end%20game.jpg)

---

## How to Run

1. Install Python (3.x)

2. Clone the repository

```
git clone https://github.com/zaynab724/checkers-AI-agent.git
```

3. Navigate to the project folder

```
cd checkers-AI-agent
```

4. Run the program

```
python main.py
```

---

## Concepts Demonstrated

* Adversarial Search
* Minimax Algorithm
* Alpha-Beta Pruning
* Heuristic Evaluation Functions
* Game State Representation
* AI Decision Making

---

## Author

Zaynab Aboulkacem
Al Akhawayn University
