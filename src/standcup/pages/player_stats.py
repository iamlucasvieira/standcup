"""Player statistics page for Standcup."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _get_win_personality(win_rate: float, matches: int) -> str:
    """Get win rate personality."""
    if win_rate >= 85 and matches >= 10:
        return "🐐 Table Football God"
    elif win_rate >= 75:
        return "👑 League Dominator"
    elif win_rate >= 65:
        return "🔥 Hot Streak"
    elif win_rate >= 55:
        return "⚽ Solid Player"
    elif win_rate >= 45:
        return "📈 Fighting Spirit"
    elif win_rate >= 35:
        return "🌱 Learning Curve"
    else:
        return "💪 Never Give Up"


def _get_goal_personality(goal_diff: float) -> str:
    """Get goal difference personality."""
    if goal_diff >= 50:
        return "🏆 Goal Machine"
    elif goal_diff >= 20:
        return "⚡ Attacking Force"
    elif goal_diff >= 0:
        return "⚖️ Balanced Player"
    elif goal_diff >= -20:
        return "🛡️ Defensive Mind"
    else:
        return "🎯 Room for Growth"


def _get_activity_personality(matches: int) -> str:
    """Get activity level personality."""
    if matches >= 100:
        return "🎆 League Legend"
    elif matches >= 50:
        return "⭐ Regular Champion"
    elif matches >= 20:
        return "🏃 Active Player"
    elif matches >= 10:
        return "🌱 Rising Star"
    else:
        return "🚀 Newcomer"


def get_player_personality(stats: pd.Series) -> dict[str, str]:
    """Generate personality traits based on player stats."""
    win_rate = stats["win_rate"]
    matches = stats["matches_played"]
    goal_diff = stats["goal_difference"]

    return {
        "win_style": _get_win_personality(win_rate, matches),
        "goal_style": _get_goal_personality(goal_diff),
        "activity": _get_activity_personality(matches),
    }


def _render_empty_stats() -> None:
    """Render empty stats message."""
    st.warning("🏆 The Hall of Fame awaits its first legend!")
    st.info(
        "🚀 **Ready to make history?** Every great player started with their first match. Your journey to glory begins now!"
    )


def _create_win_rate_gauge(win_rate: float) -> go.Figure:
    """Create a win rate gauge chart."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=win_rate,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Win Rate %", "font": {"size": 20}},
            delta={"reference": 50},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 70], "color": "yellow"},
                    {"range": [70, 85], "color": "orange"},
                    {"range": [85, 100], "color": "red"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
            },
        )
    )

    fig.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20})

    return fig


def _create_goals_chart(goals_for: int, goals_against: int) -> go.Figure:
    """Create a goals comparison chart."""
    fig = go.Figure(
        data=[
            go.Bar(name="Goals For", x=["Goals"], y=[goals_for], marker_color="#00ff00"),
            go.Bar(name="Goals Against", x=["Goals"], y=[goals_against], marker_color="#ff0000"),
        ]
    )

    fig.update_layout(
        title="Goals For vs Against", height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, showlegend=True
    )

    return fig


