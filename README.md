# Battleship Game Project

This project implements a simple network-based Battleship game using Python's `socket` and `threading` libraries. It consists of two main scripts: `BattleshipServer.py` for the server-side logic and `BattleshipClient.py` for the client-side interface. The game supports two players competing against each other over a network.

## Features

- Multi-threaded server that handles multiple client connections simultaneously.
- Time-limited ship placement phase.
- Gameplay that includes placing ships, making moves, and automatic turn management.
- Basic win condition checking (total hits on enemy ships).
- Simple text-based interface for interacting with the game.

## Requirements

- Python 3.x
- Network access between the server and client machines (or localhost for testing)

## Setup and Running the Game

### Server

1. Navigate to the directory containing `BattleshipServer.py`.
2. Run the server script by specifying the port number to listen on:

Example: python3 BattleshipServer.py 6000


### Client

1. Navigate to the directory containing `BattleshipClient.py`.
2. Run the client script by specifying the port number the server is listening on:

Example: python3 BattleshipClient.py 6000


## Game Play Instructions

### Ship Placement

- Players are prompted to place their ships at the beginning of the game.
- Input the starting row (A-E), starting column (1-5), and direction (H for horizontal, V for vertical) for each ship.
- Ships must fit entirely on the board without overlapping other ships.

### Making Moves

- Players take turns to attack the opponent's board.
- On your turn, enter the command `MOVE`, then specify the target cell (e.g., A1).
- The game updates both players about the result of the move (hit or miss) and current game state.

### Win Condition

- The game ends when one player successfully hits all segments of the opponent's ships.
- The server will notify both clients about the outcome (win or lose).

## Known Issues

- The game does not handle client disconnections gracefully during gameplay.
- There is limited error handling for invalid inputs during the game setup phase.



