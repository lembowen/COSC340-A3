"""
Protocol definitions and utilities for Battleship game communication
"""

import json
from enum import Enum
from typing import Dict, Any, Optional

class MessageType(Enum):
    START_GAME = "START_GAME"
    POSITIONING_SHIPS = "POSITIONING_SHIPS"
    SHIPS_IN_POSITION = "SHIPS_IN_POSITION"
    SHOT = "SHOT"
    HIT = "HIT"
    MISS = "MISS"
    GAME_OVER = "GAME_OVER"
    ERROR = "ERROR"

class ProtocolError(Exception):
    """Base exception for protocol-related errors"""
    pass

class InvalidMessageError(ProtocolError):
    """Raised when a message doesn't match the expected format"""
    pass

def create_message(msg_type: MessageType, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a protocol message with the given type and optional data
    """
    message = {
        "type": msg_type.value,
        "data": data or {}
    }
    return json.dumps(message) + "\n"

def parse_message(message: str) -> tuple[MessageType, Dict[str, Any]]:
    """
    Parse a protocol message into its type and data
    """
    try:
        parsed = json.loads(message.strip())
        msg_type = MessageType(parsed["type"])
        data = parsed.get("data", {})
        return msg_type, data
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise InvalidMessageError(f"Invalid message format: {e}")

def validate_coordinate(coord: str) -> bool:
    """
    Validate a coordinate string (e.g., 'A1', 'B2', etc.)
    """
    if not coord or len(coord) != 2:
        return False
    
    col, row = coord[0].upper(), coord[1]
    return (col in "ABCDEFGHI" and 
            row in "123456789") 