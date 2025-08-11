"""Match history page for Standcup."""

from __future__ import annotations

import pandas as pd
import streamlit as st


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
