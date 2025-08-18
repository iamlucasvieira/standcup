"""UI components for rendering player statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from standcup.player_insights import get_player_personality
from standcup.visualizations.charts import create_goals_chart, create_win_rate_gauge

if TYPE_CHECKING:
    import pandas as pd


def render_empty_stats() -> None:
    """Render empty stats message."""
    st.warning("🏆 The Hall of Fame awaits its first legend!")
    st.info(
        "🚀 **Ready to make history?** Every great player started with their first match. Your journey to glory begins now!"
    )


def render_player_header(selected_player: str, player_stats: pd.Series) -> None:
    """Render the player header with key stats."""
    personality = get_player_personality(player_stats)

    # Hero section
    st.markdown(
        f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin: 20px 0;">
        <h1 style="color: white; margin: 0;">🏆 {selected_player}</h1>
        <p style="color: white; font-size: 18px; margin: 10px 0;">{personality["win_style"]} • {personality["goal_style"]} • {personality["activity"]}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_key_metrics(player_stats: pd.Series) -> None:
    """Render key performance metrics in a modern card layout."""
    st.markdown("### 📊 Key Performance Metrics")

    # Create 4 columns for key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="🏆 Win Rate", value=f"{player_stats['win_rate']:.1f}%", delta=f"{player_stats['wins']} wins")

    with col2:
        st.metric(
            label="⚽ Goals For",
            value=int(player_stats["goals_for"]),
            delta=f"{player_stats['avg_goals_per_match']:.1f} per match",
        )

    with col3:
        st.metric(label="🛡️ Goal Difference", value=f"{player_stats['goal_difference']:+.0f}", delta="Net advantage")

    with col4:
        st.metric(label="🎮 Matches Played", value=int(player_stats["matches_played"]), delta="Total experience")


def render_detailed_stats(player_stats: pd.Series) -> None:
    """Render detailed statistics with charts."""
    st.markdown("### 📈 Detailed Performance Analysis")

    # Two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Win Rate Gauge")
        win_rate_gauge = create_win_rate_gauge(player_stats["win_rate"])
        st.plotly_chart(win_rate_gauge, use_container_width=True)

    with col2:
        st.markdown("#### ⚽ Goals Analysis")
        goals_chart = create_goals_chart(int(player_stats["goals_for"]), int(player_stats["goals_against"]))
        st.plotly_chart(goals_chart, use_container_width=True)

    # Additional metrics below charts
    st.markdown("#### 📋 Match Breakdown")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Wins:** {int(player_stats['wins'])}")

    with col2:
        st.error(f"**Losses:** {int(player_stats['losses'])}")

    with col3:
        st.warning(f"**Goals Against:** {int(player_stats['goals_against'])}")
