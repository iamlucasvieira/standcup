"""Head-to-head analysis page for Standcup."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from standcup.models import StandcupData
from standcup.utils import calculate_head_to_head


def create_head_to_head_chart(player1: str, player2: str, p1_win_rate: float, p2_win_rate: float) -> go.Figure:
    """Create a head-to-head win rate chart."""
    fig = go.Figure(
        data=[
            go.Bar(name=player1, x=[player1], y=[p1_win_rate], marker_color="lightblue"),
            go.Bar(name=player2, x=[player2], y=[p2_win_rate], marker_color="lightcoral"),
        ]
    )

    fig.update_layout(title=f"{player1} vs {player2} - Win Rate (%)", yaxis_title="Win Rate (%)", height=400)

    return fig


def render_head_to_head_page(data: StandcupData) -> None:
    """Render the head-to-head analysis page."""
    st.header("⚔️ Head-to-Head Analysis")

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
