"""
Match-3 Game Logic Module
Handles finding valid moves and matches in the game board
"""
from typing import List, Tuple, Optional, Set
import numpy as np


class GameBoard:
    """Represents the match-3 game board and provides logic for finding moves"""

    def __init__(self, rows: int = 9, cols: int = 9):
        self.rows = rows
        self.cols = cols
        self.board = None

    def set_board(self, board: np.ndarray):
        """Set the current board state"""
        self.board = board
        self.rows, self.cols = board.shape

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within board bounds"""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def find_matches(self, board: Optional[np.ndarray] = None) -> Set[Tuple[int, int]]:
        """
        Find all cells that are part of a match (3 or more in a row/column)
        Returns a set of (row, col) tuples
        """
        if board is None:
            board = self.board

        if board is None:
            return set()

        matches = set()

        # Check horizontal matches
        for row in range(self.rows):
            col = 0
            while col < self.cols:
                gem_type = board[row, col]
                if gem_type == 0:  # Empty cell
                    col += 1
                    continue

                # Count consecutive gems of the same type
                count = 1
                start_col = col
                while col + count < self.cols and board[row, col + count] == gem_type:
                    count += 1

                # If we have 3 or more, add them to matches
                if count >= 3:
                    for c in range(start_col, start_col + count):
                        matches.add((row, c))

                col += count if count > 1 else 1

        # Check vertical matches
        for col in range(self.cols):
            row = 0
            while row < self.rows:
                gem_type = board[row, col]
                if gem_type == 0:  # Empty cell
                    row += 1
                    continue

                # Count consecutive gems of the same type
                count = 1
                start_row = row
                while row + count < self.rows and board[row + count, col] == gem_type:
                    count += 1

                # If we have 3 or more, add them to matches
                if count >= 3:
                    for r in range(start_row, start_row + count):
                        matches.add((r, col))

                row += count if count > 1 else 1

        return matches

    def simulate_swap(self, row1: int, col1: int, row2: int, col2: int) -> Optional[Set[Tuple[int, int]]]:
        """
        Simulate a swap and return the matches that would result
        Returns None if the swap is invalid
        """
        if not self.is_valid_position(row1, col1) or not self.is_valid_position(row2, col2):
            return None

        # Create a copy of the board
        temp_board = self.board.copy()

        # Perform the swap
        temp_board[row1, col1], temp_board[row2, col2] = temp_board[row2, col2], temp_board[row1, col1]

        # Find matches after the swap
        matches = self.find_matches(temp_board)

        return matches if len(matches) > 0 else None

    def find_all_valid_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int], int]]:
        """
        Find all valid moves on the current board
        Returns a list of ((row1, col1), (row2, col2), match_count) tuples
        sorted by match count (descending)
        """
        if self.board is None:
            return []

        valid_moves = []

        # Check all possible swaps (only right and down to avoid duplicates)
        for row in range(self.rows):
            for col in range(self.cols):
                # Try swapping with the gem to the right
                if col + 1 < self.cols:
                    matches = self.simulate_swap(row, col, row, col + 1)
                    if matches:
                        valid_moves.append(((row, col), (row, col + 1), len(matches)))

                # Try swapping with the gem below
                if row + 1 < self.rows:
                    matches = self.simulate_swap(row, col, row + 1, col)
                    if matches:
                        valid_moves.append(((row, col), (row + 1, col), len(matches)))

        # Sort by match count (descending) to prioritize better moves
        valid_moves.sort(key=lambda x: x[2], reverse=True)

        return valid_moves

    def get_adjacent_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all valid adjacent positions (up, down, left, right)"""
        adjacent = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                adjacent.append((new_row, new_col))

        return adjacent
