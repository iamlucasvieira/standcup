"""Chart creation functions for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from standcup.models import StandcupData


def create_win_rate_chart(stats_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of win rates."""
    fig = px.bar(
        stats_df.sort_values("win_rate", ascending=True),
        x="win_rate",
        y="player_name",
        orientation="h",
        title="Win Rate by Player (%)",
        labels={"win_rate": "Win Rate (%)", "player_name": "Player"},
        color="win_rate",
        color_continuous_scale="viridis",
    )
    fig.update_layout(height=400)
    return fig


def create_goals_chart(stats_df: pd.DataFrame) -> go.Figure:
    """Create a chart showing goals for vs against."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(name="Goals For", x=stats_df["player_name"], y=stats_df["goals_for"], marker_color="lightgreen")
    )

    fig.add_trace(
        go.Bar(name="Goals Against", x=stats_df["player_name"], y=stats_df["goals_against"], marker_color="lightcoral")
    )

    fig.update_layout(
        title="Goals For vs Goals Against by Player",
        xaxis_title="Player",
        yaxis_title="Goals",
        barmode="group",
        height=400,
    )
    return fig


def create_match_timeline(data: StandcupData) -> go.Figure:
    """Create a timeline of matches."""
    matches_df = data.to_matches_df()

    if matches_df.empty:
        return go.Figure()

    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df = matches_df.sort_values("date")

    fig = px.scatter(
        matches_df,
        x="date",
        y="total_goals",
        color="game_type",
        size="total_goals",
        hover_data=["team1_players", "team2_players", "team1_score", "team2_score"],
        title="Match Timeline - Goals Scored Over Time",
    )

    fig.update_layout(height=400)
    return fig


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
