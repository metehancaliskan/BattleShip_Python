import socket
import threading
import sys

# Constants
BOARD_SIZE = 5
SHIP_SIZES = [4, 3, 2]  # Example ship sizes (mothership, destroyer, submarine)
TIME_LIMIT = 60

# Global Variables
client_id = None
board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
client_socket = None

def print_board(board):
    print("  1 2 3 4 5")
    for i, row in enumerate(board):
        print(f"{chr(i + ord('A'))} {' '.join(row)}")
    print()

# Function to place ships on the board
def place_ships():
    global board
    for ship in range(len(SHIP_SIZES)):
        while True:
            print(f"Place ship of size {SHIP_SIZES[ship]}")
            row = input("Enter starting row (A-E): ").upper()
            col = input("Enter starting column (1-5): ")
            direction = input("Enter direction (H for horizontal, V for vertical): ").upper()
            if not row or not col or direction not in ['H', 'V']:
                print("Invalid input. Please enter row, column, and direction.")
                continue
            row_index = ord(row) - ord('A')
            col_index = int(col) - 1
            if is_valid_ship_placement(board, ship, row_index, col_index, direction):
                print("Ship placed successfully.\n")
                print_board(board)
                client_socket.send(f"{ship} {row} {col} {direction}".encode())
                break
            else:
                print("Invalid ship placement. Try again.")

# Function to check if the ship placement is valid
def is_valid_ship_placement(board, ship, start_row, start_col, direction):
    length = SHIP_SIZES[ship]
    if direction == 'H':
        if start_col + length > BOARD_SIZE:
            return False
        for col in range(start_col, start_col + length):
            if board[start_row][col] != '.':
                return False
        for col in range(start_col, start_col + length):
            board[start_row][col] = str(ship)
    elif direction == 'V':
        if start_row + length > BOARD_SIZE:
            return False
        for row in range(start_row, start_row + length):
            if board[row][start_col] != '.':
                return False
        for row in range(start_row, start_row + length):
            board[row][start_col] = str(ship)
    else:
        return False
    return True

# Function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        print(data)
        if "You win" in data or "You lose" in data:
            client_socket.close()
            sys.exit()

# Main function
def main(port):
    global client_id, board, client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', port))

    # Receive client ID
    client_id = int(client_socket.recv(1024).decode().strip())
    print(f"Your client ID is: {client_id}")

    # Start a thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Place ships
    place_ships()

    client_socket.send(f"{client_id} SHIPS_PLACED\n".encode())

    # Wait for the game to start
    print("Waiting for the game to start...")

    # Game loop
    while True:
        command = input("Enter your command: ").strip().upper()
        if command == "MOVE":
            while True:
                row_col = input("Enter location (e.g., A1): ").upper()
                client_socket.send(f"{client_id} MOVE {row_col}\n".encode())
                response = client_socket.recv(1024).decode()
                print(response)
                if "illegal move" not in response.lower():
                    break
        elif command == "REQUEST":
            client_socket.send(f"{client_id} REQUEST\n".encode())
        else:
            print("Invalid command. Use 'MOVE' to make a move or 'REQUEST' to get board state and turn information.")

    client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 BattleshipClient.py <port_number>")
        sys.exit(1)
    port = int(sys.argv[1])
    main(port)
