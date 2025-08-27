"""Dashboard/Overview page for Standcup."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from standcup.models import MatchType, StandcupData
from standcup.utils import calculate_player_stats
from standcup.win_rate_methods import WinRateMethod, calculate_win_rate, get_method_display_name


def create_win_rate_chart(
    stats_df: pd.DataFrame,
    match_type_filter: str | None = None,
    win_rate_method: WinRateMethod = WinRateMethod.WILSON_CENTER,
) -> go.Figure:
    """Create a bar chart of win rates."""
    method_display = get_method_display_name(win_rate_method)
    title_suffix = "" if match_type_filter is None else f" ({match_type_filter})"
    fig = px.bar(
        stats_df.sort_values("win_rate", ascending=True),
        x="win_rate",
        y="player_name",
        orientation="h",
        title=f"{method_display} by Player{title_suffix}",
        labels={"win_rate": f"{method_display} (%)", "player_name": "Player"},
        color="win_rate",
        color_continuous_scale="viridis",
    )
    fig.update_layout(height=400)
    return fig


def create_goals_chart(stats_df: pd.DataFrame, match_type_filter: str | None = None) -> go.Figure:
    """Create a chart showing goals for vs against."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(name="Goals For", x=stats_df["player_name"], y=stats_df["goals_for"], marker_color="lightgreen")
    )

    fig.add_trace(
        go.Bar(name="Goals Against", x=stats_df["player_name"], y=stats_df["goals_against"], marker_color="lightcoral")
    )

    title_suffix = "" if match_type_filter is None else f" ({match_type_filter})"
    fig.update_layout(
        title=f"Goals For vs Goals Against by Player{title_suffix}",
        xaxis_title="Player",
        yaxis_title="Goals",
        barmode="group",
        height=400,
    )
    return fig


def create_league_activity_chart(data: StandcupData, match_type_filter: str | None = None) -> go.Figure:
    """Create a chart showing league activity and match competitiveness over time."""
    matches_df = data.to_matches_df()

    if matches_df.empty:
        return go.Figure()

    # Apply match type filter using match_type column directly
    if match_type_filter is not None:
        matches_df = matches_df[matches_df["match_type"] == match_type_filter]
    # None requires no filtering

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

    title_suffix = "" if match_type_filter is None else f" ({match_type_filter})"
    fig.update_layout(
        title=f"League Activity & Match Trends Over Time{title_suffix}",
        xaxis_title="Date",
        yaxis={"title": "Goals", "side": "left"},
        yaxis2={"title": "Number of Matches", "side": "right", "overlaying": "y"},
        height=400,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )

    return fig


