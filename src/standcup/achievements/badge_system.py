"""Badge system for managing and displaying achievements."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from .achievement_types import (
    AchievementBadge,
    ActivityAchievement,
    GoalAchievement,
    PerformanceAchievement,
    RookieAchievement,
    SpecialAchievement,
    StreakAchievement,
    WinRateAchievement,
)

if TYPE_CHECKING:
    import pandas as pd


def get_achievement_badges(player_stats: pd.Series) -> list[AchievementBadge]:
    """Get all achievement badges for a player."""
    badges = []

    # Collect badges from all achievement types
    badges.extend(WinRateAchievement.get_badges(player_stats))
    badges.extend(GoalAchievement.get_badges(player_stats))
    badges.extend(ActivityAchievement.get_badges(player_stats))
    badges.extend(PerformanceAchievement.get_badges(player_stats))
    badges.extend(StreakAchievement.get_badges(player_stats))
    badges.extend(SpecialAchievement.get_badges(player_stats))
    badges.extend(RookieAchievement.get_badges(player_stats))

    return badges


def render_achievement_badges(player_stats: pd.Series) -> None:
    """Render achievement badges in the UI."""
    st.markdown("### 🏅 Achievement Badges")

    badges = get_achievement_badges(player_stats)

    if not badges:
        st.info("🚀 **Rising Star!** Keep playing to unlock achievements!")
        return

    # Display badges in columns
    cols = st.columns(len(badges))
    for i, badge in enumerate(badges):
        with cols[i]:
            if badge.badge_type == "success":
                st.success(f"**{badge.title}**\n{badge.description}")
            elif badge.badge_type == "warning":
                st.warning(f"**{badge.title}**\n{badge.description}")
            else:
                st.info(f"**{badge.title}**\n{badge.description}")
