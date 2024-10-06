import curses
import time
import random

from directory_selector import directory_selection_ui


def draw_starfield(stdscr, num_stars=50, duration=3):
    """Draw an animated starfield for a specified duration."""
    height, width = stdscr.getmaxyx()
    stars = [
        [random.randint(0, height - 1), random.randint(0, width - 1), random.choice(['·', '*', '★'])]
        for _ in range(num_stars)
    ]

    start_time = time.time()
    while time.time() - start_time < duration:
        stdscr.clear()
        for star in stars:
            y, x, char = star
            try:
                stdscr.addch(y, x, char)
            except curses.error:
                pass
            star[1] = (x - 1) % width  # Move star left, wrap around screen
        stdscr.refresh()
        time.sleep(0.1)

def load_ascii_art(filename='ascii-art.txt'):
    try:
        with open(filename, 'r') as f:
            return [line.rstrip() for line in f]
    except FileNotFoundError:
        return ["ASCII ART", "NOT FOUND"]


def draw_ascii_art(stdscr, start_y, start_x, max_height, max_width):
    ascii_art = load_ascii_art()
    for i, line in enumerate(ascii_art):
        if i >= max_height:
            break
        try:
            stdscr.addstr(start_y + i, start_x, line[:max_width], curses.color_pair(4))
        except curses.error:
            pass

def draw_login_page(stdscr, username=""):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    mid_x = width // 2

    # Color setup
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Main text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Input highlights
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warnings/Errors
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # ASCII art

    # Draw ASCII art on the left side
    draw_ascii_art(stdscr, 3, 12, height - 2, mid_x - 2)

    # Draw vertical separator
    for y in range(height):
        try:
            stdscr.addch(y, mid_x, '│', curses.color_pair(1))
        except curses.error:
            pass

    # Title on the right side
    title = "IIITG SECURE LOGIN"
    try:
        stdscr.addstr(2, mid_x + (width - mid_x - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
    except curses.error:
        pass

    # Input fields
    input_start_y = height // 2 - 2
    input_start_x = mid_x + 2

    try:
        stdscr.addstr(input_start_y, input_start_x, "Username:", curses.color_pair(1))
        stdscr.addstr(input_start_y + 2, input_start_x, "Password:", curses.color_pair(1))
    except curses.error:
        pass

    # Pre-fill username if provided
    if username:
        try:
            stdscr.addstr(input_start_y, input_start_x + 10, username)
        except curses.error:
            pass

    # Instructions
    instructions = "Press ENTER to login"
    try:
        stdscr.addstr(height - 2, mid_x + (width - mid_x - len(instructions)) // 2, instructions, curses.color_pair(2))
    except curses.error:
        pass

    stdscr.refresh()
    return input_start_y, input_start_x + 10  # Return positions for input fields

def get_input(stdscr, y, x, hidden=False, prefill_text=""):
    curses.curs_set(1)  # Show cursor
    input_value = list(prefill_text)
    max_length = 20

    while True:
        # Clear the line where the input is displayed
        stdscr.move(y, x)
        stdscr.clrtoeol()

        # Display the input, with '*' for password if hidden
        display_text = ('*' * len(input_value) if hidden else ''.join(input_value))
        try:
            stdscr.addstr(y, x, display_text)
        except curses.error:
            pass

        # Move the cursor to the correct position after the displayed text
        stdscr.move(y, x + len(display_text))

        # Refresh the screen
        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        if key == ord('\n'):  # Enter key
            break
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
            if input_value:
                input_value.pop()  # Remove last character
        elif len(input_value) < max_length and 32 <= key <= 126:  # Valid character input
            input_value.append(chr(key))

    curses.curs_set(0)  # Hide cursor
    return ''.join(input_value)

def loading_bar_animation(stdscr, y, x, width):
    for i in range(width + 1):
        try:
            stdscr.addstr(y, x, f"[{'=' * i}{' ' * (width - i)}]")
            stdscr.addstr(y + 1, x, f"Authenticating: {i * 100 // width}%")
            stdscr.refresh()
        except curses.error:
            pass
        time.sleep(0.05)

def attempt_ssh_login(username, password):
    """Simulate SSH login attempt."""
    time.sleep(2)  # Simulate network delay
    return random.choice([True, False])  # Randomly succeed or fail for demonstration


def login_ui(stdscr):
    curses.curs_set(0)

    # Start with the starfield animation
    draw_starfield(stdscr, num_stars=100, duration=3)

    username = ""
    max_attempts = 3

    for attempt in range(max_attempts):
        input_y, input_x = draw_login_page(stdscr, username)

        if not username:
            username = get_input(stdscr, input_y, input_x)
        password = get_input(stdscr, input_y + 2, input_x, hidden=True)

        # Clear the right side for loading bar
        height, width = stdscr.getmaxyx()
        mid_x = width // 2
        for y in range(height):
            try:
                stdscr.addstr(y, mid_x + 1, " " * (width - mid_x - 1))
            except curses.error:
                pass

        # Show loading bar
        loading_bar_width = min(30, width - mid_x - 4)
        loading_bar_animation(stdscr, height // 2, mid_x + 2, loading_bar_width)

        login_result = attempt_ssh_login(username, password)

        if login_result:
            stdscr.clear()
            success_msg = f"ACCESS GRANTED. WELCOME, {username.upper()}!"
            try:
                stdscr.addstr(height // 2, (width - len(success_msg)) // 2, success_msg,
                              curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            time.sleep(2)

            # Call the directory selection UI after a successful login
            directory_selection_ui(stdscr, username)
            return  # Exit the login function

        error_msg = f"ACCESS DENIED. ATTEMPT {attempt + 1}/{max_attempts}. RETRY?"
        try:
            stdscr.addstr(height - 4, mid_x + (width - mid_x - len(error_msg)) // 2, error_msg,
                          curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass
        stdscr.refresh()
        time.sleep(1.5)

    stdscr.clear()
    final_msg = "MAXIMUM ATTEMPTS EXCEEDED. SYSTEM LOCKED."
    try:
        stdscr.addstr(height // 2, (width - len(final_msg)) // 2, final_msg, curses.color_pair(3) | curses.A_BOLD)
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()
