"""
Battleship game client implementation
"""

import socket
import argparse
import sys
import logging
from typing import Optional, List
import random

from protocol import (
    MessageType, create_message, parse_message, 
    validate_coordinate, ProtocolError, InvalidMessageError
)
from game_model import GameBoard, CellState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BattleshipClient:
    """
    Client for connecting and playing the Battleship game
    """
    def __init__(self, host: str = 'localhost', port: int = 5050, auto: bool = False):
        self.host = host
        self.port = port
        self.auto = auto
        self.game = GameBoard()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # For auto mode
        self.shots: List[str] = []
        self.shot_index: int = 0
        if auto:
            self._generate_shots()

    def _generate_shots(self) -> None:
        """Generate all possible coordinates in random order for auto mode"""
        self.shots = [f'{c}{n}' for c in GameBoard.ALPHABET 
                     for n in range(1, GameBoard.GRID_SIZE + 1)]
        random.shuffle(self.shots)

    def connect(self) -> None:
        """Connect to the server"""
        try:
            self.socket.connect((self.host, self.port))
            logger.info(f'Connected to {self.host}:{self.port}')
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            sys.exit(1)

    def send_message(self, msg_type: MessageType, data: Optional[dict] = None) -> None:
        """Send a protocol message to the server"""
        try:
            message = create_message(msg_type, data)
            self.socket.sendall(message.encode())
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def receive_message(self) -> tuple[MessageType, dict]:
        """Receive and parse a protocol message from the server"""
        try:
            data = self.socket.recv(1024).decode()
            if not data:
                raise ConnectionError("Server disconnected")
            return parse_message(data)
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            raise

    def get_next_shot(self) -> str:
        """Get the next coordinate to fire at"""
        if self.auto:
            coord = self.shots[self.shot_index]
            self.shot_index += 1
            logger.info(f'Auto-shoot: {coord}')
            return coord
        
        while True:
            try:
                coord = input('Enter coordinates to shoot (e.g., A1): ').upper()
                if validate_coordinate(coord):
                    return coord
                logger.warning("Invalid coordinate format. Please use format A1-I9")
            except KeyboardInterrupt:
                logger.info("\nGame terminated by user")
                self.socket.close()
                sys.exit(0)

    def display_board(self) -> None:
        """Display the current state of the game board"""
        print("\n  " + " ".join(GameBoard.ALPHABET))
        for i in range(GameBoard.GRID_SIZE):
            row = f"{i + 1} "
            for j in range(GameBoard.GRID_SIZE):
                state = self.game.get_state_at(f"{GameBoard.ALPHABET[j]}{i+1}")
                if state == CellState.HIT:
                    row += "X "
                elif state == CellState.MISS:
                    row += "O "
                else:
                    row += ". "
            print(row)
        print()

    def play(self) -> None:
        """Main gameplay loop"""
        try:
            self.connect()
            
            # Start game handshake
            self.send_message(MessageType.START_GAME)
            
            # Wait for server to position ships
            msg_type, _ = self.receive_message()
            if msg_type != MessageType.POSITIONING_SHIPS:
                raise InvalidMessageError(f"Expected POSITIONING_SHIPS, got {msg_type}")
            
            msg_type, _ = self.receive_message()
            if msg_type != MessageType.SHIPS_IN_POSITION:
                raise InvalidMessageError(f"Expected SHIPS_IN_POSITION, got {msg_type}")

            # Main game loop
            while True:
                self.display_board()
                coord = self.get_next_shot()
                
                # Send shot
                self.send_message(MessageType.SHOT, {'coordinate': coord})
                
                # Process response
                msg_type, data = self.receive_message()
                if msg_type == MessageType.ERROR:
                    logger.error(f"Server error: {data.get('message', 'Unknown error')}")
                    continue
                
                is_hit = msg_type == MessageType.HIT
                self.game.process_shot(coord)
                
                if msg_type == MessageType.GAME_OVER:
                    score = data.get('score', 0)
                    logger.info(f"Game over! Final score: {score}")
                    break

        except ProtocolError as e:
            logger.error(f"Protocol error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.socket.close()

def main():
    """Parse arguments and start the Battleship client"""
    parser = argparse.ArgumentParser(description='Battleship game client')
    parser.add_argument('--host', default='localhost', help='Server hostname')
    parser.add_argument('--port', type=int, default=5050, help='Server port')
    parser.add_argument('--auto', action='store_true', help='Enable auto mode')
    args = parser.parse_args()

    client = BattleshipClient(host=args.host, port=args.port, auto=args.auto)
    client.play()

if __name__ == '__main__':
    main()