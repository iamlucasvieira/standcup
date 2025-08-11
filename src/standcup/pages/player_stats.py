"""Player statistics page for Standcup."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_player_stats_page(stats_df: pd.DataFrame) -> None:
    """Render the player statistics page."""
    st.markdown("### 👥 Player Statistics")
    st.markdown("Dive deep into individual player performance and compare across the league.")

    if stats_df.empty:
        st.warning("⚠️ No player statistics available.")
        st.info("💡 Play some matches to generate player statistics!")
        return

    st.divider()

    # Enhanced player selection
    st.markdown("#### 🔍 Player Analysis")
    selected_player = st.selectbox(
        "Choose a player to analyze:",
        options=stats_df["player_name"].tolist(),
        index=0,
        help="Select any player to see their detailed performance metrics",
    )

    player_stats = stats_df[stats_df["player_name"] == selected_player].iloc[0]

    # Display detailed stats with enhanced presentation
    st.markdown(f"**Performance Overview for {selected_player}**")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("**🎮 Match Record**")
        st.metric("Matches Played", int(player_stats["matches_played"]), help="Total matches participated in")
        st.metric("Wins", int(player_stats["wins"]), delta=f"{player_stats['win_rate']:.1f}% win rate")

    with col2:
        st.markdown("**📊 Win/Loss Record**")
        st.metric("Losses", int(player_stats["losses"]))
        st.metric("Ties", int(player_stats["ties"]))
        goal_diff = player_stats["goal_difference"]
        st.metric(
            "Goal Difference",
            f"{goal_diff:+.0f}",
            delta="Positive is good!" if goal_diff > 0 else "Work on defense!" if goal_diff < 0 else "Balanced play",
        )

    with col3:
        st.markdown("**⚽ Scoring Stats**")
        st.metric("Goals For", int(player_stats["goals_for"]))
        st.metric("Goals Against", int(player_stats["goals_against"]))
        st.metric("Goals/Match", f"{player_stats['avg_goals_per_match']:.2f}", help="Average goals scored per match")

    st.divider()

    # Enhanced league comparison table
    st.markdown("#### 🏆 League Leaderboard")
    st.markdown("Compare all players' performance in the league.")

    display_stats = stats_df[
        [
            "player_name",
            "matches_played",
            "wins",
            "losses",
            "ties",
            "win_rate",
            "goals_for",
            "goals_against",
            "goal_difference",
        ]
    ].copy()
    display_stats.columns = [
        "Player",
        "Matches",
        "Wins",
        "Losses",
        "Ties",
        "Win Rate (%)",
        "Goals For",
        "Goals Against",
        "Goal Diff",
    ]

    # Sort by win rate and add ranking
    display_stats = display_stats.sort_values("Win Rate (%)", ascending=False)
    display_stats.insert(0, "Rank", range(1, len(display_stats) + 1))

    st.dataframe(
        display_stats,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
            "Player": st.column_config.TextColumn("👤 Player", width="medium"),
            "Win Rate (%)": st.column_config.ProgressColumn(
                "📈 Win Rate (%)", min_value=0, max_value=100, format="%.1f%%"
            ),
        },
        hide_index=True,
    )
