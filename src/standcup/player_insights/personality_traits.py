"""Player personality trait analysis based on performance."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def _get_win_personality_tier(win_rate: float, matches: int) -> str:
    """Get win rate personality tier based on win rate and matches."""
    # Define tiers with their conditions
    tiers = [
        (95, 15, "🐐 Table Football Deity"),
        (90, 10, "🐐 Table Football God"),
        (85, 10, "👑 Legendary Champion"),
        (80, 15, "👑 League Dominator"),
        (75, 20, "🔥 Elite Performer"),
        (70, 25, "🔥 Hot Streak"),
        (65, 30, "🔥 Strong Competitor"),
        (60, 35, "⚽ Solid Player"),
        (55, 40, "📈 Fighting Spirit"),
        (50, 45, "⚖️ Balanced Competitor"),
        (45, 50, "📈 Determined Fighter"),
        (40, 55, "🌱 Learning Curve"),
        (35, 60, "💪 Persistent Spirit"),
        (30, 65, "🔄 Improvement Seeker"),
    ]

    # Find the first tier that matches
    for min_win_rate, min_matches, personality in tiers:
        if win_rate >= min_win_rate and matches >= min_matches:
            return personality

    return "💪 Never Give Up"


def _get_goal_personality_tier(goal_diff: float) -> str:
    """Get goal difference personality tier."""
    # Define tiers with their thresholds
    tiers = [
        (100, "🏆 Goal Scoring Legend"),
        (75, "🏆 Goal Machine Pro"),
        (50, "🏆 Goal Machine"),
        (30, "⚡ Attacking Force"),
        (20, "⚡ Sharp Shooter"),
        (10, "⚡ Goal Scorer"),
        (5, "⚡ Offensive Player"),
        (0, "⚖️ Balanced Player"),
        (-5, "🛡️ Defensive Player"),
        (-10, "🛡️ Defensive Mind"),
        (-20, "🛡️ Defensive Specialist"),
        (-30, "🎯 Defensive Master"),
    ]

    # Find the first tier that matches
    for threshold, personality in tiers:
        if goal_diff >= threshold:
            return personality

    return "🎯 Room for Growth"


def _get_activity_personality_tier(matches: int) -> str:
    """Get activity level personality tier."""
    # Define tiers with their thresholds
    tiers = [
        (200, "🎆 Table Football Immortal"),
        (150, "🎆 League Legend"),
        (100, "🌟 Hall of Fame Legend"),
        (75, "⭐ League Legend"),
        (50, "⭐ Seasoned Veteran"),
        (35, "⭐ Regular Champion"),
        (25, "🏃 Experienced Player"),
        (20, "🏃 Active Player"),
        (15, "🏃 Regular Player"),
        (10, "🌱 Rising Star"),
        (5, "🚀 Promising Rookie"),
        (3, "🚀 Newcomer"),
        (1, "🚀 First Steps"),
    ]

    # Find the first tier that matches
    for threshold, personality in tiers:
        if matches >= threshold:
            return personality

    return "🚀 Ready to Play"


def get_player_personality(stats: pd.Series) -> dict[str, str]:
    """Generate personality traits based on player stats."""
    win_rate = stats["win_rate"]
    matches = stats["matches_played"]
    goal_diff = stats["goal_difference"]

    return {
        "win_style": _get_win_personality_tier(win_rate, matches),
        "goal_style": _get_goal_personality_tier(goal_diff),
        "activity": _get_activity_personality_tier(matches),
    }
