""" This module contains the GameBoard class representing the game board. """


class GameBoard:
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

    def __init__(self):
        # Define the center board
        self.center_board = [
            [{"piece": 0, "valid_moves": [], "type": 1} for _ in range(5)] for _ in range(5)
        ]

        # Define the left and right wings
        self.left_wing = [
            [{"piece": 0, "valid_moves": [], "type": 1} if i == 1 else {
                "piece": 0, "valid_moves": [], "type": 0} for i in range(2)]
            for _ in range(5)
        ]
        self.right_wing = [
            [{"piece": 0, "valid_moves": [], "type": 1} if i == 1 else {
                "piece": 0, "valid_moves": [], "type": 0} for i in range(2)]
            for _ in range(5)
        ]

        # Mark invalid spaces (X)
        for i in [0, 4]:
            self.left_wing[i] = [
                {"piece": 0, "valid_moves": [], "type": 0} for _ in range(2)]
            self.right_wing[i] = [
                {"piece": 0, "valid_moves": [], "type": 0} for _ in range(2)]

        # Add valid_moves manually for type 3 spaces
        # Special space to move to left wing
        self.center_board[2][0]["type"] = 3
        # Special space to move to right wing
        self.center_board[2][4]["type"] = 3

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
                if self.center_board[row][col]["type"] == 1:
                    self.center_board[row][col]["valid_moves"] = self.get_moves(
                        row, col, directions_8, self.center_board)
                elif self.center_board[row][col]["type"] == 2:
                    self.center_board[row][col]["valid_moves"] = self.get_moves(
                        row, col, directions_4, self.center_board)

        # Special moves for wings
        self.center_board[2][0]["valid_moves"] = [(2, 1, "left")]
        self.center_board[2][4]["valid_moves"] = [(2, 1, "right")]

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

    def make_move(self, player, board_type, target_row, target_col):
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
        if board_type == "center_board":
            print(f"Player {player} moved to center board: ({
                  target_row}, {target_col})")
            self.center_board[target_row][target_col]["piece"] = player
        elif board_type == "left_wing":
            print(f"Player {player} moved to left wing: ({
                  target_row}, {target_col})")
            self.left_wing[target_row][target_col]["piece"] = player
        elif board_type == "right_wing":
            print(f"Player {player} moved to right wing: ({
                  target_row}, {target_col})")
            self.right_wing[target_row][target_col]["piece"] = player
