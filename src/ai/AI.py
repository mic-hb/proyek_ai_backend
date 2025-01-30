import random
import math
from typing import List, Tuple, Optional
from src.game.piece import Piece
from src.game.player import Player
from src.game.game import Game
from src.game.board import Board
from src.game.cell import Cell
from src.game.constants import PieceTypes, CellTypes
from src.game.move_request import MoveRequest
from src.game.suggested_move import SuggestedMove
from src.ai.algorithm_1 import Algorithm1
from src.ai.algorithm_2 import Algorithm2

class AI:
    """ """
    player_name: str
    current_player_type: PieceTypes
    game_state: Game
    algorithm: int

    def __init__(self, game_state, player_name, current_player_type, algorithm):
        self.game_state = game_state
        self.player_name = player_name
        self.current_player_type = current_player_type
        self.algorithm = algorithm

    def generate_random_move(self) -> SuggestedMove:
        """ Generate a random move. """

        player: Player | None = None
        for p in self.game_state.players:
            if p.name == self.player_name:
                player = p
                break

        if player is None:
            raise ValueError(f"No player found with name {self.player_name}")

        random_piece_index: int = random.randint(0, len(player.pieces) - 1)

        piece: Piece = player.pieces[random_piece_index]

        random_x: int = random.randint(2, 6)
        random_y: int = random.randint(0, 4)

        print(f"Generated random move: {random_x}, {random_y}")

        return SuggestedMove(
            message="Random move",
            player_name=self.player_name,
            player_piece=piece,
            col=random_x,
            row=random_y,
        )

    def generate_ai_move(self) -> SuggestedMove:
        """ Generate a move using the minimax algorithm. """
        # 1. Cek semua arah dari state sekarang + tergantung macan/uwong

        # 2. Cek dari semua arah, mana yang possible move

        # 3. Cek dari semua possible move, mana yang paling optimal

        best_piece, best_move, best_score = self.minimax_alpha_beta(self.game_state.board, depth=3, is_maximizing=True, alpha=-math.inf, beta=math.inf)

        print("Best value for the maximizing player:", best_score)

        if best_piece is None or best_move is None:
            return self.generate_random_move()

        return SuggestedMove(
            message="Minimax move",
            player_name=self.player_name,
            player_piece=best_piece,
            row=best_move[0],
            col=best_move[1],
        )

    def minimax_alpha_beta(
        self, node: Board, depth: int, is_maximizing: bool, alpha: float, beta: float
    ) -> Tuple[Optional[Piece], Optional[Tuple[int, int]], float]:
        """
        Minimax algorithm with alpha-beta pruning.

        :param node: The current state of the game.
        :param depth: The depth of the search tree.
        :param is_maximizing: Whether it's the maximizing player's turn.
        :param alpha: The best value the maximizing player can guarantee.
        :param beta: The best value the minimizing player can guarantee.
        :return: The best piece, move, and evaluation score.
        """

        current_player = (
            self.current_player_type if is_maximizing else
            (PieceTypes.MACAN if self.current_player_type == PieceTypes.UWONG else PieceTypes.UWONG)
        )

        if depth == 0:
            return None, None, self.evaluate(node)

        best_piece = None
        best_move = None

        if is_maximizing:
            max_eval = -math.inf
            for child, piece, move in self.generate_children_with_moves(node, current_player):
                _, _, eval = self.minimax_alpha_beta(child, depth - 1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_piece = piece
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return best_piece, best_move, max_eval
        else:
            min_eval = math.inf
            for child, piece, move in self.generate_children_with_moves(node, current_player):
                _, _, eval = self.minimax_alpha_beta(child, depth - 1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_piece = piece
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return best_piece, best_move, min_eval

    def evaluate(self, node: Board) -> float:
        """
        Evaluate the score of a terminal node for the current player.
        Replace with game-specific evaluation logic.
        """
        if self.algorithm == 1:
            return Algorithm1.evaluate(node)
        elif self.algorithm == 2:
            return Algorithm2.evaluate(node)
        else:
            return Algorithm1.evaluate(node)

    # Utility functions for game logic
    def is_terminal(self, node: Board) -> bool:
        """
        Check if the node is a terminal state (e.g., win, loss, draw, or max depth).
        Replace with game-specific logic.
        """
        # Example placeholder
        # return node.get("is_terminal", False)
        return random.choice([True, False])

    # def evaluate(self, node: Board) -> float:
    #     """
    #     Evaluate the score of a terminal node for the current player.
    #     Replace with game-specific evaluation logic.
    #     """
    #     # Example placeholder
    #     return float(random.randint(0, 10))

    # def evaluate(self, board: Board, current_player: PieceTypes) -> float:
    #     """
    #     Evaluates the given board state and returns a numerical score.
    #     Positive values favor MACAN, negative values favor UWONG.

    #     :param board: The current game board state.
    #     :param current_player: The player making the evaluation (PieceTypes.MACAN or PieceTypes.UWONG).
    #     :return: A float representing the board's value.
    #     """
    #     # Constants for evaluation weights
    #     MACAN_WEIGHT = 10
    #     UWONG_WEIGHT = 3
    #     STRATEGIC_POSITION_WEIGHT = 3
    #     WINNING_SCORE = math.inf
    #     LOSING_SCORE = -math.inf

    #     # Count the number of Macan and Uwong pieces
    #     macan_count = 0
    #     uwong_count = 0
    #     macan_moves_available = 0

    #     for row in range(len(board)):
    #         for col in range(len(board[row])):
    #             cell: Cell = board[row][col]
    #             print(f"V - Cell at ({row}, {col}): {cell}")

    #             if cell.piece.type == PieceTypes.MACAN:
    #                 macan_count += 1
    #                 # Calculate available moves for Macan
    #                 macan_moves_available += len(self.get_valid_moves(board, row, col, PieceTypes.MACAN))

    #             elif cell.piece.type == PieceTypes.UWONG:
    #                 uwong_count += 1

    #     # Check for terminal states
    #     # 1. Macan wins if all Uwong are captured and in even jumps (handled in gameplay logic, but assume even jumps here)
    #     if uwong_count == 0:
    #         print(f"Evaluated score: {WINNING_SCORE if current_player == PieceTypes.MACAN else LOSING_SCORE}")
    #         return WINNING_SCORE if current_player == PieceTypes.MACAN else LOSING_SCORE

    #     # 2. Uwong wins if Macan cannot move (is trapped)
    #     if macan_moves_available == 0:
    #         print(f"Evaluated score: {WINNING_SCORE if current_player == PieceTypes.UWONG else LOSING_SCORE}")
    #         return WINNING_SCORE if current_player == PieceTypes.UWONG else LOSING_SCORE

    #     # Compute score based on number of pieces and positional value
    #     score = (
    #         (macan_count * MACAN_WEIGHT) -
    #         (uwong_count * UWONG_WEIGHT)
    #     )

    #     print(f"Evaluated score: {score}")
    #     # Adjust score based on the current player
    #     return score if current_player == PieceTypes.MACAN else -score


    ####################################################################################################

    def generate_children_with_moves(self, node: Board, current_player: PieceTypes):
        """
        Generate all possible child states from the current state along with the associated piece and move.

        :param node: The current game board state.
        :param current_player: The player whose turn it is (PieceTypes.MACAN or PieceTypes.UWONG).
        :return: A list of tuples containing child states, the piece, and the move.
        """
        children: List[Tuple[Board, Piece, Tuple[int, int]]] = []
        print(f"Generating children nodes")

        for row in range(len(node)):
            for col in range(len(node[row])):
                cell = node[row][col]
                print(f"G - Cell at ({row}, {col}): {cell}")

                # Skip invalid cells or cells not occupied by the current player's pieces
                if cell.type == CellTypes.INVALID or cell.piece.type != current_player:
                    continue

                # Get all valid moves for the current piece
                moves, uwong_positions = self.get_valid_moves(node, row, col, current_player)

                for move in moves:
                    new_board = self.copy_board(node)
                    self.apply_move(new_board, (row, col), move, uwong_positions)
                    children.append((new_board, node[row][col].piece, move))

        print(f"Generated {len(children)} children for player {"MACAN" if current_player == PieceTypes.MACAN else "UWONG"}")
        return children


    def get_valid_moves(self, board: Board, row: int, col: int, player: PieceTypes):
        """
        Determine all valid moves for a piece at the given position.

        :param board: The current game board state.
        :param row: The row of the piece.
        :param col: The column of the piece.
        :param player: The player (PieceTypes.MACAN or PieceTypes.UWONG).
        :return: A list of valid moves as (row, col) tuples.
        """
        directions = []
        uwong_positions: list[Tuple[int, int]] = []

        if board[row][col].type in {CellTypes.ALL_DIRECTIONS, CellTypes.SPECIAL}:
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        elif board[row][col].type == CellTypes.FOUR_DIRECTIONS:
            directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]

        valid_moves: list[Tuple[int, int]] = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            # Check board boundaries
            if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                target_cell = board[new_row][new_col]

                # Validate Uwong moves (no captures)
                if player == PieceTypes.UWONG and target_cell.piece.type == PieceTypes.BLANK:
                    valid_moves.append((new_row, new_col))

                # Validate Macan moves (captures possible)
                elif player == PieceTypes.MACAN:
                    if target_cell.piece.type == PieceTypes.BLANK:
                        valid_moves.append((new_row, new_col))
                    elif target_cell.piece.type == PieceTypes.UWONG:
                        # Check if the jump over Uwong is valid
                        jump_row, jump_col = new_row + dr, new_col + dc
                        uwong_count = 1

                        while(True):
                            if jump_row >= len(board) or jump_col >= len(board[0]) or jump_row < 0 or jump_col < 0:
                                break
                            if uwong_count % 2 == 0 and uwong_count != 0 and board[jump_row][jump_col].piece.type == PieceTypes.BLANK:
                                uwong_positions.append((jump_row - 1, jump_col - 1))
                                valid_moves.append((jump_row, jump_col))
                                break
                            if (
                                0 <= jump_row < len(board)
                                and 0 <= jump_col < len(board[0])
                                and board[jump_row][jump_col].piece.type == PieceTypes.UWONG
                            ):
                                uwong_positions.append((jump_row - 1, jump_col - 1))
                                uwong_count += 1
                                jump_row += dr
                                jump_col += dc
                            else:
                                break

        return valid_moves, uwong_positions


    def apply_move(self, board: Board, from_pos: Tuple[int, int], to_pos: Tuple[int, int], uwong_positions: list[Tuple[int, int]]):
        """
        Apply a move on the board.

        :param board: The current game board state.
        :param from_pos: The starting position of the move as (row, col).
        :param to_pos: The target position of the move as (row, col).
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = board[from_row][from_col].piece
        board[from_row][from_col].piece = Piece()  # Empty the original cell
        board[to_row][to_col].piece = piece  # Move the piece to the target cell

        # Handle Macan captures
        if piece.type == PieceTypes.MACAN and len(uwong_positions) > 0:
            for uwong_pos in uwong_positions:
                uwong_row, uwong_col = uwong_pos
                board[uwong_row][uwong_col].piece = Piece()

    def copy_board(self, board: Board) -> Board:
        """
        Create a deep copy of the board.

        :param board: The current game board state.
        :return: A deep copy of the board.
        """
        return [[Cell(piece=cell.piece, type=cell.type, valid_moves=list(cell.valid_moves)) for cell in row] for row in board]

def generate_suggested_move(move_request: MoveRequest) -> SuggestedMove:
    """
    Generate a suggested move for the given move request.

    Parameters
    ----------
    move_request : MoveRequest
        The move request for which to generate a suggested move.

    Returns
    -------
    Move
        The suggested move.
    """

    ai = AI(game_state=move_request.game_state, player_name=move_request.player_name, current_player_type=move_request.game_state.turn, algorithm=move_request.algorithm)

    suggested_move: SuggestedMove = ai.generate_ai_move()
    # suggested_move: SuggestedMove = ai.generate_random_move()

    return suggested_move