def create_win_rate_over_time_chart(
    data: StandcupData,
    match_type_filter: str | None = None,
    win_rate_method: WinRateMethod = WinRateMethod.WILSON_CENTER,
) -> go.Figure:
    """Create a chart showing win rate progression over time for each player."""
    player_matches = data.to_player_match_df()

    if player_matches.empty:
        return go.Figure()

    # Apply match type filter using match_type column directly
    if match_type_filter is not None:
        player_matches = player_matches[player_matches["match_type"] == match_type_filter]

    if player_matches.empty:
        return go.Figure()

    # Get player names mapping
    players_dict = {p.id: p.name for p in data.players}

    # Convert date to datetime and extract date only (no time)
    player_matches = player_matches.copy()
    player_matches["date"] = pd.to_datetime(player_matches["date"])

    # Sort by date to get chronological order
    player_matches = player_matches.sort_values("date")

    fig = go.Figure()

    # Get method display name for titles and hover text
    method_display = get_method_display_name(win_rate_method)

    # Calculate rolling win rate for each player
    for player_id in player_matches["player_id"].unique():
        player_data = player_matches[player_matches["player_id"] == player_id].copy()
        player_name = players_dict.get(player_id, player_id)

        # Calculate cumulative win rate for progression tracking
        player_data["cumulative_wins"] = player_data["won"].cumsum()
        player_data["cumulative_matches"] = range(1, len(player_data) + 1)
        player_data["win_rate"] = player_data.apply(
            lambda row: calculate_win_rate(
                int(row["cumulative_wins"]), int(row["cumulative_matches"]), win_rate_method
            ),
            axis=1,
        ).round(1)

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

    # Create dynamic title based on method and filter
    title_suffix = "" if match_type_filter is None else f" ({match_type_filter})"
    fig.update_layout(
        title=f"{method_display} Progression Over Time{title_suffix}",
        xaxis_title="Date",
        yaxis_title=f"{method_display} (%)",
        height=500,
        hovermode="x unified",
        legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
        yaxis={"range": [0, 100]},  # Fix y-axis to 0-100% for better comparison
    )

    return fig


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
    # Filters section
    col1, col2, *_ = st.columns(4)

    with col1:
        # Match type filter
        filter_options = ["All", MatchType.ONE_V_ONE, MatchType.TWO_V_TWO]
        selected_filter = st.segmented_control(
            "📊 **Match Type Filter**",
            filter_options,
            help="Filter statistics and charts by match type",
            default=MatchType.TWO_V_TWO,
        )

    with col2:
        # Win rate method filter
        win_rate_options = list(WinRateMethod)
        selected_win_rate_method = st.selectbox(
            "🧮 **Win Rate Method**",
            win_rate_options,
            index=win_rate_options.index(WinRateMethod.WILSON_CENTER),
            format_func=get_method_display_name,
            help="Choose how win rates are calculated. Different methods handle small sample sizes differently.",
        )

    # Convert "All" to None for internal use
    match_type_filter = None if selected_filter == "All" else selected_filter

    # Recalculate stats based on filters
    filtered_stats_df = calculate_player_stats(data, match_type_filter, selected_win_rate_method)

    # Filter matches DataFrame using match_type column directly
    filtered_matches_df = matches_df.copy()
    if match_type_filter is not None:
        filtered_matches_df = matches_df[matches_df["match_type"] == match_type_filter]

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
        if not filtered_matches_df.empty:
            avg_goals = filtered_matches_df["total_goals"].mean()
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
        if not filtered_stats_df.empty:
            top_player_idx = filtered_stats_df["win_rate"].idxmax()
            top_player = filtered_stats_df.loc[top_player_idx, "player_name"]
            top_win_rate = filtered_stats_df.loc[top_player_idx, "win_rate"]
            personality = get_top_player_personality(filtered_stats_df)
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
    if not filtered_stats_df.empty:
        st.markdown("#### 📈 Performance Analytics")

        # Leaderboard chart - full width (most important)
        st.markdown("**🏆 Player Leaderboard**")
        st.plotly_chart(
            create_win_rate_chart(filtered_stats_df, match_type_filter, selected_win_rate_method), width="stretch"
        )

        # Performance over time chart - full width
        st.markdown("**📈 Performance Over Time**")
        st.plotly_chart(
            create_win_rate_over_time_chart(data, match_type_filter, selected_win_rate_method), width="stretch"
        )

        # Side-by-side secondary charts
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**⚽ Goal Statistics**")
            st.plotly_chart(create_goals_chart(filtered_stats_df, match_type_filter), width="stretch")

        with col2:
            st.markdown("**📊 League Activity & Trends**")
            st.plotly_chart(create_league_activity_chart(data, match_type_filter), width="stretch")
    else:
        st.info("🎮 Ready Player One?")
        st.markdown("""🏆 **Your table football journey starts here!**

Get ready for epic matches, legendary comebacks, and statistical glory. Every champion started with their first game - what are you waiting for?""")

        col1, col2 = st.columns(2)
        with col1:
            st.success("💪 **Pro Tips:**\n- Practice your shots!\n- Master the defense!\n- Study your opponents!")
        with col2:
            st.info("🎯 **Coming Soon:**\n- Epic win streaks\n- Legendary rivalries\n- Championship moments")
