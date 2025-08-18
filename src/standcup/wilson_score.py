"""Wilson score interval for better win rate calculations.

The Wilson score interval provides a better estimate of win rates that accounts
for the number of games played. It's more conservative for players with fewer
games and converges to the simple win rate as the sample size increases.
"""

from __future__ import annotations

import math
from typing import Literal

MethodType = Literal["lower_bound", "center"]


def wilson_score_lower_bound(wins: int, total: int, confidence: float = 0.95) -> float:
    """Calculate the lower bound of Wilson score confidence interval.

    This gives a more conservative estimate of win rate that accounts for
    sample size. Players with fewer games get penalized more heavily.

    Args:
        wins: Number of wins
        total: Total number of games played
        confidence: Confidence level (default 0.95 for 95% confidence)

    Returns:
        Lower bound of Wilson score interval as a percentage (0-100)
    """
    if total == 0:
        return 0.0

    # Z-score for the confidence level
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
    }
    z = z_scores.get(confidence, 1.96)

    p = wins / total
    n = total

    # Wilson score formula
    numerator = p + (z * z) / (2 * n) - z * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)
    denominator = 1 + (z * z) / n

    lower_bound = numerator / denominator
    return max(0.0, lower_bound * 100)


def wilson_score_center(wins: int, total: int, confidence: float = 0.95) -> float:
    """Calculate the center (point estimate) of Wilson score confidence interval.

    This gives a balanced estimate that's less extreme than the lower bound
    but still accounts for sample size uncertainty.

    Args:
        wins: Number of wins
        total: Total number of games played
        confidence: Confidence level (default 0.95 for 95% confidence)

    Returns:
        Center point of Wilson score interval as a percentage (0-100)
    """
    if total == 0:
        return 0.0

    # Z-score for the confidence level
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
    }
    z = z_scores.get(confidence, 1.96)

    p = wins / total
    n = total

    # Wilson score center formula
    numerator = p + (z * z) / (2 * n)
    denominator = 1 + (z * z) / n

    center = numerator / denominator
    return center * 100


def get_wilson_win_rate(wins: int, total: int, method: MethodType = "lower_bound", confidence: float = 0.95) -> float:
    """Get Wilson score-based win rate.

    Args:
        wins: Number of wins
        total: Total number of games played
        method: Either "lower_bound" (conservative) or "center" (balanced)
        confidence: Confidence level (default 0.95)

    Returns:
        Wilson score win rate as a percentage (0-100)
    """
    if method == "center":
        return wilson_score_center(wins, total, confidence)
    else:
        return wilson_score_lower_bound(wins, total, confidence)
