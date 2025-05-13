import socket
import argparse
import numpy as np
import re
import random
import sys

class Battleship:
    """
    Class representing Battleship game board for client
    """

    GRID_SIZE = 9
    ALPHABET = [chr(i) for i in range(65, 65 + GRID_SIZE)] # ['A', 'B', ...,'I']
    COORD_PATTERN = re.compile(r'^[A-I][1-9]$') # Valid coordinates: e.g., 'A1\n', 'E8\n'

    def __init__(self):
        # Board initialisation: '.' indicates un unshot cell
        self.board = np.full((self.GRID_SIZE, self.GRID_SIZE), '.', dtype=str)
        self.shot_count = 0   # Number of valid shots fired
        self.hit_count = 0    # Number of succesful shots

    def __str__(self):
        return self.get_board()
    
    def get_board(self):
        """
        Returns a string representation of the current board state
        """
        rows = ['  ' + ' '.join(self.ALPHABET)] # Column headers A-I
        for i in range(self.GRID_SIZE):
            row = f"{i + 1} " + ' '.join(self.board[:, i]) # Each row with its number
            rows.append(row)
        return '\n'.join(rows) + '\n'
    

    def set_board(self, coord, value):
        """
        Marks a cell withy a given value ('X' for hit, 'O' for miss)
        """
        x, y = self.coord_to_indicies(coord)
        if self.board[x, y] == '.':
            self.board[x, y] = value
        else:
            print('Coordinate already shot')
        
        self.shot_count += 1

    def game_over(self):
        """
        Return True if all ship parts (14) have been hit
        """
        return self.hit_count >= 14
    
    @classmethod
    def coord_to_indicies(cls, coord):
        """
        Converts a coordinate string (e.g., 'C6') to board indicies
        """
        col = cls.ALPHABET.index(coord[0])
        row = int(coord[1]) - 1
        return col, row
    
    @classmethod
    def is_valid_coord(cls, coord):
        """
        Validates the coordinate format
        """
        return bool(cls.COORD_PATTERN.match(coord))
    
    def get_score(self):
        """
        Returns the number of shots taken
        """
        return self.shot_count

    @classmethod
    def generate_random_shots(cls):
        """
        Generates all possible coordinates in random order.

        NOTE: This method was created to enable quick testing of end game 
        state without the need to manually play the game to completion.
        As will all other references to 'auto mode', it is not strickly 
        necessary for this assignment, so it can be ignored.
        """
        all_coords = [f'{c}{n}' for c in cls.ALPHABET for n in range(1, cls.GRID_SIZE + 1)]
        random.shuffle(all_coords)
        return all_coords
    


class BattleshipClient:
    """
    Client class for connecting and playing the Battleship game
    """
    def __init__(self, host='localhost', port=5050, auto=False):
        self.host = host
        self.port = port
        self.game = Battleship()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # The following are used in auto mode only (FOR TESTING -- not part of the assignment specs)
        self.auto = auto # If true, the client automatically fires shots
        self.shots = Battleship.generate_random_shots()
        self.shot_index = 0

    def connect(self):
        """
        Attempts to onnect to the server at the given host and port
        """
        try:
            self.client.connect((self.host, self.port))
            print(f'Connected to {self.host}:{self.port}')
        except Exception as e:
            print(f'Connection failed: {e}')
            sys.exit(1)

    def start_game(self):
        """
        Starts the game handshake with the server
        """
        self.client.send(b'START GAME\n')

        # Expect 'POSITIONING SHIPS' message
        data = self.client.recv(20).decode()
        data = data if data else 'null'
        if data != 'POSITIONING SHIPS\n':
            print('Error using socket. Closing connection...')
            print(f'Invalid message from server. Expected POSITIONING SHIPS but received {data}')
            self.client.close()
            sys.exit(1)

        # Expect 'SHIPS IN POSITION' message
        data = self.client.recv(20).decode()
        data = data if data else 'null'
        if data != 'SHIPS IN POSITION\n':
            print('Error using socket. Closing connection...')
            print(f'Invalid message from server. Expected SHIPS IN POSITION but received {data}')
            self.client.close()
            sys.exit(1)


    def get_next_shot(self):
        """
        Gets the next coordinate to fire at.
        Either from user input or automaticaly if auto mode enabled (for TESTING ONLY)
        """

        if self.auto:
            # If auto enabled
            coord = self.shots[self.shot_index]
            self.shot_index += 1
            print(f'Auto-shoot: {coord}')
            return coord
        else:
            # Otherwise take input from the user
            try:
                return input('Enter coordinates to shoot: ').upper()
            except KeyboardInterrupt:
                self.client.close()
                print()
                sys.exit(1)
        
    def play_turn(self, coord):
        """
        Sends a shot to the server ad updates the board based on the response
        """
        self.client.send(f'{coord}\n'.encode())
        response = self.client.recv(20).decode()

        if response == 'MISS\n':
            self.game.set_board(coord, 'O')
        elif response == 'HIT\n':
            self.game.set_board(coord, 'X')
            self.game.hit_count += 1
        else:
            print(f'Error using socket. Closing connection...')
            self.client.close()
            sys.exit(1)


    def play(self):
        """
        Main gameplay loop: handles game progression
        """
        self.connect() # Connect to server
        self.start_game() # Game handshake with server

        while not self.game.game_over():
            print(self.game)
            coord = self.get_next_shot()

            if not Battleship.is_valid_coord(coord):
                print('Invalid Coordinates!\n')
                continue

            self.play_turn(coord)

        # After game over, validate final score
        print(self.game)
        final_score = int(self.client.recv(20).decode())
        assert final_score == self.game.get_score()
        print(f'You won! Final score: {final_score}\n')
        self.client.close()



def main():
    """
    Parses command line arguments and starts the Battleship client
    """
    parser = argparse.ArgumentParser(
        prog='Battleship Game',
        description='Destroy all the ships in the least number of shots.'
    )
    parser.add_argument('host', type=str, nargs='?', default='localhost', help='Server hostname')
    parser.add_argument('port', type=int, nargs='?', default=5050, help='Server port')

    # Enable automatic shooting for testing purposes (use --auto flag when running the script)
    parser.add_argument('--auto', action='store_true', help='Automatically enter shots (for testing)')
    args = parser.parse_args()

    client = BattleshipClient(host=args.host, port=args.port, auto=args.auto)
    client.play()


if __name__ == '__main__':
    main()