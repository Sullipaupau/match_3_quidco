#!/usr/bin/env python3
"""
Example usage of the Match-3 Bot
This script shows how to use the bot programmatically
"""
from match3_bot import Match3Bot


def main():
    # Example 1: Basic usage
    print("Example 1: Basic bot usage")
    bot = Match3Bot(
        url="https://example.com/match3-game",
        headless=False,  # Show the browser
        debug=True       # Save debug screenshots
    )
    # bot.run(max_moves=50)

    # Example 2: With manual board coordinates
    print("\nExample 2: Manual board coordinates")
    manual_coords = {
        'x1': 300,   # Top-left X
        'y1': 100,   # Top-left Y
        'x2': 900,   # Bottom-right X
        'y2': 700,   # Bottom-right Y
        'rows': 9,   # Number of rows
        'cols': 9    # Number of columns
    }

    bot2 = Match3Bot(
        url="https://example.com/match3-game",
        headless=False,
        debug=True
    )
    # bot2.run(max_moves=100, manual_coords=manual_coords)

    # Example 3: Headless mode (for running on servers)
    print("\nExample 3: Headless mode")
    bot3 = Match3Bot(
        url="https://example.com/match3-game",
        headless=True,
        debug=False
    )
    # bot3.run(max_moves=500)

    print("\nExamples shown (commented out to avoid actually running)")
    print("Uncomment the bot.run() calls to actually execute")


if __name__ == "__main__":
    main()
