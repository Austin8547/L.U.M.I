import sys
import select
import termios
import tty
from typing import Optional


class TerminalKeyListener:
    """Non-blocking terminal key listener using termios/tty for Linux.
    
    Bypasses root requirements while providing real-time keypress tracking.
    """

    def __init__(self):
        self.old_settings = None

    def __enter__(self):
        if sys.stdin.isatty():
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self  

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_settings and sys.stdin.isatty():
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self) -> Optional[str]:
        """Check if a key was pressed without blocking execution."""
        if not sys.stdin.isatty():
            return None

        rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
        if rlist:
            char = sys.stdin.read(1)
            return char
        return None