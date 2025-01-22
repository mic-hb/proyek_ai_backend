""" This module contains the GameBoard class representing the game board. """

import json
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
from typing import Dict, List, TypeAlias, Union, Optional

from dataclasses_json import dataclass_json

from src.game.player import Player
from src.game.piece import Piece
from src.game.constants import PieceTypes, CellTypes


@dataclass_json
@dataclass
class Cell:
    """A dataclass representing a cell on the game board."""
    piece: Piece = field(default_factory=Piece)
    type: CellTypes = field(default=CellTypes.INVALID)
    valid_moves: list[tuple[int, int, str]] = field(default_factory=list)


# @dataclass_json
# @dataclass
# class Board:
#     """A dataclass representing a board on the game board."""
#     board: list[list[Cell]]
Board: TypeAlias = list[list[Cell]]


@dataclass_json
@dataclass(order=True)
class Game:
    """
    A class to represent the game board.

    Attributes
    ----------
    center_board : list
        A 5x5 grid representing the center of the board. Each cell is a dictionary with keys:
        - "piece": int, representing the piece on the cell (0 if empty).
        - "valid_moves": list, representing the valid moves from this cell.
        - "type": int, representing the type of the cell (1 for normal, 3 for special).

    left_wing : list
        A 5x2 grid representing the left wing of the board. Each cell is a dictionary with keys:
        - "piece": int, representing the piece on the cell (0 if empty).
        - "valid_moves": list, representing the valid moves from this cell.
        - "type": int, representing the type of the cell (0 for invalid, 1 for normal).

    right_wing : list
        A 5x2 grid representing the right wing of the board. Each cell is a dictionary with keys:
        - "piece": int, representing the piece on the cell (0 if empty).
        - "valid_moves": list, representing the valid moves from this cell.
        - "type": int, representing the type of the cell (0 for invalid, 1 for normal).

    Methods
    -------
    __init__():
        Initializes the game board with center, left wing, and right wing grids. Marks invalid spaces and sets special spaces.
    """
    board: Board
    players: list[Player]
    turn: PieceTypes = field(default=PieceTypes.MACAN)

    def __init__(self):
        # Define the center board
        self.board = self._initial_board(5, 9)

        # Mark invalid spaces (X) on the left and right wings
        for i in [0, 4]:
            for j in [0, 1, 7, 8]:
                self.board[i][j] = Cell(Piece(type=PieceTypes.INVALID),  valid_moves=[],  type=CellTypes.INVALID)

        for i in [1, 3]:
            for j in [0, 1]:
                self.board[i][j] = Cell(Piece(type=PieceTypes.BLANK),  valid_moves=[],  type=CellTypes.WINGS)

        for i in [1, 3]:
            for j in [7, 8]:
                self.board[i][j] = Cell(Piece(type=PieceTypes.BLANK),  valid_moves=[],  type=CellTypes.WINGS)

        # Add valid_moves manually for type 3 spaces
        # Special space to move to left wing
        self.board[2][2].type = CellTypes.SPECIAL
        # Special space to move to right wing
        self.board[2][6].type = CellTypes.SPECIAL

        # Initialize players
        self.players = [Player(), Player()]
        self.turn = PieceTypes.MACAN

    def _initial_board(self, rows, columns) -> List[List[Cell]]:
        return [
            [Cell(piece=Piece(type=PieceTypes.BLANK),
                  valid_moves=[],  type=CellTypes.ALL_DIRECTIONS) for _ in range(columns)] for _ in range(rows)
        ]

    def calculate_valid_moves(self):
        """
        Calculate and update the valid moves for each piece on the center board.

        This method iterates through the center board and determines the valid moves
        for each piece based on its type. There are two types of pieces:
        - Type 1: Can move in 8 directions (up, down, left, right, and diagonals).
        - Type 2: Can move in 4 directions (up, down, left, right).

        Additionally, special moves are assigned to specific positions on the board.

        The valid moves are stored in the "valid_moves" key of each piece's dictionary.

        Directions:
        - directions_8: List of tuples representing 8 possible movement directions.
        - directions_4: List of tuples representing 4 possible movement directions.

        Special Moves:
        - The piece at position (2, 0) can move to (2, 1) with a "left" move.
        - The piece at position (2, 4) can move to (2, 1) with a "right" move.
        """
        # Directions for movement
        directions_8 = [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (1, 1), (-1, 1), (1, -1)]
        directions_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Center board valid moves
        for row in range(5):
            for col in range(5):
                if self.board[row][col].type == 1:
                    self.board[row][col].valid_moves = self.get_moves(
                        row, col, directions_8, self.board)
                elif self.board[row][col].type == 2:
                    self.board[row][col].valid_moves = self.get_moves(
                        row, col, directions_4, self.board)

        # Special moves for wings
        self.board[2][0].valid_moves = [(2, 1, "left")]
        self.board[2][4].valid_moves = [(2, 1, "right")]

    def get_moves(self, row, col, directions, board):
        """
        Calculate possible moves for a piece on the board.

        Args:
            row (int): The current row position of the piece.
            col (int): The current column position of the piece.
            directions (list of tuples): A list of direction vectors (dr, dc) to check for possible moves.
            board (list of list of dict): The game board represented as a 2D list of dictionaries,
                                        where each dictionary contains information about the cell.

        Returns:
            list of tuples: A list of valid moves (nr, nc) where the piece can move.
        """
        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and board[nr][nc]["type"] != 0:
                moves.append((nr, nc))
        return moves

    def make_move(self, player_name: str, player_piece: dict, target_row: int, target_col: int):
        """
        Make a move on the game board.

        This method updates the game board based on the player's move.
        It handles moving a piece from one position to another.

        Args:
            player (str): The player making the move ('player1' or 'player2').
            board_type (str): The type of board the move is being made on ('center', 'left', or 'right').
            target_row (int): The target row position for the move.
            target_col (int): The target column position for the move.
        """

        player: Player = self.get_player_by_name(player_name)

        # Check which piece to move
        moved_piece = None
        print(f"Player {player.name}, pieces: {player.pieces}")
        for piece in player.pieces:
            if piece.id == player_piece['id']:
                moved_piece = piece

        if moved_piece is None:
            return

        self.move_piece(moved_piece, target_row, target_col)
        # self.recalculate_board()

        if self.turn == PieceTypes.MACAN:
            self.turn = PieceTypes.UWONG
        else:
            self.turn = PieceTypes.MACAN

        # if board_type == "center_board":
        #     print(f"Player {player_name} moved to center board: ({
        #           target_row}, {target_col})")
        #     self.center_board[target_row][target_col].piece_type = player_piece['type']
        # elif board_type == "left_wing":
        #     print(f"Player {player_name} moved to left wing: ({
        #           target_row}, {target_col})")
        #     self.left_wing[target_row][target_col].piece_type = player_piece['type']
        # elif board_type == "right_wing":
        #     print(f"Player {player_name} moved to right wing: ({
        #           target_row}, {target_col})")
        #     self.right_wing[target_row][target_col].piece_type = player_piece['type']

    def to_json(self) -> str:
        """Convert the game state to a JSON string."""
        # Implement the logic to convert the game state to JSON

        return json.dumps({
            'center_board': self.board,
        })

    def format_board(self) -> str:
        """Format the game board for display."""
        center_board: list[list[PieceTypes]] = [[cell.piece.type for cell in row[2:7]]
                                                for row in self.board]
        left_wing: list[list[PieceTypes]] = [[cell.piece.type for cell in row[0:2]]
                                             for row in self.board]
        right_wing: list[list[PieceTypes]] = [[cell.piece.type for cell in row[7:9]]
                                              for row in self.board]

        formatted_board = ""
        for y in [0, 1, 2, 3, 4]:
            for x in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                if x < 1:
                    formatted_board += f"{left_wing[y][x]}, "
                elif x < 2:
                    formatted_board += f"{left_wing[y][x]} | "
                elif x < 6:
                    formatted_board += f"{center_board[y][x-2]}, "
                elif x < 7:
                    formatted_board += f"{center_board[y][x-2]} | "
                else:
                    formatted_board += f"{right_wing[y][x-7]}, "
            formatted_board += "\n"

        return formatted_board

    def reset(self):
        """Reset the game board to its initial state."""
        self.__init__()

    def get_player_by_name(self, player_name) -> Player:
        for player in self.players:
            if player.name == player_name:
                return player

        return Player()

    def recalculate_board(self):
        for row in self.board:
            for cell in row:
                cell.piece = Piece(type=PieceTypes.BLANK)

        for player in self.players:
            for piece in player.pieces:
                if piece.position.x == -1 and piece.position.y == -1:
                    continue
                self.board[piece.position.y][piece.position.x].piece = piece

    def move_piece(self, moved_piece, target_row, target_col):
        self.board[moved_piece.position.y][moved_piece.position.x].piece = Piece(type=PieceTypes.BLANK)
        moved_piece.position.x = target_col
        moved_piece.position.y = target_row
        self.board[target_row][target_col].piece = moved_piece
