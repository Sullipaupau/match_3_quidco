"""
Board Detector Module
Handles detecting and analyzing the game board from screenshots
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional, List
import hashlib


class BoardDetector:
    """Detects and analyzes the match-3 game board from screenshots"""

    def __init__(self):
        self.gem_templates = {}
        self.grid_size = (9, 9)  # Default grid size
        self.cell_size = 0
        self.board_region = None

    def find_board_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the game board region in the screenshot
        Returns (x, y, width, height) or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest rectangular contour (likely the game board)
        max_area = 0
        best_rect = None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter by aspect ratio (should be roughly square)
            aspect_ratio = w / h if h > 0 else 0
            if 0.8 < aspect_ratio < 1.2 and area > max_area and area > 10000:
                max_area = area
                best_rect = (x, y, w, h)

        if best_rect:
            self.board_region = best_rect
            # Calculate cell size based on 9x9 grid
            self.cell_size = best_rect[2] // self.grid_size[1]

        return best_rect

    def extract_cell_image(self, image: np.ndarray, row: int, col: int) -> Optional[np.ndarray]:
        """Extract the image of a specific cell from the board"""
        if self.board_region is None or self.cell_size == 0:
            return None

        x, y, w, h = self.board_region
        cell_x = x + col * self.cell_size
        cell_y = y + row * self.cell_size

        # Add some padding to avoid edge artifacts
        padding = int(self.cell_size * 0.1)
        cell_x += padding
        cell_y += padding
        cell_size = self.cell_size - 2 * padding

        cell_image = image[cell_y:cell_y + cell_size, cell_x:cell_x + cell_size]
        return cell_image

    def get_gem_hash(self, cell_image: np.ndarray) -> str:
        """
        Generate a hash for a gem image to identify unique gem types
        Uses color histogram as a simple feature
        """
        # Resize to standard size
        resized = cv2.resize(cell_image, (32, 32))

        # Calculate color histogram
        hist_b = cv2.calcHist([resized], [0], None, [8], [0, 256])
        hist_g = cv2.calcHist([resized], [1], None, [8], [0, 256])
        hist_r = cv2.calcHist([resized], [2], None, [8], [0, 256])

        # Normalize
        hist_b = hist_b / hist_b.sum()
        hist_g = hist_g / hist_g.sum()
        hist_r = hist_r / hist_r.sum()

        # Combine and create hash
        combined = np.concatenate([hist_b, hist_g, hist_r]).flatten()
        hash_str = hashlib.md5(combined.tobytes()).hexdigest()[:8]

        return hash_str

    def analyze_board(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the board and return a matrix of gem types
        Each gem type is assigned a unique integer
        """
        # Find board region if not already found
        if self.board_region is None:
            self.find_board_region(image)

        if self.board_region is None:
            raise ValueError("Could not find game board in image")

        rows, cols = self.grid_size
        board = np.zeros((rows, cols), dtype=int)
        gem_hash_to_id = {}
        next_gem_id = 1

        for row in range(rows):
            for col in range(cols):
                cell_image = self.extract_cell_image(image, row, col)

                if cell_image is None or cell_image.size == 0:
                    continue

                # Get gem hash
                gem_hash = self.get_gem_hash(cell_image)

                # Assign gem ID
                if gem_hash not in gem_hash_to_id:
                    gem_hash_to_id[gem_hash] = next_gem_id
                    next_gem_id += 1

                board[row, col] = gem_hash_to_id[gem_hash]

        return board

    def detect_grid_manually(self, image: np.ndarray,
                            top_left: Tuple[int, int],
                            bottom_right: Tuple[int, int],
                            grid_size: Tuple[int, int] = (9, 9)):
        """
        Manually set the board region and grid size
        Useful when automatic detection fails
        """
        x1, y1 = top_left
        x2, y2 = bottom_right
        self.board_region = (x1, y1, x2 - x1, y2 - y1)
        self.grid_size = grid_size
        self.cell_size = (x2 - x1) // grid_size[1]

    def get_cell_center(self, row: int, col: int) -> Optional[Tuple[int, int]]:
        """Get the center coordinates of a cell on the screen"""
        if self.board_region is None or self.cell_size == 0:
            return None

        x, y, w, h = self.board_region
        cell_x = x + col * self.cell_size + self.cell_size // 2
        cell_y = y + row * self.cell_size + self.cell_size // 2

        return (cell_x, cell_y)

    def visualize_board(self, image: np.ndarray, board: np.ndarray) -> np.ndarray:
        """
        Create a visualization of the detected board
        Draws grid lines and gem IDs
        """
        vis_image = image.copy()

        if self.board_region is None:
            return vis_image

        rows, cols = self.grid_size
        x, y, w, h = self.board_region

        # Draw grid lines
        for i in range(rows + 1):
            y_pos = y + i * self.cell_size
            cv2.line(vis_image, (x, y_pos), (x + w, y_pos), (0, 255, 0), 2)

        for i in range(cols + 1):
            x_pos = x + i * self.cell_size
            cv2.line(vis_image, (x_pos, y), (x_pos, y + h), (0, 255, 0), 2)

        # Draw gem IDs
        for row in range(rows):
            for col in range(cols):
                center = self.get_cell_center(row, col)
                if center:
                    gem_id = board[row, col]
                    cv2.putText(vis_image, str(gem_id), center,
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return vis_image
