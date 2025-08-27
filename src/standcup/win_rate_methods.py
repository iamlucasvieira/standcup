"""Win rate calculation methods for different player ranking approaches.

This module provides various methods for calculating win rates, each with different
characteristics for handling small sample sizes and competitive balance.
"""

from enum import StrEnum, auto

from standcup.wilson_score import get_wilson_win_rate


class WinRateMethod(StrEnum):
    """Win rate calculation methods."""

    SIMPLE = auto()
    WILSON_LOWER = auto()
    WILSON_CENTER = auto()
    ADDITIVE_SMOOTHING = auto()
    ELO_BASED = auto()


def simple_win_rate(wins: int, total: int) -> float:
    """Calculate simple win rate percentage.

    This is the most straightforward method but can be misleading for players
    with few games (e.g., 1 win out of 1 game = 100%).

    Args:
        wins: Number of wins
        total: Total number of games played

    Returns:
        Win rate as a percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (wins / total) * 100


def wilson_lower_bound_win_rate(wins: int, total: int, confidence: float = 0.95) -> float:
    """Calculate Wilson score lower bound win rate.

    Conservative estimate that heavily penalizes players with fewer games.
    Good for identifying truly consistent performers.

    Args:
        wins: Number of wins
        total: Total number of games played
        confidence: Confidence level (default 0.95)

    Returns:
        Win rate as a percentage (0-100)
    """
    return get_wilson_win_rate(wins, total, method="lower_bound", confidence=confidence)


def wilson_center_win_rate(wins: int, total: int, confidence: float = 0.95) -> float:
    """Calculate Wilson score center point win rate.

    Balanced estimate that accounts for sample size but is less extreme
    than the lower bound. This is the current default method.

    Args:
        wins: Number of wins
        total: Total number of games played
        confidence: Confidence level (default 0.95)

    Returns:
        Win rate as a percentage (0-100)
    """
    return get_wilson_win_rate(wins, total, method="center", confidence=confidence)


def additive_smoothing_win_rate(wins: int, total: int, alpha: float = 2.0) -> float:
    """Calculate win rate using additive smoothing (Laplace smoothing).

    Adds pseudo-counts to both wins and losses, creating more separation
    between players while still being conservative for small samples.
    Higher alpha = more conservative.

    Args:
        wins: Number of wins
        total: Total number of games played
        alpha: Smoothing parameter (default 2.0, equivalent to adding 2 wins and 2 losses)

    Returns:
        Win rate as a percentage (0-100)
    """
    if total == 0:
        return 50.0  # Neutral starting point

    # Add alpha pseudo-counts to both wins and losses
    smoothed_wins = wins + alpha
    smoothed_total = total + (2 * alpha)

    return (smoothed_wins / smoothed_total) * 100


def elo_based_win_rate(wins: int, total: int, k_factor: float = 32.0, starting_rating: float = 1200.0) -> float:
    """Calculate a win rate based on simplified Elo-style rating progression.

    Simulates an Elo rating system where each win/loss affects the rating,
    then converts the final rating back to a win rate percentage.
    This creates more dynamic separation between players.

    Args:
        wins: Number of wins
        total: Total number of games played
        k_factor: Rating change factor (default 32.0)
        starting_rating: Initial rating (default 1200.0)

    Returns:
        Win rate as a percentage (0-100)
    """
    if total == 0:
        return 50.0  # Neutral starting point

    losses = total - wins
    current_rating = starting_rating

    # Assume average opponent rating of 1200
    opponent_rating = 1200.0

    # Process wins
    for _ in range(wins):
        expected_score = 1 / (1 + 10 ** ((opponent_rating - current_rating) / 400))
        current_rating += k_factor * (1 - expected_score)

    # Process losses
    for _ in range(losses):
        expected_score = 1 / (1 + 10 ** ((opponent_rating - current_rating) / 400))
        current_rating += k_factor * (0 - expected_score)

    # Convert rating back to win rate percentage
    # Rating difference of 400 points ≈ 90% win rate against 1200 player
    # Use sigmoid-like function to convert rating to percentage
    rating_diff = current_rating - starting_rating
    win_rate = 50 + (rating_diff / 400) * 40  # Scale to reasonable range

    # Clamp to 0-100 range
    return max(0.0, min(100.0, win_rate))


def calculate_win_rate(wins: int, total: int, method: WinRateMethod) -> float:
    """Calculate win rate using the specified method.

    Args:
        wins: Number of wins
        total: Total number of games played
        method: Win rate calculation method to use

    Returns:
        Win rate as a percentage (0-100)
    """
    if method == WinRateMethod.SIMPLE:
        return simple_win_rate(wins, total)
    elif method == WinRateMethod.WILSON_LOWER:
        return wilson_lower_bound_win_rate(wins, total)
    elif method == WinRateMethod.WILSON_CENTER:
        return wilson_center_win_rate(wins, total)
    elif method == WinRateMethod.ADDITIVE_SMOOTHING:
        return additive_smoothing_win_rate(wins, total)
    elif method == WinRateMethod.ELO_BASED:
        return elo_based_win_rate(wins, total)
    else:
        # Default to wilson center if unknown method
        return wilson_center_win_rate(wins, total)


def get_method_description(method: WinRateMethod) -> str:
    """Get a human-readable description of the win rate method.

    Args:
        method: Win rate calculation method

    Returns:
        Description of the method's characteristics
    """
    descriptions = {
        WinRateMethod.SIMPLE: "Raw percentage - most volatile, can be misleading for few games",
        WinRateMethod.WILSON_LOWER: "Conservative Wilson bound - heavily penalizes uncertainty",
        WinRateMethod.WILSON_CENTER: "Balanced Wilson score - current default, fairly stable",
        WinRateMethod.ADDITIVE_SMOOTHING: "Smoothed percentage - creates more separation between players",
        WinRateMethod.ELO_BASED: "Elo-inspired rating - dynamic ranking with larger spreads",
    }
    return descriptions.get(method, "Unknown method")


def get_method_display_name(method: WinRateMethod) -> str:
    """Get a display-friendly name for the win rate method.

    Args:
        method: Win rate calculation method

    Returns:
        Display name for the method
    """
    display_names = {
        WinRateMethod.SIMPLE: "Simple %",
        WinRateMethod.WILSON_LOWER: "Wilson Conservative",
        WinRateMethod.WILSON_CENTER: "Wilson Balanced",
        WinRateMethod.ADDITIVE_SMOOTHING: "Smoothed %",
        WinRateMethod.ELO_BASED: "Elo-Style",
    }
    return display_names.get(method, method.value.title())
