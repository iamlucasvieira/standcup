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


def create_cumulative_wins_chart(data: StandcupData) -> go.Figure:
    """Create a cumulative wins by match chart showing leaderboard progression."""
    player_matches = data.to_player_match_df()

    if player_matches.empty:
        return go.Figure()

    # Get player names mapping
    players_dict = {p.id: p.name for p in data.players}

    # Convert date to datetime and strip time for even distribution
    player_matches = player_matches.copy()
    player_matches["date"] = player_matches["date"].apply(lambda x: pd.to_datetime(x).date())

    # Sort by date to get chronological order
    player_matches = player_matches.sort_values("date")

    # Calculate cumulative wins for each player
    cumulative_data = []

    for player_id in player_matches["player_id"].unique():
        player_data = player_matches[player_matches["player_id"] == player_id].copy()
        player_data["cumulative_wins"] = player_data["won"].cumsum()

        # Add player name
        player_data["player_name"] = players_dict.get(player_id, player_id)

        cumulative_data.append(player_data)

    # Combine all player data
    all_data = pd.concat(cumulative_data, ignore_index=True)

    # Create the plot
    fig = go.Figure()

    # Add a line for each player
    for player_id in all_data["player_id"].unique():
        player_data = all_data[all_data["player_id"] == player_id]
        player_name = players_dict.get(player_id, player_id)

        fig.add_trace(
            go.Scatter(
                x=player_data["date"],
                y=player_data["cumulative_wins"],
                mode="lines+markers",
                name=player_name,
                line={"width": 3},
                marker={"size": 6},
                hovertemplate=f"<b>{player_name}</b><br>"
                + "Date: %{x}<br>"
                + "Cumulative Wins: %{y}<br>"
                + "<extra></extra>",
            )
        )

    fig.update_layout(
        title="Cumulative Wins by Date - Leaderboard Progression",
        xaxis_title="Date",
        yaxis_title="Cumulative Wins",
        height=500,
        hovermode="x unified",
        legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
    )

    return fig
