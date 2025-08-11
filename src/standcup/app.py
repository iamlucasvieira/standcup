"""Streamlit app for Standcup - Table Football Tracker."""

from __future__ import annotations

import streamlit as st

from standcup.pages import (
    render_head_to_head_page,
    render_match_history_page,
    render_match_maker_page,
    render_overview_page,
    render_player_stats_page,
)
from standcup.utils import calculate_player_stats, load_data


def main() -> None:
    """Main Streamlit app."""
    st.set_page_config(
        page_title="⚽ Standcup - Table Football Tracker",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.title("⚽ Standcup - Table Football Tracker")
    st.markdown("Welcome to your table football statistics dashboard!")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page", ["Overview", "Player Stats", "Match History", "Head-to-Head", "Match Maker"]
    )

    # Load data
    try:
        data = load_data()

        if not data.players:
            st.warning("No players found in the data!")
            return

        if not data.matches:
            st.warning("No matches found in the data!")
            return

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Calculate stats
    stats_df = calculate_player_stats(data)
    matches_df = data.to_matches_df()

    # Route to appropriate page
    if page == "Overview":
        render_overview_page(data, stats_df, matches_df)
    elif page == "Player Stats":
        render_player_stats_page(stats_df)
    elif page == "Match History":
        render_match_history_page(matches_df)
    elif page == "Head-to-Head":
        render_head_to_head_page(data)
    elif page == "Match Maker":
        render_match_maker_page(data, stats_df)


if __name__ == "__main__":
    main()
