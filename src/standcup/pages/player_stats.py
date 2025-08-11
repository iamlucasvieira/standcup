"""Player statistics page for Standcup."""

from __future__ import annotations

import pandas as pd
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


def _get_win_delta_message(win_rate: float) -> str:
    """Get win rate delta message."""
    if win_rate >= 70:
        return f"{win_rate:.1f}% - Unstoppable! 🔥"
    elif win_rate >= 60:
        return f"{win_rate:.1f}% - Strong! ⚽"
    elif win_rate >= 50:
        return f"{win_rate:.1f}% - Balanced! ⚖️"
    else:
        return f"{win_rate:.1f}% - Improving! 📈"


def _get_goal_diff_message(goal_diff: float) -> str:
    """Get goal difference message."""
    if goal_diff >= 30:
        return "Absolute Beast! 🦁"
    elif goal_diff >= 15:
        return "Goal Machine! ⚡"
    elif goal_diff >= 5:
        return "Sharp Shooter! 🎯"
    elif goal_diff >= 0:
        return "Balanced Force! ⚖️"
    elif goal_diff >= -10:
        return "Defensive Wall! 🛡️"
    else:
        return "Comeback King! 💪"


def _render_match_record(col, player_stats: pd.Series) -> None:
    """Render match record section."""
    with col:
        st.markdown("**🎮 Match Record**")
        st.metric("Matches Played", int(player_stats["matches_played"]), help="Total matches participated in")

        wins = int(player_stats["wins"])
        win_rate = player_stats["win_rate"]
        win_delta = _get_win_delta_message(win_rate)
        st.metric("Wins", wins, delta=win_delta)


def _render_win_loss_record(col, player_stats: pd.Series) -> None:
    """Render win/loss record section."""
    with col:
        st.markdown("**📊 Win/Loss Record**")
        st.metric("Losses", int(player_stats["losses"]))
        st.metric("Ties", int(player_stats["ties"]))

        goal_diff = player_stats["goal_difference"]
        diff_msg = _get_goal_diff_message(goal_diff)
        st.metric("Goal Difference", f"{goal_diff:+.0f}", delta=diff_msg)


def _render_scoring_stats(col, player_stats: pd.Series) -> None:
    """Render scoring statistics section."""
    with col:
        st.markdown("**⚽ Scoring Stats**")
        st.metric("Goals For", int(player_stats["goals_for"]))
        st.metric("Goals Against", int(player_stats["goals_against"]))
        st.metric("Goals/Match", f"{player_stats['avg_goals_per_match']:.2f}", help="Average goals scored per match")


def _render_player_profile(selected_player: str, player_stats: pd.Series) -> None:
    """Render individual player profile section."""
    personality = get_player_personality(player_stats)

    st.markdown(f"**🏅 {selected_player}'s Championship Profile**")
    st.markdown(f"*{personality['win_style']} • {personality['goal_style']} • {personality['activity']}*")

    col1, col2, col3 = st.columns(3, gap="medium")
    _render_match_record(col1, player_stats)
    _render_win_loss_record(col2, player_stats)
    _render_scoring_stats(col3, player_stats)


def _get_achievement_status(rank: int, win_rate: float, matches: int) -> str:
    """Get achievement status for player."""
    if rank == 1 and matches >= 5:
        return "👑 Champion"
    elif rank <= 3 and matches >= 5:
        return "🥉 Podium"
    elif win_rate >= 70:
        return "🔥 Elite"
    elif matches >= 50:
        return "⭐ Veteran"
    elif matches >= 20:
        return "🏃 Active"
    elif matches >= 10:
        return "🌱 Rising"
    else:
        return "🚀 Rookie"


def _render_leaderboard(stats_df: pd.DataFrame) -> None:
    """Render the leaderboard section."""
    st.markdown("#### 🏆 League Leaderboard & Hall of Fame")
    st.markdown("🌟 **Champions, legends, and rising stars - see where everyone stands in the ultimate ranking!**")

    display_stats = stats_df[
        [
            "player_name",
            "matches_played",
            "wins",
            "losses",
            "ties",
            "win_rate",
            "goals_for",
            "goals_against",
            "goal_difference",
        ]
    ].copy()
    display_stats.columns = [
        "Player",
        "Matches",
        "Wins",
        "Losses",
        "Ties",
        "Win Rate (%)",
        "Goals For",
        "Goals Against",
        "Goal Diff",
    ]

    # Sort by win rate and add ranking with achievements
    display_stats = display_stats.sort_values("Win Rate (%)", ascending=False)
    display_stats.insert(0, "Rank", range(1, len(display_stats) + 1))

    # Add achievement column
    achievements = [
        _get_achievement_status(row["Rank"], row["Win Rate (%)"], row["Matches"]) for _, row in display_stats.iterrows()
    ]
    display_stats.insert(1, "Status", achievements)

    st.dataframe(
        display_stats,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
            "Status": st.column_config.TextColumn("🎆 Status", width="medium"),
            "Player": st.column_config.TextColumn("👤 Player", width="medium"),
            "Win Rate (%)": st.column_config.ProgressColumn(
                "📈 Win Rate (%)", min_value=0, max_value=100, format="%.1f%%"
            ),
        },
        hide_index=True,
    )


def render_player_stats_page(stats_df: pd.DataFrame) -> None:
    """Render the player statistics page."""
    st.markdown("### 🏆 Player Hall of Fame")
    st.markdown(
        "🎯 **Discover the legends, rising stars, and comeback stories of your league!** Every player has their unique style - let's find yours."
    )

    if stats_df.empty:
        _render_empty_stats()
        return

    st.divider()

    # Enhanced player selection
    st.markdown("#### 🔍 Player Analysis")
    selected_player = st.selectbox(
        "Choose a player to analyze:",
        options=stats_df["player_name"].tolist(),
        index=0,
        help="Select any player to see their detailed performance metrics",
    )

    player_stats = stats_df[stats_df["player_name"] == selected_player].iloc[0]
    _render_player_profile(selected_player, player_stats)

    st.divider()
    _render_leaderboard(stats_df)