def _render_player_header(selected_player: str, player_stats: pd.Series) -> None:
    """Render the player header with key stats."""
    personality = get_player_personality(player_stats)

    # Hero section
    st.markdown(
        f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin: 20px 0;">
        <h1 style="color: white; margin: 0;">🏆 {selected_player}</h1>
        <p style="color: white; font-size: 18px; margin: 10px 0;">{personality["win_style"]} • {personality["goal_style"]} • {personality["activity"]}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def _render_key_metrics(player_stats: pd.Series) -> None:
    """Render key performance metrics in a modern card layout."""
    st.markdown("### 📊 Key Performance Metrics")

    # Create 4 columns for key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="🏆 Win Rate", value=f"{player_stats['win_rate']:.1f}%", delta=f"{player_stats['wins']} wins")

    with col2:
        st.metric(
            label="⚽ Goals For",
            value=int(player_stats["goals_for"]),
            delta=f"{player_stats['avg_goals_per_match']:.1f} per match",
        )

    with col3:
        st.metric(label="🛡️ Goal Difference", value=f"{player_stats['goal_difference']:+.0f}", delta="Net advantage")

    with col4:
        st.metric(label="🎮 Matches Played", value=int(player_stats["matches_played"]), delta="Total experience")


def _render_detailed_stats(player_stats: pd.Series) -> None:
    """Render detailed statistics with charts."""
    st.markdown("### 📈 Detailed Performance Analysis")

    # Two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Win Rate Gauge")
        win_rate_gauge = _create_win_rate_gauge(player_stats["win_rate"])
        st.plotly_chart(win_rate_gauge, use_container_width=True)

    with col2:
        st.markdown("#### ⚽ Goals Analysis")
        goals_chart = _create_goals_chart(int(player_stats["goals_for"]), int(player_stats["goals_against"]))
        st.plotly_chart(goals_chart, use_container_width=True)

    # Additional metrics below charts
    st.markdown("#### 📋 Match Breakdown")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Wins:** {int(player_stats['wins'])}")

    with col2:
        st.error(f"**Losses:** {int(player_stats['losses'])}")

    with col3:
        st.warning(f"**Goals Against:** {int(player_stats['goals_against'])}")


def _get_achievement_badges(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get achievement badges based on performance."""
    achievements = []

    # Win rate achievements
    if player_stats["win_rate"] >= 80:
        achievements.append(("👑 Elite Winner", "80%+ win rate", "success"))
    elif player_stats["win_rate"] >= 65:
        achievements.append(("🔥 Strong Competitor", "65%+ win rate", "info"))

    # Goal achievements
    if player_stats["goal_difference"] >= 20:
        achievements.append(("⚡ Goal Machine", "20+ goal difference", "success"))
    elif player_stats["goal_difference"] >= 0:
        achievements.append(("⚖️ Balanced Player", "Positive goal difference", "info"))

    # Activity achievements
    if player_stats["matches_played"] >= 50:
        achievements.append(("⭐ League Veteran", "50+ matches", "warning"))
    elif player_stats["matches_played"] >= 20:
        achievements.append(("🏃 Active Player", "20+ matches", "info"))

    return achievements


def _render_achievement_badges(player_stats: pd.Series) -> None:
    """Render achievement badges based on performance."""
    st.markdown("### 🏅 Achievement Badges")

    achievements = _get_achievement_badges(player_stats)

    if not achievements:
        st.info("🚀 **Rising Star!** Keep playing to unlock achievements!")
    else:
        cols = st.columns(len(achievements))
        for i, (title, desc, color) in enumerate(achievements):
            with cols[i]:
                if color == "success":
                    st.success(f"**{title}**\n{desc}")
                elif color == "warning":
                    st.warning(f"**{title}**\n{desc}")
                else:
                    st.info(f"**{title}**\n{desc}")


def _render_leaderboard(stats_df: pd.DataFrame) -> None:
    """Render the leaderboard section with modern styling."""
    st.markdown("### 🏆 League Leaderboard")
    st.markdown("🌟 **Champions, legends, and rising stars - see where everyone stands!**")

    # Filter and prepare data
    display_stats = stats_df[
        [
            "player_name",
            "matches_played",
            "wins",
            "losses",
            "win_rate",
            "goals_for",
            "goals_against",
            "goal_difference",
        ]
    ].copy()

    # Sort by win rate and add ranking
    display_stats = display_stats.sort_values("win_rate", ascending=False)
    display_stats.insert(0, "Rank", range(1, len(display_stats) + 1))

    # Add achievement status
    achievements = []
    for _, row in display_stats.iterrows():
        if row["Rank"] == 1 and row["matches_played"] >= 5:
            achievements.append("👑 Champion")
        elif row["Rank"] <= 3 and row["matches_played"] >= 5:
            achievements.append("🥉 Podium")
        elif row["win_rate"] >= 70:
            achievements.append("🔥 Elite")
        elif row["matches_played"] >= 50:
            achievements.append("⭐ Veteran")
        elif row["matches_played"] >= 20:
            achievements.append("🏃 Active")
        elif row["matches_played"] >= 10:
            achievements.append("🌱 Rising")
        else:
            achievements.append("🚀 Rookie")

    display_stats.insert(1, "Status", achievements)

    # Display with modern styling
    st.dataframe(
        display_stats,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
            "Status": st.column_config.TextColumn("🎆 Status", width="medium"),
            "player_name": st.column_config.TextColumn("👤 Player", width="medium"),
            "win_rate": st.column_config.ProgressColumn("📈 Win Rate (%)", min_value=0, max_value=100, format="%.1f%%"),
            "goal_difference": st.column_config.NumberColumn("⚽ Goal Diff", width="small"),
        },
        hide_index=True,
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

    # Render all sections
    _render_player_header(selected_player, player_stats)
    _render_key_metrics(player_stats)
    _render_detailed_stats(player_stats)
    _render_achievement_badges(player_stats)

    st.divider()
    _render_leaderboard(stats_df)
