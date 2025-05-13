import socket
import numpy as np
import argparse
import re
import sys


class Battleship:
    """
    Class representing Battleship game board and game logic
    """

    GRID_SIZE = 9
    ALPHABET = [chr(i) for i in range(65, 65 + GRID_SIZE)] # ['A', 'B', ...,'I']
    COORD_PATTERN = re.compile(r'^[A-I][1-9]\n\Z')  # Valid coordinates: e.g., 'A1\n', 'E8\n'

    def __init__(self):
        self.board = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        self.shot_count = 0  # Number of valid shots fired
        self.hit_count = 0   # Number of successful hits
        self.ships = {
            'C': 5, # Canberra-class Landing Helicopter Dock
            'H': 4, # Hobart-class Destroyer
            'L': 3, # Leeuwin-class Survey Vessel
            'A': 2  # Armidale-class Patrol Boat
        }
        assert self.GRID_SIZE >= max(self.ships.values()) # Grid too small for largest ship
        self.position_ships()

    def position_ships(self):
        """
        Randomnly position ships on board without overlapping
        """
        for size in self.ships.values():
            while True:
                x, y = np.random.randint(self.GRID_SIZE, size=2)
                direction = np.random.choice(['H', 'V']) # Horizontal or vertical
                if self.is_valid_placement(x, y, size, direction):
                    self.set_ship(x, y, size, direction)
                    break
        
    def is_valid_placement(self, x, y, size, direction):
        """
        Check if a ship can be placed at (x, y) in given direction without overlapping
        """
        if direction == 'H' and y + size <= self.GRID_SIZE:
            return np.all(self.board[x, y:y+size] == 0)
        elif direction == 'V' and x + size <= self.GRID_SIZE:
            return np.all(self.board[x:x+size, y] == 0)
        return False
    
    def set_ship(self, x, y, size, direction):
        """
        Place ship on board at (x, y) in given direction
        """
        if direction == 'H':
            self.board[x, y:y+size] = 1
        elif direction == 'V':
            self.board[x:x+size, y] = 1
        else:
            raise ValueError("Direction must be 'H' or 'V'")
        
    def game_over(self):
        """
        Return True if all ships have been sunk
        """
        return self.hit_count == sum(self.ships.values())


    def coord_to_indicies(self, coord):
        """
        Convert coordinate string (e.g., 'B7') into grid indices (x, y)
        """
        col = self.ALPHABET.index(coord[0])
        row = int(coord[1]) - 1
        return col, row
    

    def get_value_at(self, coord):
        """
        Return value at given coordinate
        """
        x, y = self.coord_to_indicies(coord)
        return self.board[x, y]
    
    def set_value_at(self, coord, value):
        """
        Set value at given coordinate
        """
        x, y = self.coord_to_indicies(coord)
        self.board[x, y] = value
    
    @classmethod
    def is_valid_coord(cls, coord):
        """
        Check if coordinate string matches expected protocol
        """
        return bool(cls.COORD_PATTERN.match(coord))
            
class BattleshipServer:
    """
    Server for hosting Battleship games and communicating with client
    """
    
    def __init__(self, host='localhost', port=5050):
        """Initialise server socket and bind to host/port"""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.bind((self.host, self.port))
        except Exception:
            print('Error using socket. Closing connection...')
            print('Address already in use')
            sys.exit(1)

        self.socket.listen()
        print(f'Server listening on {self.host}:{self.port}')


    def wait_for_client(self):
        """
        Wait for client to connect and return the connection
        """
        conn, _ = self.socket.accept()
        return conn
    
        
    def handle_client(self, conn):
        """
        Main loop for handling a single client connection. If the client at any point
        sends an unexpected message to the server, the server will drop the connection and wait
        for the next client to connect.
        """
        game = Battleship()

        # Expect initial 'START GAME' message
        data = conn.recv(30).decode()
        print(f'Client: {data.strip()}')
        if data != 'START GAME\n':
            print('Error communicating with client. Closing connection...')
            print(f'Invalid message from client. Expected START GAME but received: {data}')
            conn.close()
            return
        
        # Acknowledge and start game
        conn.send(b'POSITIONING SHIPS\n')
        print('Server: POSITIONING SHIPS')
        conn.send(b'SHIPS IN POSITION\n')
        print('Server: SHIPS IN POSITION')

        # Main game loop
        while not game.game_over():
            coord = conn.recv(20).decode()
            coord = coord if coord else 'null'
            print(f'Client: {coord.strip()}')

            if not game.is_valid_coord(coord):
                # Invalid coordinate, break and close the connection
                print('Error communicating with client. Closing connection...')
                print(f'Illegal Cell: {coord}')
                break

            if game.get_value_at(coord) == 1:
                # Coordinate occupied by ship (x, y) == 1
                print('Server: HIT')
                conn.send(b'HIT\n')
                game.set_value_at(coord, -1) # Mark cell as hit
                game.hit_count += 1
            else:
                # Space empty: (x, y) == -1 (already hit) or 0 (empty)
                print('Server: MISS')
                conn.send(b'MISS\n')

            # Track the number of shots
            game.shot_count += 1

        # Game over - send final shot count (i.e., score)
        if game.game_over():
            conn.send(f'{game.shot_count}'.encode())
            print(f'Server: {game.shot_count}')

        conn.close()
        

    def run(self):
        """
        Run the server indefinitely
        """
        while True:
            conn = self.wait_for_client()
            self.handle_client(conn)



def main():
    """
    Parse arguments and start the Battleship server
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=5050, help='Server port')
    args = parser.parse_args()

    server = BattleshipServer(port=args.port)
    try:
        # Run the server until a keyboard interrupt occurs, then gracefully exit
        server.run()
    except KeyboardInterrupt:
        print('\nServer sutting down...')
        server.socket.close()


if __name__ == '__main__':
    main()