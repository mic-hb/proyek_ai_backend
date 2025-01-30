""" This module contains the Game class representing the game. """

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List
import json

from src.game.board import Board
from src.game.player import Player
from src.game.piece import Piece, PositionVector
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
            [Cell(piece=Piece(type=PieceTypes.BLANK, position=PositionVector(x=col, y=row)),
                  valid_moves=[],  type=CellTypes.ALL_DIRECTIONS)
             for col in range(columns)] for row in range(rows)
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
                    piece=Piece(type=PieceTypes.INVALID, position=PositionVector(x=j, y=i)),
                    valid_moves=[],
                    type=CellTypes.INVALID
                )

    def _setup_wings(self):
        for i in [1, 2, 3]:
            for j in [0, 1, 7, 8]:
                self.board[i][j] = Cell(
                    piece=Piece(type=PieceTypes.BLANK, position=PositionVector(x=j, y=i)),
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
        Calculate and update the valid moves for each piece on the board.
        This method checks all pieces owned by both players and updates their valid_moves.
        """
        # Clear all valid moves first
        for row in self.board:
            for cell in row:
                cell.valid_moves = []

        # Calculate valid moves for each player's pieces
        for player in self.players:
            for piece in player.pieces:
                # Skip pieces that are captured (-2, -2) or not placed yet (-1, -1)
                if piece.position.x < 0 or piece.position.y < 0:
                    continue

                valid_moves: list[PositionVector] = []
                current_row, current_col = piece.position.y, piece.position.x

                # Check all possible target positions on the board
                for target_row in range(len(self.board)):
                    for target_col in range(len(self.board[0])):
                        # Create a temporary piece dict for validate_move
                        temp_piece_dict = {
                            'id': piece.id,
                            'type': piece.type,
                            'position': {'x': piece.position.x, 'y': piece.position.y}
                        }

                        # Save current turn state
                        original_turn = self.turn
                        # Temporarily set turn to piece's type for validation
                        self.turn = piece.type

                        # Check if move is valid
                        is_valid, _ = self.validate_move(player.sid, temp_piece_dict, target_row, target_col)

                        # For MACAN pieces, also check capture moves
                        if piece.type == PieceTypes.MACAN:
                            is_capture_valid = self.validate_macan_capture(piece, target_row, target_col)
                            is_valid = is_valid or is_capture_valid

                        # Restore original turn
                        self.turn = original_turn

                        if is_valid:
                            # Add to both piece's valid moves and cell's valid moves
                            move_direction = ""
                            # Determine wing direction if moving to wings
                            if self.board[target_row][target_col].type == CellTypes.WINGS:
                                if target_col <= 1:
                                    move_direction = "left"
                                else:
                                    move_direction = "right"

                            valid_moves.append(PositionVector(x=target_col, y=target_row))

                piece.valid_moves = valid_moves

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

        self.calculate_valid_moves()

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
                cell.piece = Piece(type=PieceTypes.BLANK, position=PositionVector(x=cell.piece.position.x, y=cell.piece.position.y))

        for player in self.players:
            for piece in player.pieces:
                if piece.position.x == -1 and piece.position.y == -1:
                    continue
                self.board[piece.position.y][piece.position.x].piece = piece

    def move_piece(self, moved_piece: Piece, target_row: int, target_col: int):
        """
        Move a piece to a new position on the board.
        If it's a MACAN piece making a capture move, remove captured UWONG pieces.
        """
        current_row, current_col = moved_piece.position.y, moved_piece.position.x

        # Check if this is a MACAN capture move
        if moved_piece.type == PieceTypes.MACAN and self.validate_macan_capture(moved_piece, target_row, target_col):
            # Calculate direction vector
            dr = target_row - current_row
            dc = target_col - current_col

            # Get unit direction vector
            if dr != 0:
                dr = dr // abs(dr)
            if dc != 0:
                dc = dc // abs(dc)

            # Remove captured UWONG pieces
            row, col = current_row + dr, current_col + dc
            while row != target_row or col != target_col:
                # Find the player who owns this UWONG piece
                captured_piece = self.board[row][col].piece
                for player in self.players:
                    for piece in player.pieces:
                        if piece.id == captured_piece.id and piece.type == PieceTypes.UWONG:
                            # Set captured piece position to (-2, -2)
                            piece.position.x = -2
                            piece.position.y = -2

                # Clear the cell
                self.board[row][col].piece = Piece(type=PieceTypes.BLANK, position=PositionVector(x=col, y=row))

                # Move to next cell
                row += dr
                col += dc

        # Move the piece to its new position
        self.board[current_row][current_col].piece = Piece(type=PieceTypes.BLANK, position=PositionVector(x=current_col, y=current_row))
        moved_piece.position.x = target_col
        moved_piece.position.y = target_row
        self.board[target_row][target_col].piece = moved_piece

    def validate_move(self, player_sid: str, player_piece: dict, target_row: int, target_col: int) -> tuple[bool, str]:
        """Validate a move on the board."""

        player: Player = self.get_player_by_sid(player_sid)
        # Check which piece to move
        moved_piece = None
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

        macan_is_capturing: bool = self.validate_macan_capture(moved_piece, target_row, target_col)

        if dx == 0 and dy == 0:
            return False, "Cannot move to the same position!"

        if (dx > 1 or dy > 1) and is_on_board and not macan_is_capturing:
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

        if target_cell_type == CellTypes.WINGS and not is_current_cell_special and not is_piece_on_wings and not macan_is_capturing:
            return False, "Cannot move to wings!"

        if target_cell_type == CellTypes.WINGS and is_diagonal_move and not macan_is_capturing:
            return False, "Cannot move diagonally on wings!"


        if current_cell_type == CellTypes.WINGS and not macan_is_capturing:
            if not target_cell_type == CellTypes.SPECIAL and not target_cell_type == CellTypes.WINGS:
                return False, "Cannot move out of wings!"

        return True, ""

    def validate_macan_capture(self, moved_piece: Piece, target_row: int, target_col: int) -> bool:
        """
        Validate a macan capture move on the board.

        A MACAN piece can capture UWONG pieces when:
        1. The UWONG pieces are aligned in a straight line
        2. There must be even number of UWONG pieces (2, 4, etc.)
        3. The first UWONG piece must be adjacent to MACAN
        4. Movement direction must respect the cell type (ALL_DIRECTIONS or FOUR_DIRECTIONS)

        Returns:
            bool: True if the capture move is valid, False otherwise
        """
        if moved_piece.type != PieceTypes.MACAN:
            return False

        # Get current position and cell type
        current_row, current_col = moved_piece.position.y, moved_piece.position.x
        current_cell_type = self.board[current_row][current_col].type

        # Calculate direction vector
        dr = target_row - current_row
        dc = target_col - current_col

        # Validate diagonal movement based on cell type
        is_diagonal = abs(dr) == abs(dc) and dr != 0
        if is_diagonal and current_cell_type == CellTypes.FOUR_DIRECTIONS:
            return False

        # Get unit direction vector
        if dr != 0:
            dr = dr // abs(dr)
        if dc != 0:
            dc = dc // abs(dc)

        # Count UWONG pieces in the path
        uwong_count = 0
        row, col = current_row + dr, current_col + dc

        # Check if first piece is adjacent and is UWONG
        if not (0 <= row < len(self.board) and 0 <= col < len(self.board[0])):
            return False
        if self.board[row][col].piece.type != PieceTypes.UWONG:
            return False

        # Count consecutive UWONG pieces
        while row != target_row or col != target_col:
            if not (0 <= row < len(self.board) and 0 <= col < len(self.board[0])):
                return False

            current_piece = self.board[row][col].piece.type
            if current_piece != PieceTypes.UWONG:
                return False

            uwong_count += 1
            row += dr
            col += dc

        # Validate target position
        if not (0 <= target_row < len(self.board) and 0 <= target_col < len(self.board[0])):
            return False

        # Check if target cell is occupied
        if self.board[target_row][target_col].piece.type != PieceTypes.BLANK:
            return False

        # Validate number of UWONG pieces (must be even)
        if uwong_count == 0 or uwong_count % 2 != 0:
            return False

        # Allow capture into wings even if starting point is not SPECIAL
        target_cell_type = self.board[target_row][target_col].type
        if target_cell_type == CellTypes.WINGS:
            return True

        return True
