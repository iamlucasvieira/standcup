"""Streamlit app for Standcup - Table Football Tracker."""

from __future__ import annotations

import streamlit as st
from pages import (
    render_head_to_head_page,
    render_leaderboard_page,
    render_match_history_page,
    render_match_maker_page,
    render_overview_page,
    render_player_stats_page,
)
from utils import calculate_player_stats, load_data


def main() -> None:
    """Main Streamlit app."""
    st.set_page_config(
        page_title="⚽ Standcup - Table Football Tracker",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Modern navigation
    pages = [
        st.Page(render_dashboard_wrapper, title="Dashboard", icon="🏠"),
        st.Page(render_leaderboard_wrapper, title="Leaderboard", icon="🏆"),
        st.Page(render_player_stats_wrapper, title="Player Stats", icon="👥"),
        st.Page(render_match_history_wrapper, title="Match History", icon="📋"),
        st.Page(render_head_to_head_wrapper, title="Head-to-Head", icon="⚔️"),
        st.Page(render_match_maker_wrapper, title="Match Maker", icon="🎯"),
    ]

    pg = st.navigation(pages)

    # App header with improved styling
    st.markdown(
        """
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); border-radius: 10px;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">⚽ Standcup</h1>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 300;">Table Football Analytics & Match Making</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    pg.run()


def render_dashboard_wrapper():
    """Wrapper for dashboard page."""
    data = load_data()
    if not _validate_data(data):
        return
    stats_df = calculate_player_stats(data)
    matches_df = data.to_matches_df()
    render_overview_page(data, stats_df, matches_df)


def render_leaderboard_wrapper():
    """Wrapper for leaderboard page."""
    data = load_data()
    if not _validate_data(data):
        return
    stats_df = calculate_player_stats(data)
    render_leaderboard_page(stats_df)


def render_player_stats_wrapper():
    """Wrapper for player stats page."""
    data = load_data()
    if not _validate_data(data):
        return
    stats_df = calculate_player_stats(data)
    render_player_stats_page(stats_df)


def render_match_history_wrapper():
    """Wrapper for match history page."""
    data = load_data()
    if not _validate_data(data):
        return
    matches_df = data.to_matches_df()
    render_match_history_page(matches_df)


def render_head_to_head_wrapper():
    """Wrapper for head-to-head page."""
    data = load_data()
    if not _validate_data(data):
        return
    render_head_to_head_page(data)


def render_match_maker_wrapper():
    """Wrapper for match maker page."""
    data = load_data()
    if not _validate_data(data):
        return
    stats_df = calculate_player_stats(data)
    render_match_maker_page(data, stats_df)


def _validate_data(data) -> bool:
    """Validate loaded data and show appropriate warnings."""
    if not data.players:
        st.error("🚫 No players found in the data!")
        st.info("💡 Please add players to your data source to get started.")
        return False

    if not data.matches:
        st.warning("⚠️ No matches found in the data!")
        st.info("💡 Add some match results to see statistics and analytics.")
        return False

    return True


if __name__ == "__main__":
    main()
