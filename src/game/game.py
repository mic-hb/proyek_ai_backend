""" This module contains the Game class representing the game. """

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List
import json

from src.game.board import Board
from src.game.player import Player
from src.game.piece import Piece
from src.game.cell import Cell
from src.game.constants import PieceTypes, CellTypes

@dataclass_json
@dataclass(order=True)
class Game:
    """A class to represent the game board."""
    board: Board
    players: list[Player] = field(default_factory=list)
    turn: PieceTypes = field(default=PieceTypes.MACAN)

    def __init__(self):
        # Initialize board and players
        self.board = self._initial_board(5, 9)
        self.turn = PieceTypes.MACAN
        self.players = []

        # Initialize board setup
        self._setup_board()

    def _initial_board(self, rows: int, columns: int) -> List[List[Cell]]:
        return [
            [Cell(piece=Piece(type=PieceTypes.BLANK),
                  valid_moves=[],  type=CellTypes.ALL_DIRECTIONS)
             for _ in range(columns)] for _ in range(rows)
        ]

    def _setup_board(self):
        # Mark cells with only 4 directions
        for i in [0, 2, 4]:
            for j in [3, 5]:
                self.board[i][j].type = CellTypes.FOUR_DIRECTIONS

        for i in [1, 3]:
            for j in [2, 4, 6]:
                self.board[i][j].type = CellTypes.FOUR_DIRECTIONS

        # Setup invalid spaces and wings
        self._setup_invalid_spaces()
        self._setup_wings()
        self._setup_special_spaces()

    def _setup_invalid_spaces(self):
        for i in [0, 4]:
            for j in [0, 1, 7, 8]:
                self.board[i][j] = Cell(
                    Piece(type=PieceTypes.INVALID),
                    valid_moves=[],
                    type=CellTypes.INVALID
                )

    def _setup_wings(self):
        for i in [1, 2, 3]:
            for j in [0, 1, 7, 8]:
                self.board[i][j] = Cell(
                    Piece(type=PieceTypes.BLANK),
                    valid_moves=[],
                    type=CellTypes.WINGS
                )

    def _setup_special_spaces(self):
        # Special space to move to left wing
        self.board[2][2].type = CellTypes.SPECIAL
        # Special space to move to right wing
        self.board[2][6].type = CellTypes.SPECIAL

    def calculate_valid_moves(self):
        """
        Calculate and update the valid moves for each piece on the center board.

        This method iterates through the center board and determines the valid moves
        for each piece based on its type. There are two types of pieces:
        - Type 1: Can move in 8 directions (up, down, left, right, and diagonals).
        - Type 2: Can move in 4 directions (up, down, left, right).

        Additionally, special moves are assigned to specific positions on the board.

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
                if self.board[row][col].type == CellTypes.ALL_DIRECTIONS:
                    self.board[row][col].valid_moves = self.get_moves(
                        row, col, directions_8, self.board)
                elif self.board[row][col].type == CellTypes.FOUR_DIRECTIONS:
                    self.board[row][col].valid_moves = self.get_moves(
                        row, col, directions_4, self.board)

        # Special moves for wings
        self.board[2][0].valid_moves = [(2, 1, "left")]
        self.board[2][4].valid_moves = [(2, 1, "right")]

    def get_moves(self, row: int, col: int, directions: List[tuple[int, int]], board: List[List[Cell]]) -> List[tuple[int, int, str]]:
        """
        Calculate possible moves for a piece on the board.

        Args:
            row: The current row position of the piece.
            col: The current column position of the piece.
            directions: A list of direction vectors (dr, dc) to check for possible moves.
            board: The game board represented as a 2D list of Cells.

        Returns:
            A list of valid moves (row, col, direction) where the piece can move.
        """
        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and board[nr][nc].type != CellTypes.INVALID:
                moves.append((nr, nc, ""))
        return moves

    def make_move(self, player_sid: str, player_piece: dict, target_row: int, target_col: int):
        """
        Make a move on the game board.

        This method updates the game board based on the player's move.
        It handles moving a piece from one position to another.

        Args:
            player_name: The name of the player making the move
            player_piece: Dictionary containing the piece information
            target_row: The target row position for the move
            target_col: The target column position for the move
        """
        player: Player = self.get_player_by_sid(player_sid)

        # Check which piece to move
        moved_piece = None
        # print(f"Player {player.name}, pieces: {player.pieces}")
        for piece in player.pieces:
            if piece.id == player_piece['id']:
                moved_piece = piece

        if moved_piece is None:
            return

        self.move_piece(moved_piece, target_row, target_col)

        if self.turn == PieceTypes.MACAN:
            self.turn = PieceTypes.UWONG
        else:
            self.turn = PieceTypes.MACAN

    def to_json(self) -> str:
        """Convert the game state to a JSON string."""
        return json.dumps({
            'board': self.board,
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

    def get_player_by_sid(self, player_sid: str) -> Player:
        """Get a player by their sid."""
        for player in self.players:
            if player.sid == player_sid:
                return player
        return Player()

    def recalculate_board(self):
        """Recalculate the board state based on piece positions."""
        for row in self.board:
            for cell in row:
                cell.piece = Piece(type=PieceTypes.BLANK)

        for player in self.players:
            for piece in player.pieces:
                if piece.position.x == -1 and piece.position.y == -1:
                    continue
                self.board[piece.position.y][piece.position.x].piece = piece

    def move_piece(self, moved_piece: Piece, target_row: int, target_col: int):
        """Move a piece to a new position on the board."""
        self.board[moved_piece.position.y][moved_piece.position.x].piece = Piece(type=PieceTypes.BLANK)
        moved_piece.position.x = target_col
        moved_piece.position.y = target_row
        self.board[target_row][target_col].piece = moved_piece

    def validate_move(self, player_sid: str, player_piece: dict, target_row: int, target_col: int) -> tuple[bool, str]:
        """Validate a move on the board."""

        player: Player = self.get_player_by_sid(player_sid)
        # Check which piece to move
        moved_piece = None
        # print(f"Player {player.name}, pieces: {player.pieces}")
        for piece in player.pieces:
            if piece.id == player_piece['id']:
                moved_piece = piece


        if moved_piece is None:
            return False, "Piece not found!"

        if player.piece_type != self.turn:
            return False, "Not your turn!"

        print(f"Moving piece {moved_piece.id} from {moved_piece.position.x}, {moved_piece.position.y} to {target_col}, {target_row}")

        dx, dy = abs(target_col - moved_piece.position.x), abs(target_row - moved_piece.position.y)
        is_diagonal_move: bool = dx != 0 and dy != 0
        is_on_board: bool = (moved_piece.position.x != -1 or moved_piece.position.y != -1)
        current_cell_type: CellTypes = self.board[moved_piece.position.y][moved_piece.position.x].type
        target_cell_type: CellTypes = self.board[target_row][target_col].type

        if dx == 0 and dy == 0:
            return False, "Cannot move to the same position!"

        if (dx > 1 or dy > 1) and is_on_board:
            return False, "Cannot move more than 1 cell!"

        if is_diagonal_move and not (current_cell_type == CellTypes.ALL_DIRECTIONS or current_cell_type == CellTypes.SPECIAL) and is_on_board:
            return False, "Cannot move diagonally!"

        if target_row < 0 or target_row >= len(self.board) or target_col < 0 or target_col >= len(self.board[0]):
            return False, "Move is outside the board boundaries!"

        if target_cell_type == CellTypes.INVALID:
            return False, "Invalid move!"

        if self.board[target_row][target_col].piece.type != PieceTypes.BLANK:
            return False, "Target position is occupied by another piece!"

        is_current_cell_special: bool = self.board[moved_piece.position.y][moved_piece.position.x].type == CellTypes.SPECIAL
        is_piece_on_wings: bool = not is_on_board or (current_cell_type == CellTypes.WINGS)

        print(f"Target cell type: {target_cell_type}")
        print(f"Is target wings: {target_cell_type == CellTypes.WINGS}")
        print(f"Is current special: {is_current_cell_special}")

        if target_cell_type == CellTypes.WINGS and not is_current_cell_special and not is_piece_on_wings:
            return False, "Cannot move to wings!"

        if target_cell_type == CellTypes.WINGS and is_diagonal_move:
            return False, "Cannot move diagonally on wings!"


        if current_cell_type == CellTypes.WINGS:
            if not target_cell_type == CellTypes.SPECIAL and not target_cell_type == CellTypes.WINGS:
                return False, "Cannot move out of wings!"


        return True, ""
