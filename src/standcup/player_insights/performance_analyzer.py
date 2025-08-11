"""Performance analysis and insights for players."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    import pandas as pd


def render_player_insights(player_stats: pd.Series, stats_df: pd.DataFrame) -> None:
    """Render interesting player insights and fun statistics."""
    st.markdown("### 🧠 Player Insights & Fun Facts")

    # Calculate some interesting metrics
    total_players = len(stats_df)
    player_rank = stats_df[stats_df["player_name"] == player_stats["player_name"]].index[0] + 1
    percentile = ((total_players - player_rank) / total_players) * 100

    # Fun facts and insights
    col1, col2 = st.columns(2)

    with col1:
        _render_performance_analysis(player_stats, percentile)

    with col2:
        _render_playing_style_analysis(player_stats)


def _render_performance_analysis(player_stats: pd.Series, percentile: float) -> None:
    """Render performance analysis section."""
    st.markdown("#### 📊 Performance Analysis")

    # Win rate analysis
    if player_stats["win_rate"] >= 80:
        st.success(f"🎯 **Elite Performance**: You're in the top {percentile:.1f}% of players!")
    elif player_stats["win_rate"] >= 60:
        st.info(f"📈 **Above Average**: You're performing better than {percentile:.1f}% of players!")
    elif player_stats["win_rate"] >= 40:
        st.warning(f"⚖️ **Balanced**: You're in the middle {percentile:.1f}% of players!")
    else:
        st.info("🌱 **Growing**: Every match is a learning opportunity!")

    # Goal difference analysis
    if player_stats["goal_difference"] > 0:
        st.success(f"⚽ **Offensive Master**: You score {player_stats['goal_difference']} more goals than you concede!")
    elif player_stats["goal_difference"] < 0:
        st.info("🛡️ **Defensive Specialist**: You're great at keeping games close!")
    else:
        st.info("⚖️ **Perfect Balance**: You're equally strong on both ends!")


def _render_playing_style_analysis(player_stats: pd.Series) -> None:
    """Render playing style analysis section."""
    st.markdown("#### 🎭 Playing Style")

    # Determine playing style
    if player_stats["win_rate"] >= 75 and player_stats["goal_difference"] >= 20:
        st.success("🏆 **Dominant Attacker**: You control the game and score freely!")
    elif player_stats["win_rate"] >= 65 and player_stats["goal_difference"] <= -10:
        st.info("🛡️ **Defensive Master**: You win through solid defense!")
    elif player_stats["matches_played"] >= 30 and player_stats["win_rate"] <= 40:
        st.warning("💪 **Persistent Fighter**: You never give up, even when the odds are against you!")
    elif player_stats["matches_played"] <= 10 and player_stats["win_rate"] >= 60:
        st.success("⭐ **Natural Talent**: You're showing great potential from the start!")
    else:
        st.info("🎯 **Versatile Player**: You adapt your style based on the situation!")
