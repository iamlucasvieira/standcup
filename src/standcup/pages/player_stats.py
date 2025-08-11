"""Player statistics page for Standcup."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _get_win_personality_tier(win_rate: float, matches: int) -> str:
    """Get win rate personality tier based on win rate and matches."""
    # Define tiers with their conditions
    tiers = [
        (95, 15, "🐐 Table Football Deity"),
        (90, 10, "🐐 Table Football God"),
        (85, 10, "👑 Legendary Champion"),
        (80, 15, "👑 League Dominator"),
        (75, 20, "🔥 Elite Performer"),
        (70, 25, "🔥 Hot Streak"),
        (65, 30, "🔥 Strong Competitor"),
        (60, 35, "⚽ Solid Player"),
        (55, 40, "📈 Fighting Spirit"),
        (50, 45, "⚖️ Balanced Competitor"),
        (45, 50, "📈 Determined Fighter"),
        (40, 55, "🌱 Learning Curve"),
        (35, 60, "💪 Persistent Spirit"),
        (30, 65, "🔄 Improvement Seeker"),
    ]

    # Find the first tier that matches
    for min_win_rate, min_matches, personality in tiers:
        if win_rate >= min_win_rate and matches >= min_matches:
            return personality

    return "💪 Never Give Up"


def _get_win_personality(win_rate: float, matches: int) -> str:
    """Get win rate personality."""
    return _get_win_personality_tier(win_rate, matches)


def _get_goal_personality_tier(goal_diff: float) -> str:
    """Get goal difference personality tier."""
    # Define tiers with their thresholds
    tiers = [
        (100, "🏆 Goal Scoring Legend"),
        (75, "🏆 Goal Machine Pro"),
        (50, "🏆 Goal Machine"),
        (30, "⚡ Attacking Force"),
        (20, "⚡ Sharp Shooter"),
        (10, "⚡ Goal Scorer"),
        (5, "⚡ Offensive Player"),
        (0, "⚖️ Balanced Player"),
        (-5, "🛡️ Defensive Player"),
        (-10, "🛡️ Defensive Mind"),
        (-20, "🛡️ Defensive Specialist"),
        (-30, "🎯 Defensive Master"),
    ]

    # Find the first tier that matches
    for threshold, personality in tiers:
        if goal_diff >= threshold:
            return personality

    return "🎯 Room for Growth"


def _get_goal_personality(goal_diff: float) -> str:
    """Get goal difference personality."""
    return _get_goal_personality_tier(goal_diff)


def _get_activity_personality_tier(matches: int) -> str:
    """Get activity level personality tier."""
    # Define tiers with their thresholds
    tiers = [
        (200, "🎆 Table Football Immortal"),
        (150, "🎆 League Legend"),
        (100, "🌟 Hall of Fame Legend"),
        (75, "⭐ League Legend"),
        (50, "⭐ Seasoned Veteran"),
        (35, "⭐ Regular Champion"),
        (25, "🏃 Experienced Player"),
        (20, "🏃 Active Player"),
        (15, "🏃 Regular Player"),
        (10, "🌱 Rising Star"),
        (5, "🚀 Promising Rookie"),
        (3, "🚀 Newcomer"),
        (1, "🚀 First Steps"),
    ]

    # Find the first tier that matches
    for threshold, personality in tiers:
        if matches >= threshold:
            return personality

    return "🚀 Ready to Play"


def _get_activity_personality(matches: int) -> str:
    """Get activity level personality."""
    return _get_activity_personality_tier(matches)


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


def _get_win_rate_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get win rate based achievements."""
    achievements = []
    win_rate = player_stats["win_rate"]

    if win_rate >= 90:
        achievements.append(("👑 Legendary Champion", "90%+ win rate", "success"))
    elif win_rate >= 80:
        achievements.append(("🏆 Elite Winner", "80%+ win rate", "success"))
    elif win_rate >= 65:
        achievements.append(("🔥 Strong Competitor", "65%+ win rate", "info"))
    elif win_rate >= 50:
        achievements.append(("⚖️ Balanced Player", "50%+ win rate", "info"))

    return achievements


def _get_goal_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get goal difference based achievements."""
    achievements = []
    goal_diff = player_stats["goal_difference"]

    if goal_diff >= 50:
        achievements.append(("⚡ Goal Machine Pro", "50+ goal difference", "success"))
    elif goal_diff >= 30:
        achievements.append(("⚡ Goal Machine", "30+ goal difference", "success"))
    elif goal_diff >= 20:
        achievements.append(("⚡ Goal Scorer", "20+ goal difference", "success"))
    elif goal_diff >= 10:
        achievements.append(("⚡ Sharp Shooter", "10+ goal difference", "info"))
    elif goal_diff >= 0:
        achievements.append(("⚖️ Balanced Player", "Positive goal difference", "info"))
    elif goal_diff >= -10:
        achievements.append(("🛡️ Defensive Player", "Close goal difference", "warning"))

    return achievements


def _get_activity_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get activity based achievements."""
    achievements = []
    matches = player_stats["matches_played"]

    if matches >= 100:
        achievements.append(("🌟 Hall of Famer", "100+ matches", "success"))
    elif matches >= 75:
        achievements.append(("⭐ League Legend", "75+ matches", "success"))
    elif matches >= 50:
        achievements.append(("⭐ League Veteran", "50+ matches", "warning"))
    elif matches >= 25:
        achievements.append(("🏃 Active Player", "25+ matches", "info"))
    elif matches >= 10:
        achievements.append(("🌱 Rising Star", "10+ matches", "info"))
    elif matches >= 5:
        achievements.append(("🚀 Rookie", "5+ matches", "info"))

    return achievements


