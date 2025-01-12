"""Utility functions for the Shmistogram package."""

from time import time


def say_time_since(timestamp: float, task: str | None) -> None:
    """Summarize the time since a timestamp."""
    delta = time() - timestamp
    task = task or ""
    print(f"{task} seconds elapsed: {delta}")


class ClassUtils:
    """Basic methods useful in many classes."""

    verbose: bool

    def vp(self, string):
        """Verbose print."""
        if self.verbose:
            print(string)

    def timer(self, timestamp: float | None = None, task: str | None = None) -> float | None:
        """Set a timestamp or return time since a timestamp.

        Args:
            timestamp: If None, return time(); else summarize the time since timestamp
            task: A description of what is being timed
        """
        if not self.verbose:
            return None
        if timestamp is None:
            return time()
        else:
            say_time_since(timestamp, task=task)
