#!/usr/bin/env python3
"""
Match-3 Game Bot
Automatically plays match-3 games in a web browser
"""
import argparse
import time
import cv2
import numpy as np
from typing import Optional
import sys
import os

from browser_controller import BrowserController
from board_detector import BoardDetector
from game_logic import GameBoard


class Match3Bot:
    """Main bot class that coordinates all components"""

    def __init__(self, url: str, headless: bool = False, debug: bool = False, browser: str = "auto"):
        self.url = url
        self.headless = headless
        self.debug = debug
        self.browser_type = browser

        self.browser = BrowserController(headless=headless)
        self.detector = BoardDetector()
        self.game_board = GameBoard()

        self.moves_made = 0
        self.max_moves = 1000  # Safety limit

    def start(self):
        """Start the browser and navigate to the game"""
        print("Starting browser...")
        self.browser.start_browser(self.browser_type)

        print(f"Navigating to {self.url}")
        self.browser.navigate_to_game(self.url)

        print("Finding game canvas...")
        if not self.browser.find_game_canvas():
            print("Warning: Could not find game canvas, using default")

        time.sleep(2)  # Wait for game to initialize

    def detect_board_region(self, manual_coords: Optional[dict] = None):
        """
        Detect the game board region
        If manual_coords is provided, use those instead of auto-detection
        """
        print("Taking initial screenshot...")
        screenshot = self.browser.take_screenshot()

        if manual_coords:
            print("Using manual board coordinates...")
            self.detector.detect_grid_manually(
                screenshot,
                (manual_coords['x1'], manual_coords['y1']),
                (manual_coords['x2'], manual_coords['y2']),
                (manual_coords.get('rows', 9), manual_coords.get('cols', 9))
            )
        else:
            print("Auto-detecting board region...")
            region = self.detector.find_board_region(screenshot)
            if region:
                print(f"Board found at: {region}")
            else:
                print("Warning: Auto-detection failed. You may need to provide manual coordinates.")
                # Try to use the whole screen as fallback
                h, w = screenshot.shape[:2]
                self.detector.detect_grid_manually(
                    screenshot,
                    (w // 4, h // 6),
                    (w * 3 // 4, h * 5 // 6)
                )

    def analyze_current_board(self) -> np.ndarray:
        """
        Take a screenshot and analyze the current board state
        Returns the board matrix
        """
        screenshot = self.browser.take_screenshot()
        board = self.detector.analyze_board(screenshot)

        if self.debug:
            # Save debug visualization
            vis = self.detector.visualize_board(screenshot, board)
            debug_path = f"debug_board_{self.moves_made}.png"
            cv2.imwrite(debug_path, vis)
            print(f"Debug image saved to {debug_path}")

        return board

    def execute_move(self, pos1: tuple, pos2: tuple):
        """
        Execute a move by swapping two gems
        pos1 and pos2 are (row, col) tuples
        """
        # Get screen coordinates for both positions
        coords1 = self.detector.get_cell_center(pos1[0], pos1[1])
        coords2 = self.detector.get_cell_center(pos2[0], pos2[1])

        if coords1 is None or coords2 is None:
            print(f"Error: Could not get coordinates for move {pos1} -> {pos2}")
            return False

        print(f"Swapping ({pos1[0]},{pos1[1]}) with ({pos2[0]},{pos2[1]})")

        # Perform the swap
        self.browser.swap_gems(coords1, coords2)

        # Wait for animation and cascades
        self.browser.wait_for_stable_board()

        self.moves_made += 1
        return True

    def play_one_move(self) -> bool:
        """
        Analyze the board and make one move
        Returns True if a move was made, False if no valid moves
        """
        # Analyze current board
        board = self.analyze_current_board()
        self.game_board.set_board(board)

        if self.debug:
            print("\nCurrent board:")
            print(board)

        # Find valid moves
        valid_moves = self.game_board.find_all_valid_moves()

        if not valid_moves:
            print("No valid moves found!")
            return False

        # Execute the best move (first in sorted list)
        best_move = valid_moves[0]
        pos1, pos2, match_count = best_move

        print(f"Found {len(valid_moves)} valid moves. Best move creates {match_count} matches.")

        return self.execute_move(pos1, pos2)

    def run(self, max_moves: Optional[int] = None, manual_coords: Optional[dict] = None):
        """
        Main game loop
        """
        try:
            self.start()
            self.detect_board_region(manual_coords)

            if max_moves:
                self.max_moves = max_moves

            print(f"\nStarting game loop (max {self.max_moves} moves)...")
            print("Press Ctrl+C to stop\n")

            while self.moves_made < self.max_moves:
                print(f"\n--- Move {self.moves_made + 1} ---")

                # Check if game is over
                if self.browser.is_game_over():
                    print("Game over detected!")
                    if self.browser.restart_game():
                        print("Game restarted, continuing...")
                        time.sleep(2)
                    else:
                        print("Could not restart game, stopping.")
                        break

                # Make one move
                if not self.play_one_move():
                    print("No valid moves available. Waiting and retrying...")
                    time.sleep(2)

                    # Try one more time
                    if not self.play_one_move():
                        print("Still no valid moves. Game may be stuck.")
                        break

                # Small delay between moves
                time.sleep(0.5)

            print(f"\nBot finished after {self.moves_made} moves")

        except KeyboardInterrupt:
            print("\n\nBot stopped by user")

        except Exception as e:
            print(f"\nError occurred: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("\nClosing browser...")
        self.browser.close()
        print("Done!")


def main():
    parser = argparse.ArgumentParser(description="Match-3 Game Bot")
    parser.add_argument("url", help="URL of the match-3 game")
    parser.add_argument("--browser", default="auto",
                       choices=["auto", "edge", "chrome", "firefox"],
                       help="Browser to use (default: auto-detect)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (save screenshots)")
    parser.add_argument("--max-moves", type=int, help="Maximum number of moves to make")
    parser.add_argument("--x1", type=int, help="Manual board detection: top-left X coordinate")
    parser.add_argument("--y1", type=int, help="Manual board detection: top-left Y coordinate")
    parser.add_argument("--x2", type=int, help="Manual board detection: bottom-right X coordinate")
    parser.add_argument("--y2", type=int, help="Manual board detection: bottom-right Y coordinate")
    parser.add_argument("--rows", type=int, default=9, help="Number of rows in the grid")
    parser.add_argument("--cols", type=int, default=9, help="Number of columns in the grid")

    args = parser.parse_args()

    # Build manual coordinates dict if provided
    manual_coords = None
    if args.x1 is not None and args.y1 is not None and args.x2 is not None and args.y2 is not None:
        manual_coords = {
            'x1': args.x1,
            'y1': args.y1,
            'x2': args.x2,
            'y2': args.y2,
            'rows': args.rows,
            'cols': args.cols
        }

    # Create and run the bot
    bot = Match3Bot(args.url, headless=args.headless, debug=args.debug, browser=args.browser)
    bot.run(max_moves=args.max_moves, manual_coords=manual_coords)


if __name__ == "__main__":
    main()
