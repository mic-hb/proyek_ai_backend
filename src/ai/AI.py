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
            return None, None, self.do_evaluation(node)

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

    def do_evaluation(self, node: Board) -> float:
        """
        Evaluate the score of a terminal node for the current player.
        Replace with game-specific evaluation logic.
        """
        if self.algorithm == 1:
            return self.evaluate_1(node)
        elif self.algorithm == 2:
            return self.evaluate_2(node)
        else:
            return self.evaluate_1(node)

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

    def evaluate_1(self, node: Board) -> float:
        """
        Fungsi evaluasi untuk menentukan skor permainan berdasarkan posisi pion macan dan uwong.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
                    contoh: {"macan": [(x1, y1), (x2, y2)], "uwong": [(x3, y3), (x4, y4), ...]}
        :return: skor evaluasi (positif jika menguntungkan macan, negatif jika menguntungkan uwong)
        """
        nilai_macan = 0
        nilai_uwong = 0

        posisi = {"macan": [], "uwong": []}
        for row in range(len(node)):
            for col in range(len(node[row])):
                cell = node[row][col]
                if cell.piece.type == PieceTypes.MACAN:
                    posisi["macan"].append((row, col))
                elif cell.piece.type == PieceTypes.UWONG:
                    posisi["uwong"].append((row, col))

        # # Macan: Evaluasi langkah valid
        # for macan in posisi['macan']:
        #     langkah_valid = self.get_valid_moves_for_pion(posisi, macan)
        #     nilai_macan += len(langkah_valid) * 5

        #     # Ancaman pengepungan
        #     pion_di_sekitar = self.get_pion_di_sekitar(posisi, macan, "uwong")
        #     nilai_macan -= len(pion_di_sekitar) * 5

        #     # Peluang untuk melompat
        #     garis_genap = self.get_garis_genap(posisi, macan, "uwong")
        #     nilai_macan += len(garis_genap) * 30

        #     # Penalti jika pola ganjil di garis lurus
        #     garis_ganjil = self.get_garis_ganjil(posisi, macan, "uwong")
        #     nilai_macan -= len(garis_ganjil) * 10

        # # Uwong: Evaluasi langkah valid dan pola
        # for uwong in posisi['uwong']:
        #     langkah_valid = self.get_valid_moves_for_pion(posisi, uwong)
        #     nilai_uwong += len(langkah_valid) * 5

        #     # Bonus untuk pola ganjil
        #     garis_ganjil = self.get_garis_ganjil(posisi, uwong, "uwong")
        #     nilai_uwong += len(garis_ganjil) * 20

        #     # Penalti untuk pola genap
        #     garis_genap = self.get_garis_genap(posisi, uwong, "uwong")
        #     nilai_uwong -= len(garis_genap) * 10

        #     # Penalti untuk pion terisolasi
        #     pion_di_sekitar = self.get_pion_di_sekitar(posisi, uwong, "uwong")
        #     if len(pion_di_sekitar) == 0:
        #         nilai_uwong += 10

        # # Uwong: Evaluasi blokade
        # for macan in posisi['macan']:
        #     langkah_valid = self.get_valid_moves_for_pion(posisi, macan)
        #     blokir = len([move for move in langkah_valid if move in posisi['uwong']])
        #     nilai_uwong += blokir * 10

        # # Evaluasi kemenangan
        # if all(len(self.get_valid_moves_for_pion(posisi, macan)) == 0 for macan in posisi['macan']):
        #     # Uwong menang
        #     return -1000
        # if all(len(self.get_valid_moves_for_pion(posisi, uwong)) == 0 for uwong in posisi['uwong']):
        #     # Macan menang
        #     return 1000

        nilai_macan = self.evaluate_macan(posisi['macan'], posisi['uwong'], len(node))
        nilai_uwong = self.evaluate_uwong(posisi['uwong'], posisi['macan'], len(node))

        # Evaluasi total (nilai macan - nilai uwong)
        return nilai_macan - nilai_uwong


    # def get_valid_moves_for_pion(self, posisi, pion):
    #     """
    #     Mengembalikan daftar langkah valid untuk pion tertentu.
    #     :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
    #     :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
    #     :return: list langkah valid (x, y).
    #     """
    #     x, y = pion
    #     langkah = [
    #         (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),  # Vertikal & Horizontal
    #         (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)  # Diagonal
    #     ]
    #     # Filter langkah yang berada di dalam papan dan tidak ada pion lain
    #     langkah_valid = [
    #         (lx, ly) for lx, ly in langkah
    #         if (lx, ly) not in posisi['macan'] and (lx, ly) not in posisi['uwong'] and 0 <= lx < 8 and 0 <= ly < 8
    #     ]
    #     return langkah_valid


    # def get_pion_di_sekitar(self, posisi, pion, tipe):
    #     """
    #     Mengembalikan daftar pion di sekitar pion tertentu.
    #     :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
    #     :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
    #     :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
    #     :return: list pion di sekitar.
    #     """
    #     x, y = pion
    #     sekitar = [
    #         (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
    #         (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)
    #     ]
    #     pion_di_sekitar = [p for p in sekitar if p in posisi[tipe]]
    #     return pion_di_sekitar


    # def get_garis_genap(self, posisi, pion, tipe):
    #     """
    #     Mengembalikan daftar garis lurus dengan pion jumlah genap.
    #     :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
    #     :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
    #     :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
    #     :return: list garis (daftar pion dalam 1 garis).
    #     """
    #     x, y = pion
    #     arah = [
    #         (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
    #         (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
    #     ]
    #     garis_genap = []

    #     for dx, dy in arah:
    #         garis = []
    #         nx, ny = x + dx, y + dy
    #         while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
    #             garis.append((nx, ny))
    #             nx += dx
    #             ny += dy
    #         if len(garis) > 0 and len(garis) % 2 == 0:  # Hanya ambil jika jumlahnya genap
    #             garis_genap.append(garis)

    #     return garis_genap


    # def get_garis_ganjil(self, posisi, pion, tipe):
    #     """
    #     Mengembalikan daftar garis lurus dengan pion jumlah ganjil.
    #     :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
    #     :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
    #     :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
    #     :return: list garis (daftar pion dalam 1 garis).
    #     """
    #     x, y = pion
    #     arah = [
    #         (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
    #         (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
    #     ]
    #     garis_ganjil = []

    #     for dx, dy in arah:
    #         garis = []
    #         nx, ny = x + dx, y + dy
    #         while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
    #             garis.append((nx, ny))
    #             nx += dx
    #             ny += dy
    #         if len(garis) > 0 and len(garis) % 2 != 0:  # Hanya ambil jika jumlahnya ganjil
    #             garis_ganjil.append(garis)

    #     return garis_ganjil

    ####################################################################################################

    def calculate_macan_penalty(self, macan_positions, board_size):
        """
        Menghitung penalti untuk posisi macan berdasarkan posisi mereka di ujung atau sudut peta.

        Args:
            macan_positions (list of tuple): Daftar posisi macan di papan, [(x1, y1), (x2, y2)].
            board_size (int): Ukuran papan (diasumsikan papan NxN).

        Returns:
            int: Total penalti untuk posisi macan.
        """
        penalty = 0
        corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]
        edges = set(
            [(0, y) for y in range(board_size)] +
            [(board_size - 1, y) for y in range(board_size)] +
            [(x, 0) for x in range(board_size)] +
            [(x, board_size - 1) for x in range(board_size)]
        )
        edges -= set(corners)  # Hilangkan sudut dari tepi

        for position in macan_positions:
            if position in corners:
                penalty -= 15  # Penalti jika macan berada di sudut papan
            elif position in edges:
                penalty -= 10  # Penalti jika macan berada di ujung peta

        return penalty


    def evaluate_macan(self, macan_positions, uwong_positions, board_size):
        """
        Evaluasi nilai total untuk macan berdasarkan faktor-faktor strategis.

        Args:
            macan_positions (list of tuple): Daftar posisi macan di papan.
            uwong_positions (list of tuple): Daftar posisi uwong di papan.
            board_size (int): Ukuran papan (diasumsikan papan NxN).

        Returns:
            int: Total nilai evaluasi macan.
        """
        # Hitung jumlah langkah valid untuk setiap macan
        valid_moves = sum(len(self.get_valid_moves_for_pion(position, macan_positions + uwong_positions, board_size))
                        for position in macan_positions)
        valid_move_score = valid_moves * 5

        # Hitung peluang menerkam uwong
        terkam_score = 0
        for position in macan_positions:
            valid_jumps = self.get_valid_jumps_for_macan(position, uwong_positions, macan_positions, board_size)
            terkam_score += len(valid_jumps) * 40

        # Hitung penalti untuk posisi macan
        position_penalty = self.calculate_macan_penalty(macan_positions, board_size)

        # Total nilai
        total_score = valid_move_score + terkam_score + position_penalty
        print(f"Evaluated score: {total_score}")

        return total_score


    def evaluate_uwong(self, uwong_positions, macan_positions, board_size):
        """
        Evaluasi nilai total untuk uwong berdasarkan faktor-faktor strategis.

        Args:
            uwong_positions (list of tuple): Daftar posisi uwong di papan.
            macan_positions (list of tuple): Daftar posisi macan di papan.
            board_size (int): Ukuran papan (diasumsikan papan NxN).

        Returns:
            int: Total nilai evaluasi uwong.
        """
        # Hitung jumlah langkah valid untuk uwong
        valid_moves = sum(len(self.get_valid_moves_for_pion(position, macan_positions + uwong_positions, board_size))
                        for position in uwong_positions)
        valid_move_score = valid_moves * 5

        # Hitung peluang mengepung macan
        kepung_score = 0
        for macan in macan_positions:
            if len(self.get_valid_moves_for_pion(macan, macan_positions + uwong_positions, board_size)) == 0:
                kepung_score += 30

        # Hitung pion di garis ganjil/genap
        ganjil_score = sum(1 for x, y in uwong_positions if (x + y) % 2 != 0) * 10
        genap_penalty = sum(1 for x, y in uwong_positions if (x + y) % 2 == 0) * -10

        # Total nilai
        total_score = valid_move_score + kepung_score + ganjil_score + genap_penalty
        return total_score


    def get_valid_moves_for_pion(self, position, all_positions, board_size):
        """
        Mendapatkan langkah valid untuk pion, baik macan atau uwong, pada papan.

        Args:
            position (tuple): Posisi pion yang akan dihitung langkah validnya.
            all_positions (list of tuple): Daftar posisi semua pion (macan dan uwong) di papan.
            board_size (int): Ukuran papan (diasumsikan papan NxN).

        Returns:
            list: Daftar langkah valid yang bisa diambil pion.
        """
        x, y = position
        valid_moves = []

        # Cek 4 arah (atas, bawah, kiri, kanan)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Pastikan langkah masih dalam batas papan
            if 0 <= nx < board_size and 0 <= ny < board_size:
                # Pastikan tidak ada pion yang menghalangi langkah
                if (nx, ny) not in all_positions:
                    valid_moves.append((nx, ny))

        return valid_moves


    def get_valid_jumps_for_macan(self, macan_position, uwong_positions, macan_positions, board_size):
        """
        Mendapatkan semua peluang lompatan untuk macan, dimana macan bisa melompati pion uwong yang berderet
        dalam garis lurus (horizontal, vertikal, atau diagonal) dengan jumlah pion uwong genap.

        Args:
            macan_position (tuple): Posisi macan yang sedang diperiksa.
            uwong_positions (list of tuple): Posisi uwong di papan.
            macan_positions (list of tuple): Posisi macan lainnya di papan.
            board_size (int): Ukuran papan (diasumsikan papan NxN).

        Returns:
            list: Daftar posisi uwong yang dapat diterkam oleh macan.
        """
        x, y = macan_position
        valid_jumps = []

        # Cek 4 arah (horizontal, vertikal, dan diagonal)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            uwong_in_line = []
            # Menelusuri sepanjang garis dalam arah yang sama
            nx, ny = x + dx, y + dy
            while 0 <= nx < board_size and 0 <= ny < board_size:
                if (nx, ny) in uwong_positions:
                    uwong_in_line.append((nx, ny))
                elif (nx, ny) in macan_positions:  # Dihentikan jika ada macan
                    break
                nx, ny = nx + dx, ny + dy

            # Jika ada pion uwong yang terjajar dan jumlahnya genap, simpan sebagai langkah valid
            if len(uwong_in_line) % 2 == 0 and len(uwong_in_line) > 1:
                valid_jumps.extend(uwong_in_line)

        return valid_jumps

    # def get_pion_di_sekitar(self, position, all_positions, board_size):
    #     """
    #     Mendapatkan jumlah pion uwong yang berada di sekitar macan dalam radius satu langkah.

    #     Args:
    #         position (tuple): Posisi pion yang sedang diperiksa.
    #         all_positions (list of tuple): Posisi semua pion (macan dan uwong) di papan.
    #         board_size (int): Ukuran papan (diasumsikan papan NxN).

    #     Returns:
    #         int: Jumlah pion uwong yang berada di sekitar pion yang diperiksa.
    #     """
    #     x, y = position
    #     surrounding_uwong = 0

    #     # Cek 8 arah sekitar pion
    #     directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    #     for dx, dy in directions:
    #         nx, ny = x + dx, y + dy
    #         if 0 <= nx < board_size and 0 <= ny < board_size:
    #             if (nx, ny) in all_positions and (nx, ny) not in macan_positions:
    #                 surrounding_uwong += 1

    #     return surrounding_uwong

    #############################################################################

    def evaluate_2(self, node: Board) -> float:
        """
        Fungsi evaluasi untuk menentukan skor permainan berdasarkan posisi pion macan dan uwong.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
                    contoh: {"macan": [(x1, y1), (x2, y2)], "uwong": [(x3, y3), (x4, y4), ...]}
        :return: skor evaluasi (positif jika menguntungkan macan, negatif jika menguntungkan uwong)
        """
        nilai_macan = 0
        nilai_uwong = 0

        posisi = {"macan": [], "uwong": []}
        for row in range(len(node)):
            for col in range(len(node[row])):
                cell = node[row][col]
                if cell.piece.type == PieceTypes.MACAN:
                    posisi["macan"].append((row, col))
                elif cell.piece.type == PieceTypes.UWONG:
                    posisi["uwong"].append((row, col))

        # Macan: Evaluasi langkah valid
        for macan in posisi['macan']:
            langkah_valid = self.get_valid_moves_for_pion_2(posisi, macan)
            nilai_macan += len(langkah_valid) * 5

            # Ancaman pengepungan
            pion_di_sekitar = self.get_pion_di_sekitar(posisi, macan, "uwong")
            nilai_macan -= len(pion_di_sekitar) * 10

            # Peluang untuk melompat
            garis_genap = self.get_garis_genap(posisi, macan, "uwong")
            nilai_macan += len(garis_genap) * 15

            # Penalti jika pola ganjil di garis lurus
            garis_ganjil = self.get_garis_ganjil(posisi, macan, "uwong")
            nilai_macan -= len(garis_ganjil) * 10

        # Uwong: Evaluasi langkah valid dan pola
        for uwong in posisi['uwong']:
            langkah_valid = self.get_valid_moves_for_pion_2(posisi, uwong)
            nilai_uwong += len(langkah_valid) * 5

            # Bonus untuk pola ganjil
            garis_ganjil = self.get_garis_ganjil(posisi, uwong, "uwong")
            nilai_uwong += len(garis_ganjil) * 15

            # Penalti untuk pola genap
            garis_genap = self.get_garis_genap(posisi, uwong, "uwong")
            nilai_uwong -= len(garis_genap) * 10

            # Penalti untuk pion terisolasi
            pion_di_sekitar = self.get_pion_di_sekitar(posisi, uwong, "uwong")
            if len(pion_di_sekitar) == 0:
                nilai_uwong -= 10

        # Uwong: Evaluasi blokade
        for macan in posisi['macan']:
            langkah_valid = self.get_valid_moves_for_pion_2(posisi, macan)
            blokir = len([move for move in langkah_valid if move in posisi['uwong']])
            nilai_uwong += blokir * 10

        # Evaluasi kemenangan
        if all(len(self.get_valid_moves_for_pion_2(posisi, macan)) == 0 for macan in posisi['macan']):
            # Uwong menang
            return -1000
        if all(len(self.get_valid_moves_for_pion_2(posisi, uwong)) == 0 for uwong in posisi['uwong']):
            # Macan menang
            return 1000

        # Evaluasi total (nilai macan - nilai uwong)
        return nilai_macan - nilai_uwong


    def get_valid_moves_for_pion_2(self, posisi, pion):
        """
        Mengembalikan daftar langkah valid untuk pion tertentu.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :return: list langkah valid (x, y).
        """
        x, y = pion
        langkah = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),  # Vertikal & Horizontal
            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)  # Diagonal
        ]
        # Filter langkah yang berada di dalam papan dan tidak ada pion lain
        langkah_valid = [
            (lx, ly) for lx, ly in langkah
            if (lx, ly) not in posisi['macan'] and (lx, ly) not in posisi['uwong'] and 0 <= lx < 8 and 0 <= ly < 8
        ]
        return langkah_valid


    def get_pion_di_sekitar(self, posisi, pion, tipe):
        """
        Mengembalikan daftar pion di sekitar pion tertentu.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list pion di sekitar.
        """
        x, y = pion
        sekitar = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)
        ]
        pion_di_sekitar = [p for p in sekitar if p in posisi[tipe]]
        return pion_di_sekitar


    def get_garis_genap(self, posisi, pion, tipe):
        """
        Mengembalikan daftar garis lurus dengan pion jumlah genap.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list garis (daftar pion dalam 1 garis).
        """
        x, y = pion
        arah = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]
        garis_genap = []

        for dx, dy in arah:
            garis = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
                garis.append((nx, ny))
                nx += dx
                ny += dy
            if len(garis) > 0 and len(garis) % 2 == 0:  # Hanya ambil jika jumlahnya genap
                garis_genap.append(garis)

        return garis_genap


    def get_garis_ganjil(self, posisi, pion, tipe):
        """
        Mengembalikan daftar garis lurus dengan pion jumlah ganjil.
        :param posisi: dictionary yang berisi lokasi pion macan dan uwong di papan.
        :param pion: tuple (x, y) posisi pion yang sedang dievaluasi.
        :param tipe: tipe pion yang ingin dicari ('macan' atau 'uwong').
        :return: list garis (daftar pion dalam 1 garis).
        """
        x, y = pion
        arah = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Vertikal & Horizontal
            (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal
        ]
        garis_ganjil = []

        for dx, dy in arah:
            garis = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in posisi[tipe]:
                garis.append((nx, ny))
                nx += dx
                ny += dy
            if len(garis) > 0 and len(garis) % 2 != 0:  # Hanya ambil jika jumlahnya ganjil
                garis_ganjil.append(garis)

        return garis_ganjil


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
