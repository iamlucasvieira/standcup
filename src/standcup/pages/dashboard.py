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


def create_league_activity_chart(data: StandcupData) -> go.Figure:
    """Create a chart showing league activity and match competitiveness over time."""
    matches_df = data.to_matches_df()

    if matches_df.empty:
        return go.Figure()

    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df = matches_df.sort_values("date")

    # Calculate rolling averages for trends
    matches_df["goal_difference"] = abs(matches_df["team1_score"] - matches_df["team2_score"])

    # Group by week to show trends
    matches_df["week"] = matches_df["date"].dt.to_period("W").dt.start_time
    weekly_stats = (
        matches_df.groupby("week").agg({"total_goals": "mean", "goal_difference": "mean", "match_id": "count"}).round(2)
    )

    # Create subplot with secondary y-axis
    fig = go.Figure()

    # Match frequency (bar chart)
    fig.add_trace(
        go.Bar(
            x=weekly_stats.index,
            y=weekly_stats["match_id"],
            name="Matches per Week",
            marker_color="lightblue",
            opacity=0.7,
            yaxis="y2",
        )
    )

    # Average goals per match (line)
    fig.add_trace(
        go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats["total_goals"],
            mode="lines+markers",
            name="Avg Goals/Match",
            line={"color": "green", "width": 3},
            marker={"size": 8},
        )
    )

    # Average goal difference (competitiveness indicator)
    fig.add_trace(
        go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats["goal_difference"],
            mode="lines+markers",
            name="Avg Goal Difference",
            line={"color": "orange", "width": 3, "dash": "dot"},
            marker={"size": 6},
        )
    )

    fig.update_layout(
        title="League Activity & Match Trends Over Time",
        xaxis_title="Date",
        yaxis={"title": "Goals", "side": "left"},
        yaxis2={"title": "Number of Matches", "side": "right", "overlaying": "y"},
        height=400,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )

    return fig


def create_win_rate_over_time_chart(data: StandcupData) -> go.Figure:
    """Create a chart showing win rate progression over time for each player."""
    player_matches = data.to_player_match_df()

    if player_matches.empty:
        return go.Figure()

    # Get player names mapping
    players_dict = {p.id: p.name for p in data.players}

    # Convert date to datetime and extract date only (no time)
    player_matches = player_matches.copy()
    player_matches["date"] = pd.to_datetime(player_matches["date"]).dt.date

    # Sort by date to get chronological order
    player_matches = player_matches.sort_values("date")

    fig = go.Figure()

    # Calculate rolling win rate for each player
    for player_id in player_matches["player_id"].unique():
        player_data = player_matches[player_matches["player_id"] == player_id].copy()
        player_name = players_dict.get(player_id, player_id)

        # Calculate cumulative win rate
        player_data["cumulative_wins"] = player_data["won"].cumsum()
        player_data["cumulative_matches"] = range(1, len(player_data) + 1)
        player_data["win_rate"] = (player_data["cumulative_wins"] / player_data["cumulative_matches"] * 100).round(1)

        # Group by date and take the last (end-of-day) win rate for each date
        # This eliminates multiple points on the same day
        daily_win_rates = (
            player_data.groupby("date")
            .agg({
                "win_rate": "last",  # End-of-day win rate
                "cumulative_matches": "last",  # Total matches by end of day
            })
            .reset_index()
        )

        fig.add_trace(
            go.Scatter(
                x=daily_win_rates["date"],
                y=daily_win_rates["win_rate"],
                mode="lines+markers",
                name=player_name,
                line={"width": 3},
                marker={"size": 6},
                hovertemplate=f"<b>{player_name}</b><br>" + "Win Rate: %{y:.1f}%<br>" + "<extra></extra>",
            )
        )

    fig.update_layout(
        title="Win Rate Progression Over Time",
        xaxis_title="Date",
        yaxis_title="Win Rate (%)",
        height=500,
        hovermode="x unified",
        legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
        yaxis={"range": [0, 100]},  # Fix y-axis to 0-100% for better comparison
    )

    return fig


