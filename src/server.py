"""
Battleship game server implementation
"""

import socket
import argparse
import sys
import logging
from typing import Optional
from contextlib import contextmanager

from protocol import (
    MessageType, create_message, parse_message, 
    validate_coordinate, ProtocolError, InvalidMessageError
)
from game_model import GameBoard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BattleshipServer:
    """
    Server for hosting Battleship games and communicating with client
    """
    
    def __init__(self, host: str = 'localhost', port: int = 5050):
        """Initialize server socket and bind to host/port"""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
        except Exception as e:
            logger.error(f"Failed to bind to {self.host}:{self.port}: {e}")
            sys.exit(1)

        self.socket.listen()
        logger.info(f'Server listening on {self.host}:{self.port}')

    @contextmanager
    def client_connection(self):
        """Context manager for handling client connections"""
        conn = None
        try:
            conn, addr = self.socket.accept()
            logger.info(f'New connection from {addr}')
            yield conn
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            if conn:
                conn.close()
                logger.info("Connection closed")

    def send_message(self, conn: socket.socket, msg_type: MessageType, data: Optional[dict] = None) -> None:
        """Send a protocol message to the client"""
        try:
            message = create_message(msg_type, data)
            conn.sendall(message.encode())
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def receive_message(self, conn: socket.socket) -> tuple[MessageType, dict]:
        """Receive and parse a protocol message from the client"""
        try:
            data = conn.recv(1024).decode()
            if not data:
                raise ConnectionError("Client disconnected")
            return parse_message(data)
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            raise

    def handle_client(self, conn: socket.socket) -> None:
        """Handle a single client connection"""
        game = GameBoard()
        game.position_ships()

        try:
            # Expect initial START_GAME message
            msg_type, data = self.receive_message(conn)
            if msg_type != MessageType.START_GAME:
                raise InvalidMessageError(f"Expected START_GAME, got {msg_type}")

            # Acknowledge and start game
            self.send_message(conn, MessageType.POSITIONING_SHIPS)
            self.send_message(conn, MessageType.SHIPS_IN_POSITION)

            # Main game loop
            while not game.is_game_over():
                msg_type, data = self.receive_message(conn)
                if msg_type != MessageType.SHOT:
                    raise InvalidMessageError(f"Expected SHOT, got {msg_type}")

                coord = data.get('coordinate', '')
                if not validate_coordinate(coord):
                    self.send_message(conn, MessageType.ERROR, 
                                    {'message': 'Invalid coordinate format'})
                    continue

                is_hit, is_game_over = game.process_shot(coord)
                response_type = MessageType.HIT if is_hit else MessageType.MISS
                self.send_message(conn, response_type)

            # Game over - send final score
            self.send_message(conn, MessageType.GAME_OVER, 
                            {'score': game.get_score()})
            logger.info(f"Game completed with score: {game.get_score()}")

        except ProtocolError as e:
            logger.error(f"Protocol error: {e}")
            self.send_message(conn, MessageType.ERROR, {'message': str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.send_message(conn, MessageType.ERROR, 
                            {'message': 'Internal server error'})

    def run(self) -> None:
        """Run the server indefinitely"""
        while True:
            with self.client_connection() as conn:
                self.handle_client(conn)

def main():
    """Parse arguments and start the Battleship server"""
    parser = argparse.ArgumentParser(description='Battleship game server')
    parser.add_argument('--host', default='localhost', help='Server hostname')
    parser.add_argument('--port', type=int, default=5050, help='Server port')
    args = parser.parse_args()

    server = BattleshipServer(host=args.host, port=args.port)
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info('\nServer shutting down...')
        server.socket.close()

if __name__ == '__main__':
    main()