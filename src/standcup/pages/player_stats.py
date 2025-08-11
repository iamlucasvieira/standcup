"""Player statistics page for Standcup."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from ..achievements import render_achievement_badges
from ..player_insights import render_player_insights
from ..visualizations import render_detailed_stats, render_key_metrics, render_player_header

if TYPE_CHECKING:
    import pandas as pd


def _render_empty_stats() -> None:
    """Render empty stats message."""
    st.warning("🏆 The Hall of Fame awaits its first legend!")
    st.info(
        "🚀 **Ready to make history?** Every great player started with their first match. Your journey to glory begins now!"
    )


def render_player_stats_page(stats_df: pd.DataFrame) -> None:
    """Render the modernized player statistics page."""
    st.markdown("## 🏆 Player Hall of Fame")
    st.markdown(
        "🎯 **Discover the legends, rising stars, and comeback stories of your league!** Every player has their unique style - let's find yours."
    )

    if stats_df.empty:
        _render_empty_stats()
        return

    # Player selection with modern styling
    st.markdown("### 🔍 Player Analysis")
    selected_player = st.selectbox(
        "Choose a player to analyze:",
        options=stats_df["player_name"].tolist(),
        index=0,
        help="Select any player to see their detailed performance metrics",
        key="player_selector",
    )

    player_stats = stats_df[stats_df["player_name"] == selected_player].iloc[0]

    # Render all sections using the modular components
    render_player_header(selected_player, player_stats)
    render_key_metrics(player_stats)
    render_detailed_stats(player_stats)
    render_achievement_badges(player_stats)
    render_player_insights(player_stats, stats_df)
