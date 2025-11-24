"""
Browser Controller Module
Handles browser automation and interaction with the game
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
import time
import numpy as np
from PIL import Image
import io
import platform


class BrowserController:
    """Controls the browser and interacts with the match-3 game"""

    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.game_element = None

    def detect_browser(self) -> str:
        """
        Detect the default browser on the system
        Returns 'edge', 'chrome', or 'firefox'
        """
        system = platform.system().lower()

        # On Windows, Edge is very common
        if system == "windows":
            return "edge"
        # On macOS, Chrome is common
        elif system == "darwin":
            return "chrome"
        # On Linux, Firefox is common
        else:
            return "firefox"

    def start_browser(self, browser_type: str = "auto"):
        """
        Start the browser with appropriate options
        Automatically downloads and manages browser drivers

        Args:
            browser_type: "auto", "edge", "chrome", or "firefox"
        """
        # Auto-detect browser if requested
        if browser_type.lower() == "auto":
            browser_type = self.detect_browser()
            print(f"Auto-detected browser: {browser_type}")

        try:
            if browser_type.lower() == "edge":
                options = webdriver.EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)

                # Auto-download and install EdgeDriver
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)

            elif browser_type.lower() == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)

                # Auto-download and install ChromeDriver
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

            elif browser_type.lower() == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")

                # Auto-download and install GeckoDriver
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)

            else:
                raise ValueError(f"Unsupported browser type: {browser_type}. Use 'auto', 'edge', 'chrome', or 'firefox'")

            self.driver.maximize_window()
            print(f"✓ {browser_type.capitalize()} browser started successfully")

        except Exception as e:
            print(f"Error starting {browser_type} browser: {e}")
            print("Trying fallback browsers...")

            # Try fallback browsers
            fallback_order = ["edge", "chrome", "firefox"]
            if browser_type in fallback_order:
                fallback_order.remove(browser_type)

            for fallback in fallback_order:
                try:
                    print(f"Attempting to start {fallback}...")
                    self.start_browser(fallback)
                    return
                except:
                    continue

            raise RuntimeError("Could not start any browser. Please install Edge, Chrome, or Firefox.")

    def navigate_to_game(self, url: str):
        """Navigate to the game URL"""
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        self.driver.get(url)
        time.sleep(2)  # Wait for page to load

    def find_game_canvas(self) -> bool:
        """
        Find the game canvas or container element
        Returns True if found, False otherwise
        """
        if self.driver is None:
            return False

        # Try to find the game container by common selectors
        selectors = [
            (By.TAG_NAME, "canvas"),
            (By.ID, "game"),
            (By.CLASS_NAME, "game-board"),
            (By.CLASS_NAME, "game-container"),
            (By.XPATH, "//div[contains(@class, 'game')]"),
        ]

        for by, selector in selectors:
            try:
                element = self.driver.find_element(by, selector)
                if element.is_displayed():
                    self.game_element = element
                    return True
            except NoSuchElementException:
                continue

        # If no specific element found, use the body
        self.game_element = self.driver.find_element(By.TAG_NAME, "body")
        return True

    def take_screenshot(self) -> np.ndarray:
        """
        Take a screenshot of the game area
        Returns the image as a numpy array (BGR format for OpenCV)
        """
        if self.driver is None:
            raise RuntimeError("Browser not started")

        # Take screenshot as PNG
        screenshot_png = self.driver.get_screenshot_as_png()

        # Convert to numpy array
        image = Image.open(io.BytesIO(screenshot_png))
        image_array = np.array(image)

        # Convert RGB to BGR for OpenCV
        image_bgr = image_array[:, :, [2, 1, 0]]

        return image_bgr

    def click_at_position(self, x: int, y: int):
        """
        Click at a specific position on the screen
        Uses ActionChains to perform the click
        """
        if self.driver is None or self.game_element is None:
            raise RuntimeError("Browser or game element not initialized")

        # Get the game element's location and size
        location = self.game_element.location
        size = self.game_element.size

        # Calculate offset from the element's top-left corner
        offset_x = x - location['x']
        offset_y = y - location['y']

        # Perform the click
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(self.game_element, offset_x, offset_y)
        actions.click()
        actions.perform()

    def drag_from_to(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.3):
        """
        Perform a drag operation from (x1, y1) to (x2, y2)
        """
        if self.driver is None or self.game_element is None:
            raise RuntimeError("Browser or game element not initialized")

        # Get the game element's location
        location = self.game_element.location

        # Calculate offsets
        offset_x1 = x1 - location['x']
        offset_y1 = y1 - location['y']
        offset_x2 = x2 - location['x']
        offset_y2 = y2 - location['y']

        # Perform drag and drop
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(self.game_element, offset_x1, offset_y1)
        actions.click_and_hold()
        actions.pause(duration / 2)
        actions.move_to_element_with_offset(self.game_element, offset_x2, offset_y2)
        actions.pause(duration / 2)
        actions.release()
        actions.perform()

    def swap_gems(self, pos1: tuple, pos2: tuple, delay: float = 0.5):
        """
        Swap two gems by dragging from pos1 to pos2
        pos1 and pos2 should be (x, y) coordinates
        """
        x1, y1 = pos1
        x2, y2 = pos2

        self.drag_from_to(x1, y1, x2, y2, duration=0.3)
        time.sleep(delay)  # Wait for animation

    def wait_for_stable_board(self, max_wait: float = 5.0, check_interval: float = 0.5):
        """
        Wait for the board to become stable (no more falling gems or animations)
        """
        time.sleep(max_wait)  # Simple approach: just wait for animations

    def is_game_over(self) -> bool:
        """
        Check if the game is over
        Looks for game over elements or modals
        """
        try:
            # Look for common game over indicators
            game_over_selectors = [
                "//div[contains(text(), 'Game Over')]",
                "//div[contains(text(), 'Level Complete')]",
                "//button[contains(text(), 'Play Again')]",
                "//div[contains(@class, 'game-over')]",
                "//div[contains(@class, 'level-complete')]",
            ]

            for selector in game_over_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue

            return False
        except:
            return False

    def restart_game(self) -> bool:
        """
        Try to restart the game by clicking restart/play again button
        Returns True if restart button was found and clicked
        """
        try:
            restart_selectors = [
                "//button[contains(text(), 'Play Again')]",
                "//button[contains(text(), 'Restart')]",
                "//button[contains(text(), 'Try Again')]",
                "//a[contains(text(), 'Play Again')]",
            ]

            for selector in restart_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(2)
                        return True
                except NoSuchElementException:
                    continue

            return False
        except:
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
