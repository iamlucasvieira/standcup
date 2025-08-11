"""Dashboard/Overview page for Standcup."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from standcup.charts import (
    create_cumulative_wins_chart,
    create_goals_chart,
    create_match_timeline,
    create_win_rate_chart,
)
from standcup.models import StandcupData


def render_overview_page(data: StandcupData, stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> None:
    """Render the overview/dashboard page."""
    st.markdown("### 📊 League Overview")
    st.markdown("Get insights into your table football league performance and statistics.")

    st.divider()

    # Key metrics with enhanced styling
    st.markdown("#### 🏆 Key Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_players = len(data.players)
        st.metric(label="👥 Total Players", value=total_players, help="Number of active players in your league")

    with col2:
        total_matches = len(data.matches)
        st.metric(label="⚽ Total Matches", value=total_matches, help="Total matches played across all game types")

    with col3:
        if not matches_df.empty:
            avg_goals = matches_df["total_goals"].mean()
            st.metric(label="🥅 Avg Goals/Match", value=f"{avg_goals:.1f}", help="Average total goals scored per match")
        else:
            st.metric("🥅 Avg Goals/Match", "0.0")

    with col4:
        if not stats_df.empty:
            top_player_idx = stats_df["win_rate"].idxmax()
            top_player = stats_df.loc[top_player_idx, "player_name"]
            top_win_rate = stats_df.loc[top_player_idx, "win_rate"]
            st.metric(
                label="🌟 Top Player",
                value=top_player,
                delta=f"{top_win_rate:.1f}% win rate",
                help="Player with the highest win rate",
            )
        else:
            st.metric("🌟 Top Player", "No data")

    st.divider()

    # Charts section with improved presentation
    if not stats_df.empty:
        st.markdown("#### 📈 Performance Analytics")

        # Leaderboard progression chart - full width
        st.markdown("**Win Progression Over Time**")
        st.plotly_chart(create_cumulative_wins_chart(data), use_container_width=True)

        # Side-by-side performance charts
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**Player Win Rates**")
            st.plotly_chart(create_win_rate_chart(stats_df), use_container_width=True)

        with col2:
            st.markdown("**Goal Statistics**")
            st.plotly_chart(create_goals_chart(stats_df), use_container_width=True)

        # Match activity timeline
        st.markdown("**Match Activity Timeline**")
        st.plotly_chart(create_match_timeline(data), use_container_width=True)
    else:
        st.info("📊 Charts will appear here once you have match data!")
        st.markdown("Start playing matches to see beautiful analytics and insights.")