def _get_performance_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get performance based achievements."""
    achievements = []
    wins = player_stats["wins"]

    if wins >= 50:
        achievements.append(("🏅 Victory Master", "50+ wins", "success"))
    elif wins >= 25:
        achievements.append(("🏅 Victory Expert", "25+ wins", "success"))
    elif wins >= 10:
        achievements.append(("🏅 Victory Hunter", "10+ wins", "info"))

    return achievements


def _get_streak_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get streak based achievements."""
    achievements = []

    if "current_win_streak" in player_stats:
        streak = player_stats["current_win_streak"]
        if streak >= 10:
            achievements.append(("🔥 Unstoppable", "10+ win streak", "success"))
        elif streak >= 5:
            achievements.append(("🔥 Hot Streak", "5+ win streak", "success"))
        elif streak >= 3:
            achievements.append(("🔥 On Fire", "3+ win streak", "info"))

    return achievements


def _get_special_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get special combination achievements."""
    achievements = []
    matches = player_stats["matches_played"]
    win_rate = player_stats["win_rate"]
    goal_diff = player_stats["goal_difference"]

    # Consistent performer
    if matches >= 20 and win_rate >= 75:
        achievements.append(("💎 Consistent Performer", "High activity + win rate", "success"))

    # Dominant force
    if goal_diff >= 15 and win_rate >= 70:
        achievements.append(("🎯 Dominant Force", "High goals + win rate", "success"))

    # Persistent fighter
    if matches >= 30 and win_rate <= 30:
        achievements.append(("💪 Persistent Fighter", "Many matches despite challenges", "warning"))

    # Reliable competitor
    if matches >= 40 and win_rate >= 60:
        achievements.append(("🌟 Reliable Competitor", "Steady performance over time", "info"))

    return achievements


def _get_rookie_achievements(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get rookie achievements for new players."""
    achievements = []
    matches = player_stats["matches_played"]
    win_rate = player_stats["win_rate"]

    if matches <= 5 and win_rate >= 60:
        achievements.append(("🚀 Promising Start", "Strong start for new player", "info"))

    if matches <= 3 and win_rate >= 80:
        achievements.append(("⭐ Natural Talent", "Exceptional start", "success"))

    return achievements


def _get_achievement_badges(player_stats: pd.Series) -> list[tuple[str, str, str]]:
    """Get achievement badges based on performance."""
    achievements = []

    # Collect achievements from all categories
    achievements.extend(_get_win_rate_achievements(player_stats))
    achievements.extend(_get_goal_achievements(player_stats))
    achievements.extend(_get_activity_achievements(player_stats))
    achievements.extend(_get_performance_achievements(player_stats))
    achievements.extend(_get_streak_achievements(player_stats))
    achievements.extend(_get_special_achievements(player_stats))
    achievements.extend(_get_rookie_achievements(player_stats))

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


def _render_player_insights(player_stats: pd.Series, stats_df: pd.DataFrame) -> None:
    """Render interesting player insights and fun statistics."""
    st.markdown("### 🧠 Player Insights & Fun Facts")

    # Calculate some interesting metrics
    total_players = len(stats_df)
    player_rank = stats_df[stats_df["player_name"] == player_stats["player_name"]].index[0] + 1
    percentile = ((total_players - player_rank) / total_players) * 100

    # Fun facts and insights
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Performance Analysis")

        # Win rate analysis
        if player_stats["win_rate"] >= 80:
            st.success(f"🎯 **Elite Performance**: You're in the top {percentile:.1f}% of players!")
        elif player_stats["win_rate"] >= 60:
            st.info(f"📈 **Above Average**: You're performing better than {percentile:.1f}% of players!")
        elif player_stats["win_rate"] >= 40:
            st.warning(f"⚖️ **Balanced**: You're in the middle {percentile:.1f}% of players!")
        else:
            st.info("🌱 **Growing**: Every match is a learning opportunity!")

        # Goal difference analysis
        if player_stats["goal_difference"] > 0:
            st.success(
                f"⚽ **Offensive Master**: You score {player_stats['goal_difference']} more goals than you concede!"
            )
        elif player_stats["goal_difference"] < 0:
            st.info("🛡️ **Defensive Specialist**: You're great at keeping games close!")
        else:
            st.info("⚖️ **Perfect Balance**: You're equally strong on both ends!")

    with col2:
        st.markdown("#### 🎭 Playing Style")

        # Determine playing style
        if player_stats["win_rate"] >= 75 and player_stats["goal_difference"] >= 20:
            st.success("🏆 **Dominant Attacker**: You control the game and score freely!")
        elif player_stats["win_rate"] >= 65 and player_stats["goal_difference"] <= -10:
            st.info("🛡️ **Defensive Master**: You win through solid defense!")
        elif player_stats["matches_played"] >= 30 and player_stats["win_rate"] <= 40:
            st.warning("💪 **Persistent Fighter**: You never give up, even when the odds are against you!")
        elif player_stats["matches_played"] <= 10 and player_stats["win_rate"] >= 60:
            st.success("⭐ **Natural Talent**: You're showing great potential from the start!")
        else:
            st.info("🎯 **Versatile Player**: You adapt your style based on the situation!")


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
    _render_player_insights(player_stats, stats_df)
