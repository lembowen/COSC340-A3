"""
Shared game model and utilities for Battleship game
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class CellState(Enum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3

@dataclass
class Ship:
    name: str
    size: int
    position: Optional[Tuple[int, int]] = None
    direction: Optional[str] = None

class GameBoard:
    """
    Represents a Battleship game board with ships and shot tracking
    """
    GRID_SIZE = 9
    ALPHABET = [chr(i) for i in range(65, 65 + GRID_SIZE)]  # ['A', 'B', ...,'I']
    
    def __init__(self):
        self.board = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        self.shot_count = 0
        self.hit_count = 0
        self.ships: Dict[str, Ship] = {
            'C': Ship('Canberra-class', 5),
            'H': Ship('Hobart-class', 4),
            'L': Ship('Leeuwin-class', 3),
            'A': Ship('Armidale-class', 2)
        }
        assert self.GRID_SIZE >= max(ship.size for ship in self.ships.values())

    def position_ships(self) -> None:
        """Randomly position ships on board without overlapping"""
        for ship in self.ships.values():
            while True:
                x, y = np.random.randint(self.GRID_SIZE, size=2)
                direction = np.random.choice(['H', 'V'])
                if self._is_valid_placement(x, y, ship.size, direction):
                    self._place_ship(x, y, ship, direction)
                    break

    def _is_valid_placement(self, x: int, y: int, size: int, direction: str) -> bool:
        """Check if a ship can be placed at (x, y) in given direction without overlapping"""
        if direction == 'H' and y + size <= self.GRID_SIZE:
            return np.all(self.board[x, y:y+size] == CellState.EMPTY.value)
        elif direction == 'V' and x + size <= self.GRID_SIZE:
            return np.all(self.board[x:x+size, y] == CellState.EMPTY.value)
        return False

    def _place_ship(self, x: int, y: int, ship: Ship, direction: str) -> None:
        """Place ship on board at (x, y) in given direction"""
        ship.position = (x, y)
        ship.direction = direction
        if direction == 'H':
            self.board[x, y:y+ship.size] = CellState.SHIP.value
        else:  # Vertical
            self.board[x:x+ship.size, y] = CellState.SHIP.value

    def process_shot(self, coord: str) -> Tuple[bool, bool]:
        """
        Process a shot at the given coordinate
        Returns: (is_hit, is_game_over)
        """
        x, y = self._coord_to_indices(coord)
        current_state = self.board[x, y]
        
        if current_state == CellState.SHIP.value:
            self.board[x, y] = CellState.HIT.value
            self.hit_count += 1
            self.shot_count += 1
            return True, self.is_game_over()
        elif current_state == CellState.EMPTY.value:
            self.board[x, y] = CellState.MISS.value
            self.shot_count += 1
            return False, False
        else:  # Already hit or missed
            return False, False

    def is_game_over(self) -> bool:
        """Return True if all ships have been sunk"""
        return self.hit_count == sum(ship.size for ship in self.ships.values())

    def _coord_to_indices(self, coord: str) -> Tuple[int, int]:
        """Convert coordinate string (e.g., 'B7') into grid indices (x, y)"""
        col = self.ALPHABET.index(coord[0].upper())
        row = int(coord[1]) - 1
        return col, row

    def get_state_at(self, coord: str) -> CellState:
        """Get the state of a cell at the given coordinate"""
        x, y = self._coord_to_indices(coord)
        return CellState(self.board[x, y])

    def get_score(self) -> int:
        """Get the current score (number of shots taken)"""
        return self.shot_count 