def get_league_status_message(stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> tuple[str, str]:
    """Generate dynamic status message based on league activity."""
    if stats_df.empty or matches_df.empty:
        return (
            "🚀 Ready to Kick Off!",
            "Your table football adventure is about to begin! Start playing matches to see epic stats and rivalries unfold.",
        )

    total_matches = len(matches_df)
    avg_goals = matches_df["total_goals"].mean() if not matches_df.empty else 0
    top_win_rate = stats_df["win_rate"].max()

    if total_matches < 10:
        return (
            "🌱 Growing League",
            f"Just getting started with {total_matches} matches! The competition is heating up...",
        )
    elif total_matches < 50:
        return (
            "⚽ Active League",
            f"{total_matches} matches played! The battle for supremacy continues with an average of {avg_goals:.1f} goals per match!",
        )
    elif avg_goals > 8:
        return (
            "🔥 High-Octane League",
            f"This league is on fire! {avg_goals:.1f} goals per match - pure attacking football at its finest!",
        )
    elif top_win_rate > 80:
        return (
            "👑 Dominated League",
            f"We have a champion! Someone's absolutely crushing it with {top_win_rate:.1f}% win rate!",
        )
    else:
        return (
            "⚔️ Competitive League",
            f"Epic battles across {total_matches} matches! Every game matters in this tight competition!",
        )


def get_top_player_personality(stats_df: pd.DataFrame) -> str:
    """Generate personality text for top player metric."""
    if stats_df.empty:
        return "No champion yet"

    top_idx = stats_df["win_rate"].idxmax()
    win_rate = stats_df.loc[top_idx, "win_rate"]
    matches = stats_df.loc[top_idx, "matches_played"]

    if win_rate >= 90 and matches >= 10:
        return "🐐 Legendary!"
    elif win_rate >= 80:
        return "👑 Dominating!"
    elif win_rate >= 70:
        return "🔥 On fire!"
    elif win_rate >= 60:
        return "⭐ Solid player!"
    else:
        return "📈 Improving!"


def render_overview_page(data: StandcupData, stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> None:
    """Render the overview/dashboard page."""
    status_title, status_msg = get_league_status_message(stats_df, matches_df)

    st.markdown(f"### {status_title}")
    st.markdown(status_msg)

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
            if avg_goals >= 9:
                goal_msg = "🔥 Explosive!"
            elif avg_goals >= 8:
                goal_msg = "⚡ High-scoring!"
            elif avg_goals >= 7:
                goal_msg = "⚽ Action-packed!"
            elif avg_goals >= 6:
                goal_msg = "🎯 Balanced!"
            else:
                goal_msg = "🛡️ Defensive!"
            st.metric(
                label="🥅 Goals/Match", value=f"{avg_goals:.1f}", delta=goal_msg, help="How explosive are your matches?"
            )
        else:
            st.metric("🥅 Goals/Match", "0.0")

    with col4:
        if not stats_df.empty:
            top_player_idx = stats_df["win_rate"].idxmax()
            top_player = stats_df.loc[top_player_idx, "player_name"]
            top_win_rate = stats_df.loc[top_player_idx, "win_rate"]
            personality = get_top_player_personality(stats_df)
            st.metric(
                label="🌟 League Champion",
                value=top_player,
                delta=f"{top_win_rate:.1f}% • {personality}",
                help="The player currently ruling the league!",
            )
        else:
            st.metric("🌟 League Champion", "Crown awaits...")

    st.divider()

    # Charts section with improved presentation
    if not stats_df.empty:
        st.markdown("#### 📈 Performance Analytics")

        # Win rate progression chart - full width
        st.markdown("**Win Rate Progression Over Time**")
        st.plotly_chart(create_win_rate_over_time_chart(data), use_container_width=True)

        # Side-by-side performance charts
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**Player Win Rates**")
            st.plotly_chart(create_win_rate_chart(stats_df), use_container_width=True)

        with col2:
            st.markdown("**Goal Statistics**")
            st.plotly_chart(create_goals_chart(stats_df), use_container_width=True)

        # League activity and trends
        st.markdown("**League Activity & Match Trends**")
        st.plotly_chart(create_league_activity_chart(data), use_container_width=True)
    else:
        st.info("🎮 Ready Player One?")
        st.markdown("""🏆 **Your table football journey starts here!**

Get ready for epic matches, legendary comebacks, and statistical glory. Every champion started with their first game - what are you waiting for?""")

        col1, col2 = st.columns(2)
        with col1:
            st.success("💪 **Pro Tips:**\n- Practice your shots!\n- Master the defense!\n- Study your opponents!")
        with col2:
            st.info("🎯 **Coming Soon:**\n- Epic win streaks\n- Legendary rivalries\n- Championship moments")
