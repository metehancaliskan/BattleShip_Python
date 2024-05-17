import socket
import threading
import time

# Constants
BOARD_SIZE = 5
SHIP_SIZES = [4, 3, 2]  # Example ship sizes (mothership, destroyer, submarine)
TIME_LIMIT = 60

# Global Variables
clients = []
boards = {}
turns = {}
lock = threading.Lock()

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

# Function to handle each client in a separate thread
def handle_client(client_socket, client_id):
    global clients, boards, turns
    client_socket.send(f"{client_id}\n".encode())
    client_socket.send(f"Welcome Player {client_id}. Please place your ships.\n".encode())

    # Initialize player's board
    board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    boards[client_id] = board

    start_time = time.time()
    while time.time() - start_time < TIME_LIMIT:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break
        if data == f"{client_id} SHIPS_PLACED":
            break
        # Expecting data in the format: "ship row col direction"
        try:
            ship, row, col, direction = data.split()
            ship = int(ship)
            row = ord(row.upper()) - ord('A')
            col = int(col) - 1
            if is_valid_ship_placement(board, ship, row, col, direction):
                client_socket.send("Ship placed successfully.\n".encode())
            else:
                client_socket.send("Invalid ship placement.\n".encode())
        except ValueError:
            client_socket.send("Invalid input. Please enter ship, row, col, and direction.\n".encode())

    if time.time() - start_time >= TIME_LIMIT:
        client_socket.send("Time's up! You are disqualified.\n".encode())
        client_socket.close()
        with lock:
            clients.remove(client_socket)
        return

    client_socket.send("All ships placed. Waiting for the other player...\n".encode())

    # Wait until both clients are ready
    while len(clients) < 2:
        time.sleep(1)

    with lock:
        if len(turns) == 0:
            turns[client_id] = True
            other_client_id = 1 - client_id
            turns[other_client_id] = False
        else:
            other_client_id = 1 - client_id

    # Notify clients the game is starting
    print("The game has started.")
    client_socket.send("The game is starting!\n".encode())
    if turns[client_id]:
        client_socket.send("Your turn!\n".encode())
    else:
        clients[other_client_id].send("Your turn!\n".encode())

    def send_game_state(client_id, other_client_id):
        client_socket = clients[client_id]
        client_socket.send(f"Turn information: {'Your turn!' if turns[client_id] else 'Player {other_client_id}’s turn!'}\n".encode())
        client_socket.send("State of opposing board:\n".encode())
        client_socket.send("  1 2 3 4 5\n".encode())
        for i, row in enumerate(boards[other_client_id]):
            client_socket.send(f"{chr(i + ord('A'))} {' '.join(['.' if cell not in ['X', 'O'] else cell for cell in row])}\n".encode())
        client_socket.send("State of your board:\n".encode())
        client_socket.send("  1 2 3 4 5\n".encode())
        for i, row in enumerate(boards[client_id]):
            client_socket.send(f"{chr(i + ord('A'))} {' '.join(row)}\n".encode())

    def check_win_condition(board):
        return sum(row.count('X') for row in board) == 9

  # Game loop
    while True:
        if turns[client_id]:
            print(f"Waiting for Player {client_id}'s move")
            send_game_state(client_id, other_client_id)

            while True:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                if data.startswith(f"{client_id} MOVE"):
                    try:
                        _, _, row_col = data.split()
                        row = ord(row_col[0].upper()) - ord('A')
                        col = int(row_col[1]) - 1
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                            hit = boards[other_client_id][row][col] not in ['.', 'X', 'O']
                            boards[other_client_id][row][col] = 'X' if hit else 'O'
                            client_socket.send(f"{'It’s a hit!!!' if hit else 'You missed.'}\n".encode())
                            other_client_socket = clients[other_client_id]
                            if hit:
                                other_client_socket.send(f"Torpedo hits your ship at {chr(row + ord('A'))} {col + 1}.\n".encode())
                            print(f"Player {client_id} made its move")
                            if check_win_condition(boards[other_client_id]):
                                client_socket.send("You win!\n".encode())
                                other_client_socket.send("You lose!\n".encode())
                                print(f"Winner player: {client_id}")
                                client_socket.close()
                                other_client_socket.close()
                                return
                            turns[client_id] = False
                            turns[other_client_id] = True
                            other_client_socket.send("Your turn!\n".encode())
                            break
                        else:
                            client_socket.send("This is an illegal move. Please change your move!\n".encode())
                    except ValueError:
                        client_socket.send("Invalid move input. Please enter the location in the format A1.\n".encode())
                elif data.startswith(f"{client_id} REQUEST"):
                    send_game_state(client_id, other_client_id)

        else:
            send_game_state(client_id, other_client_id)
            while not turns[client_id]:
                time.sleep(1)

# Main function
def main(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(2)
    print(f"Server started on port {port}. Waiting for players...")

    while len(clients) < 2:
        client_socket, addr = server_socket.accept()
        with lock:
            client_id = len(clients)
            clients.append(client_socket)
        print(f"A client is connected, and it is assigned with the ID={client_id}.")
        threading.Thread(target=handle_client, args=(client_socket, client_id)).start()

    print("Waiting 60 seconds for ship positioning.")
    time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 BattleshipServer.py <port_number>")
        sys.exit(1)
    port = int(sys.argv[1])
    main(port)
