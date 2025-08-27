"""Leaderboard page for Standcup - Table Football Tracker."""

import pandas as pd
import streamlit as st


def render_leaderboard_page(stats_df: pd.DataFrame) -> None:
    """Render the leaderboard page with modern styling."""
    st.markdown("## 🏆 League Leaderboard")
    st.markdown("🌟 **Champions, legends, and rising stars - see where everyone stands!**")

    if stats_df.empty:
        st.warning("🏆 The Hall of Fame awaits its first legend!")
        st.info(
            "🚀 **Ready to make history?** Every great player started with their first match. Your journey to glory begins now!"
        )
        return

    # Filter and prepare data
    display_stats = stats_df[
        [
            "player_name",
            "matches_played",
            "wins",
            "losses",
            "win_rate",
            "goals_for",
            "goals_against",
            "goal_difference",
        ]
    ].copy()

    # Sort by win rate and add ranking
    display_stats = display_stats.sort_values("win_rate", ascending=False)
    display_stats.insert(0, "Rank", range(1, len(display_stats) + 1))

    # Add some interesting statistics below the leaderboard
    st.divider()

    # Highlight top performers
    st.markdown("### 🏅 Top Performers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👥 Total Players", len(stats_df))
        st.metric("🏆 League Leader", display_stats.iloc[0]["player_name"])

    with col2:
        st.metric("📈 Highest Win Rate", f"{display_stats.iloc[0]['win_rate']:.1f}%")
        st.metric("🔥 Most Matches", display_stats.loc[display_stats["matches_played"].idxmax(), "player_name"])

    with col3:
        st.metric("⚽ Best Goal Difference", f"+{display_stats.iloc[0]['goal_difference']}")
        st.metric("🌟 League Veterans", len(stats_df[stats_df["matches_played"] >= 25]))

    # Show podium places
    if len(display_stats) >= 3:
        st.markdown("#### 🏆 Podium")
        podium_cols = st.columns(3)

        with podium_cols[0]:
            if len(display_stats) >= 2:
                st.info(f"🥈 **2nd Place**: {display_stats.iloc[1]['player_name']}")

        with podium_cols[1]:
            st.success(f"👑 **1st Place**: {display_stats.iloc[0]['player_name']}")

        with podium_cols[2]:
            if len(display_stats) >= 3:
                st.warning(f"🥉 **3rd Place**: {display_stats.iloc[2]['player_name']}")

    # Add sorting options
    st.markdown("### 🔄 Sort Options")

    sort_option = st.selectbox(
        "Sort by:",
        options=["Win Rate (Default)", "Goals Scored", "Most Active", "Goal Difference", "Goals Against"],
        index=0,
        help="Choose how to sort the leaderboard",
    )

    # Apply sorting based on selection
    if sort_option == "Goals Scored":
        display_stats = display_stats.sort_values("goals_for", ascending=False)
    elif sort_option == "Most Active":
        display_stats = display_stats.sort_values("matches_played", ascending=False)
    elif sort_option == "Goal Difference":
        display_stats = display_stats.sort_values("goal_difference", ascending=False)
    elif sort_option == "Goals Against":
        display_stats = display_stats.sort_values("goals_against", ascending=True)
    else:  # Win Rate (Default)
        display_stats = display_stats.sort_values("win_rate", ascending=False)

    # Update ranking after sorting
    display_stats["Rank"] = range(1, len(display_stats) + 1)

    # Display the sorted data
    st.dataframe(
        display_stats,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
            "player_name": st.column_config.TextColumn("👤 Player", width="medium"),
            "matches_played": st.column_config.NumberColumn("🎮 Matches", width="small"),
            "wins": st.column_config.NumberColumn("🏆 Wins", width="small"),
            "losses": st.column_config.NumberColumn("💔 Losses", width="small"),
            "win_rate": st.column_config.ProgressColumn("📈 Win Rate (%)", min_value=0, max_value=100, format="%.1f%%"),
            "goals_for": st.column_config.NumberColumn("⚽ Goals For", width="small"),
            "goals_against": st.column_config.NumberColumn("🛡️ Goals Against", width="small"),
            "goal_difference": st.column_config.NumberColumn("🎯 Goal Diff", width="small"),
        },
        hide_index=True,
    )
