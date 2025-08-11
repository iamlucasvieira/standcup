"""Page components for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from standcup.charts import (
    create_cumulative_wins_chart,
    create_goals_chart,
    create_head_to_head_chart,
    create_match_timeline,
    create_win_rate_chart,
)
from standcup.models import StandcupData
from standcup.utils import calculate_head_to_head


def render_overview_page(data: StandcupData, stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> None:
    """Render the overview/dashboard page."""
    st.header("📊 Dashboard Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Players", len(data.players))

    with col2:
        st.metric("Total Matches", len(data.matches))

    with col3:
        if not matches_df.empty:
            avg_goals = matches_df["total_goals"].mean()
            st.metric("Avg Goals/Match", f"{avg_goals:.1f}")

    with col4:
        if not stats_df.empty:
            top_player = stats_df.loc[stats_df["win_rate"].idxmax(), "player_name"]
            st.metric("Top Win Rate", top_player)

    # Charts
    if not stats_df.empty:
        # Leaderboard progression chart - full width
        st.plotly_chart(create_cumulative_wins_chart(data), use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_win_rate_chart(stats_df), use_container_width=True)

        with col2:
            st.plotly_chart(create_goals_chart(stats_df), use_container_width=True)

        st.plotly_chart(create_match_timeline(data), use_container_width=True)


def render_player_stats_page(stats_df: pd.DataFrame) -> None:
    """Render the player statistics page."""
    st.header("👥 Player Statistics")

    if stats_df.empty:
        st.warning("No player statistics available.")
        return

    # Player selection
    selected_player = st.selectbox(
        "Select a player for detailed stats:", options=stats_df["player_name"].tolist(), index=0
    )

    player_stats = stats_df[stats_df["player_name"] == selected_player].iloc[0]

    # Display detailed stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Matches Played", int(player_stats["matches_played"]))
        st.metric("Wins", int(player_stats["wins"]))
        st.metric("Win Rate", f"{player_stats['win_rate']:.1f}%")

    with col2:
        st.metric("Losses", int(player_stats["losses"]))
        st.metric("Ties", int(player_stats["ties"]))
        st.metric("Goal Difference", f"{player_stats['goal_difference']:+.0f}")

    with col3:
        st.metric("Goals For", int(player_stats["goals_for"]))
        st.metric("Goals Against", int(player_stats["goals_against"]))
        st.metric("Avg Goals/Match", f"{player_stats['avg_goals_per_match']:.2f}")

    # Overall stats table
    st.subheader("All Players Comparison")
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

    st.dataframe(display_stats.sort_values("Win Rate (%)", ascending=False), use_container_width=True)


def render_match_history_page(matches_df: pd.DataFrame) -> None:
    """Render the match history page."""
    st.header("🏆 Match History")

    if matches_df.empty:
        st.warning("No matches available.")
        return

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        game_types = ["All", *matches_df["game_type"].unique().tolist()]
        selected_type = st.selectbox("Game Type", game_types)

    with col2:
        match_types = ["All", "Singles Only", "Doubles Only"]
        selected_match_type = st.selectbox("Match Type", match_types)

    # Filter data
    filtered_df = matches_df.copy()

    if selected_type != "All":
        filtered_df = filtered_df[filtered_df["game_type"] == selected_type]

    if selected_match_type == "Singles Only":
        filtered_df = filtered_df[filtered_df["is_singles"]]
    elif selected_match_type == "Doubles Only":
        filtered_df = filtered_df[~filtered_df["is_singles"]]

    # Display matches
    st.subheader(f"Matches ({len(filtered_df)} total)")

    display_matches = filtered_df[
        [
            "date",
            "team1_players",
            "team2_players",
            "team1_score",
            "team2_score",
            "game_type",
            "duration_minutes",
        ]
    ].copy()
    display_matches.loc[:, "date"] = display_matches["date"].apply(
        lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M")
    )
    display_matches.columns = ["Date", "Team 1", "Team 2", "Score 1", "Score 2", "Type", "Duration (min)"]

    st.dataframe(display_matches.sort_values("Date", ascending=False), use_container_width=True)


def render_head_to_head_page(data: StandcupData) -> None:
    """Render the head-to-head analysis page."""
    st.header("🆚 Head-to-Head Analysis")

    if len(data.players) < 2:
        st.warning("Need at least 2 players for head-to-head analysis.")
        return

    # Player selection
    col1, col2 = st.columns(2)

    player_names = [p.name for p in data.players]

    with col1:
        player1 = st.selectbox("Player 1", player_names, index=0)

    with col2:
        player2_options = [p for p in player_names if p != player1]
        player2 = st.selectbox("Player 2", player2_options, index=0 if player2_options else None)

    if not (player1 and player2 and player1 != player2):
        return

    # Get player IDs
    player1_id = next(p.id for p in data.players if p.name == player1)
    player2_id = next(p.id for p in data.players if p.name == player2)

    # Calculate head-to-head stats
    h2h_stats = calculate_head_to_head(data, player1_id, player2_id)

    if h2h_stats["total_matches"] == 0:
        st.info(f"{player1} and {player2} haven't played against each other yet.")
        return

    # Display results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(f"{player1} Wins", h2h_stats["p1_wins"])

    with col2:
        st.metric("Ties", h2h_stats["ties"])

    with col3:
        st.metric(f"{player2} Wins", h2h_stats["p2_wins"])

    # Win percentage chart
    if h2h_stats["total_matches"] > 0:
        p1_win_rate = (h2h_stats["p1_wins"] / h2h_stats["total_matches"]) * 100
        p2_win_rate = (h2h_stats["p2_wins"] / h2h_stats["total_matches"]) * 100

        st.subheader("Head-to-Head Win Rates")
        st.plotly_chart(create_head_to_head_chart(player1, player2, p1_win_rate, p2_win_rate), use_container_width=True)
