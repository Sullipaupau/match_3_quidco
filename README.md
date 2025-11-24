# Match-3 Game Bot

An automated bot that plays match-3 games (like Candy Crush, Bejeweled, etc.) in a web browser using computer vision and browser automation.

## Features

- **Automatic board detection**: Uses computer vision to detect and analyze the game board
- **Intelligent move selection**: Finds all valid moves and prioritizes those that create the most matches
- **Browser automation**: Controls the browser using Selenium to execute moves
- **Debug mode**: Save screenshots showing detected board state
- **Manual calibration**: Option to manually specify board coordinates if auto-detection fails

## Requirements

- Python 3.7+
- Chrome or Firefox browser
- ChromeDriver or GeckoDriver (matching your browser version)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd match_3_quidco
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Install browser driver:
   - **Chrome**: Download [ChromeDriver](https://chromedriver.chromium.org/) matching your Chrome version
   - **Firefox**: Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
   - Place the driver in your PATH or in the project directory

## Usage

### Basic Usage

Run the bot with the URL of the match-3 game:

```bash
python match3_bot.py "https://example.com/match3-game"
```

### Options

```
python match3_bot.py <URL> [OPTIONS]

Arguments:
  URL                    URL of the match-3 game

Options:
  --headless            Run browser in headless mode (no GUI)
  --debug               Enable debug mode (save board detection screenshots)
  --max-moves N         Maximum number of moves to make (default: 1000)
  --x1 X --y1 Y         Manual board detection: top-left corner coordinates
  --x2 X --y2 Y         Manual board detection: bottom-right corner coordinates
  --rows N              Number of rows in grid (default: 9)
  --cols N              Number of columns in grid (default: 9)
```

### Examples

**Run with debug mode:**
```bash
python match3_bot.py "https://example.com/game" --debug
```

**Run headless with move limit:**
```bash
python match3_bot.py "https://example.com/game" --headless --max-moves 100
```

**Manual board coordinates (if auto-detection fails):**
```bash
python match3_bot.py "https://example.com/game" --x1 300 --y1 100 --x2 900 --y2 700
```

**For an 8x8 board:**
```bash
python match3_bot.py "https://example.com/game" --rows 8 --cols 8
```

## How It Works

1. **Browser Control**: The bot opens the game in a Selenium-controlled browser
2. **Board Detection**: Takes a screenshot and uses computer vision to locate the game board
3. **Gem Recognition**: Analyzes each cell in the grid and identifies gem types using color histograms
4. **Move Finding**: Uses match-3 logic to find all valid moves (swaps that create 3+ matches)
5. **Move Execution**: Simulates drag-and-drop to swap gems
6. **Repeat**: Waits for animations and continues playing

## Architecture

The project is organized into several modules:

- **match3_bot.py**: Main script and game loop
- **browser_controller.py**: Selenium automation for browser control
- **board_detector.py**: Computer vision for board detection and analysis
- **game_logic.py**: Match-3 game logic and move finding algorithms

## Troubleshooting

### Board Not Detected

If the bot can't find the game board automatically:

1. Run with `--debug` to see what it's detecting
2. Use manual coordinates: measure the board position and provide `--x1 --y1 --x2 --y2`

### Gems Not Recognized Correctly

The bot uses color histograms to identify gems. If gems aren't being distinguished:

- Make sure the game is at full brightness
- Try running the bot again (gem recognition is calibrated per session)
- Check debug images to see how gems are being identified

### Moves Not Executing

If swaps aren't working:

- The game might use a different interaction method (click vs drag)
- Check if there are any overlays or popups blocking the board
- Try adjusting the wait times in browser_controller.py

### Browser Driver Issues

If you get driver errors:

- Make sure ChromeDriver/GeckoDriver matches your browser version
- Add the driver to your system PATH
- Or place it in the project directory

## Configuration

You can modify these settings in the code:

- **Grid size**: Default is 9x9, adjust with `--rows` and `--cols`
- **Wait times**: Edit delays in `browser_controller.py` for faster/slower execution
- **Move limit**: Use `--max-moves` or modify `self.max_moves` in `Match3Bot`

## Known Limitations

- Works best with games that have distinct gem colors
- Requires the game board to be visible (not covered by popups/ads)
- Performance depends on animation speed (slower animations = slower bot)
- May not handle special gems or power-ups optimally

## Contributing

Feel free to improve the bot! Some ideas:

- Better gem recognition using template matching
- Support for special moves (bombs, lasers, etc.)
- Multi-step planning for combo optimization
- Support for different game types (hexagonal grids, etc.)

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This bot is for educational purposes. Use responsibly and in accordance with the game's terms of service.
