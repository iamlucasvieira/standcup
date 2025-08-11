"""Achievement type definitions and logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class AchievementBadge:
    """Represents an achievement badge."""

    title: str
    description: str
    badge_type: str  # "success", "info", "warning"


class WinRateAchievement:
    """Win rate based achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get win rate based achievement badges."""
        badges = []
        win_rate = player_stats["win_rate"]

        if win_rate >= 90:
            badges.append(AchievementBadge("👑 Legendary Champion", "90%+ win rate", "success"))
        elif win_rate >= 80:
            badges.append(AchievementBadge("🏆 Elite Winner", "80%+ win rate", "success"))
        elif win_rate >= 65:
            badges.append(AchievementBadge("🔥 Strong Competitor", "65%+ win rate", "info"))
        elif win_rate >= 50:
            badges.append(AchievementBadge("⚖️ Balanced Player", "50%+ win rate", "info"))

        return badges


class GoalAchievement:
    """Goal difference based achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get goal difference based achievement badges."""
        badges = []
        goal_diff = player_stats["goal_difference"]

        if goal_diff >= 50:
            badges.append(AchievementBadge("⚡ Goal Machine Pro", "50+ goal difference", "success"))
        elif goal_diff >= 30:
            badges.append(AchievementBadge("⚡ Goal Machine", "30+ goal difference", "success"))
        elif goal_diff >= 20:
            badges.append(AchievementBadge("⚡ Goal Scorer", "20+ goal difference", "success"))
        elif goal_diff >= 10:
            badges.append(AchievementBadge("⚡ Sharp Shooter", "10+ goal difference", "info"))
        elif goal_diff >= 0:
            badges.append(AchievementBadge("⚖️ Balanced Player", "Positive goal difference", "info"))
        elif goal_diff >= -10:
            badges.append(AchievementBadge("🛡️ Defensive Player", "Close goal difference", "warning"))

        return badges


class ActivityAchievement:
    """Activity based achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get activity based achievement badges."""
        badges = []
        matches = player_stats["matches_played"]

        if matches >= 100:
            badges.append(AchievementBadge("🌟 Hall of Famer", "100+ matches", "success"))
        elif matches >= 75:
            badges.append(AchievementBadge("⭐ League Legend", "75+ matches", "success"))
        elif matches >= 50:
            badges.append(AchievementBadge("⭐ League Veteran", "50+ matches", "warning"))
        elif matches >= 25:
            badges.append(AchievementBadge("🏃 Active Player", "25+ matches", "info"))
        elif matches >= 10:
            badges.append(AchievementBadge("🌱 Rising Star", "10+ matches", "info"))
        elif matches >= 5:
            badges.append(AchievementBadge("🚀 Rookie", "5+ matches", "info"))

        return badges


class PerformanceAchievement:
    """Performance based achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get performance based achievement badges."""
        badges = []
        wins = player_stats["wins"]

        if wins >= 50:
            badges.append(AchievementBadge("🏅 Victory Master", "50+ wins", "success"))
        elif wins >= 25:
            badges.append(AchievementBadge("🏅 Victory Expert", "25+ wins", "success"))
        elif wins >= 10:
            badges.append(AchievementBadge("🏅 Victory Hunter", "10+ wins", "info"))

        return badges


class StreakAchievement:
    """Streak based achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get streak based achievement badges."""
        badges = []

        if "current_win_streak" in player_stats:
            streak = player_stats["current_win_streak"]
            if streak >= 10:
                badges.append(AchievementBadge("🔥 Unstoppable", "10+ win streak", "success"))
            elif streak >= 5:
                badges.append(AchievementBadge("🔥 Hot Streak", "5+ win streak", "success"))
            elif streak >= 3:
                badges.append(AchievementBadge("🔥 On Fire", "3+ win streak", "info"))

        return badges


class SpecialAchievement:
    """Special combination achievements."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get special combination achievement badges."""
        badges = []
        matches = player_stats["matches_played"]
        win_rate = player_stats["win_rate"]
        goal_diff = player_stats["goal_difference"]

        # Consistent performer
        if matches >= 20 and win_rate >= 75:
            badges.append(AchievementBadge("💎 Consistent Performer", "High activity + win rate", "success"))

        # Dominant force
        if goal_diff >= 15 and win_rate >= 70:
            badges.append(AchievementBadge("🎯 Dominant Force", "High goals + win rate", "success"))

        # Persistent fighter
        if matches >= 30 and win_rate <= 30:
            badges.append(AchievementBadge("💪 Persistent Fighter", "Many matches despite challenges", "warning"))

        # Reliable competitor
        if matches >= 40 and win_rate >= 60:
            badges.append(AchievementBadge("🌟 Reliable Competitor", "Steady performance over time", "info"))

        return badges


class RookieAchievement:
    """Rookie achievements for new players."""

    @staticmethod
    def get_badges(player_stats: pd.Series) -> list[AchievementBadge]:
        """Get rookie achievement badges."""
        badges = []
        matches = player_stats["matches_played"]
        win_rate = player_stats["win_rate"]

        if matches <= 5 and win_rate >= 60:
            badges.append(AchievementBadge("🚀 Promising Start", "Strong start for new player", "info"))

        if matches <= 3 and win_rate >= 80:
            badges.append(AchievementBadge("⭐ Natural Talent", "Exceptional start", "success"))

        return badges
