"""Dashboard/Overview page for Standcup."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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


def render_overview_page(data: StandcupData, stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> None:
    """Render the overview/dashboard page."""
    st.markdown("### 📊 League Overview")
    st.markdown("Get insights into your table football league performance and statistics.")

    st.divider()

    # Key metrics with enhanced styling
    st.markdown("#### 🏆 Key Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_players = len(data.players)
        st.metric(label="👥 Total Players", value=total_players, help="Number of active players in your league")

    with col2:
        total_matches = len(data.matches)
        st.metric(label="⚽ Total Matches", value=total_matches, help="Total matches played across all game types")

    with col3:
        if not matches_df.empty:
            avg_goals = matches_df["total_goals"].mean()
            st.metric(label="🥅 Avg Goals/Match", value=f"{avg_goals:.1f}", help="Average total goals scored per match")
        else:
            st.metric("🥅 Avg Goals/Match", "0.0")

    with col4:
        if not stats_df.empty:
            top_player_idx = stats_df["win_rate"].idxmax()
            top_player = stats_df.loc[top_player_idx, "player_name"]
            top_win_rate = stats_df.loc[top_player_idx, "win_rate"]
            st.metric(
                label="🌟 Top Player",
                value=top_player,
                delta=f"{top_win_rate:.1f}% win rate",
                help="Player with the highest win rate",
            )
        else:
            st.metric("🌟 Top Player", "No data")

    st.divider()

    # Charts section with improved presentation
    if not stats_df.empty:
        st.markdown("#### 📈 Performance Analytics")

        # Leaderboard progression chart - full width
        st.markdown("**Win Progression Over Time**")
        st.plotly_chart(create_cumulative_wins_chart(data), use_container_width=True)

        # Side-by-side performance charts
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**Player Win Rates**")
            st.plotly_chart(create_win_rate_chart(stats_df), use_container_width=True)

        with col2:
            st.markdown("**Goal Statistics**")
            st.plotly_chart(create_goals_chart(stats_df), use_container_width=True)

        # Match activity timeline
        st.markdown("**Match Activity Timeline**")
        st.plotly_chart(create_match_timeline(data), use_container_width=True)
    else:
        st.info("📊 Charts will appear here once you have match data!")
        st.markdown("Start playing matches to see beautiful analytics and insights.")
