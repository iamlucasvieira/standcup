"""Match history page for Standcup."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def get_match_excitement(team1_score: int, team2_score: int) -> str:
    """Generate excitement level for match based on score."""
    total_goals = team1_score + team2_score
    goal_diff = abs(team1_score - team2_score)

    if goal_diff == 1:
        if total_goals >= 18:
            return "🔥 Nail-biter!"
        else:
            return "⚔️ Close Battle!"
    elif goal_diff == 2:
        return "⚡ Tight Match!"
    elif goal_diff >= 8:
        return "💥 Demolition!"
    elif goal_diff >= 6:
        return "🚀 Dominant!"
    else:
        return "⚽ Good Game!"


def get_match_history_intro(matches_df: pd.DataFrame) -> tuple[str, str]:
    """Generate dynamic intro based on match history."""
    if matches_df.empty:
        return (
            "📖 The Chronicles Await",
            "Every legend starts with their first chapter. Your table football story is ready to begin!",
        )

    total_matches = len(matches_df)
    matches_df.head(10)
    avg_goals = matches_df["total_goals"].mean()
    close_matches = len(matches_df[abs(matches_df["team1_score"] - matches_df["team2_score"]) <= 2])

    if total_matches >= 100:
        return (
            "📚 Hall of Fame Chronicles",
            f"Witness the epic saga! {total_matches} legendary battles have been fought, each one adding to your league's rich history.",
        )
    elif total_matches >= 50:
        return (
            "⚔️ Battle Hardened Archives",
            f"{total_matches} matches of pure competition! Your league has seen glory, heartbreak, and legendary comebacks.",
        )
    elif close_matches / total_matches > 0.6:
        return (
            "🔥 Thriller Collection",
            f"This league delivers drama! {close_matches}/{total_matches} matches decided by 2 goals or less - edge-of-your-seat action!",
        )
    elif avg_goals >= 8:
        return (
            "💥 Goal Fest Archives",
            f"High-octane action with {avg_goals:.1f} goals per match! This league doesn't believe in boring games.",
        )
    else:
        return (
            "📝 Growing Legend",
            f"{total_matches} matches and counting! Each game adds another page to your league's story.",
        )


def render_match_history_page(matches_df: pd.DataFrame) -> None:
    """Render the match history page."""
    title, description = get_match_history_intro(matches_df)
    st.header(title)
    st.markdown(description)

    if matches_df.empty:
        st.info("🏆 **Ready to make history?**")
        st.markdown("""
        🚀 **Your first match awaits!** Every great rivalry, every legendary comeback, every championship moment starts with a single game.

        🎯 What will your first story be?
        """)
        return

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        game_types = ["All", *matches_df["game_type"].unique().tolist()]
        selected_type = st.selectbox("Game Type", game_types)

    with col2:
        match_types = ["All", "Singles Only", "Doubles Only"]
        selected_match_type = st.selectbox("Match Type", match_types)

    # Filter data
    filtered_df = matches_df.copy()

    if selected_type != "All":
        filtered_df = filtered_df[filtered_df["game_type"] == selected_type]

    if selected_match_type == "Singles Only":
        filtered_df = filtered_df[filtered_df["is_singles"]]
    elif selected_match_type == "Doubles Only":
        filtered_df = filtered_df[~filtered_df["is_singles"]]

    # Match statistics
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🏆 Total Matches", len(filtered_df))

        with col2:
            avg_goals = filtered_df["total_goals"].mean()
            if avg_goals >= 9:
                goal_status = "🔥 Explosive!"
            elif avg_goals >= 8:
                goal_status = "⚡ High-scoring!"
            else:
                goal_status = "⚽ Competitive!"
            st.metric("⚽ Avg Goals", f"{avg_goals:.1f}", delta=goal_status)

        with col3:
            close_matches = len(filtered_df[abs(filtered_df["team1_score"] - filtered_df["team2_score"]) <= 2])
            close_pct = (close_matches / len(filtered_df)) * 100
            st.metric("🔥 Close Matches", f"{close_pct:.0f}%", help="Matches decided by 2 goals or less")

        with col4:
            if "duration_minutes" in filtered_df.columns:
                avg_duration = filtered_df["duration_minutes"].mean()
                st.metric("⏱️ Avg Duration", f"{avg_duration:.0f}m")
            else:
                st.metric("⏱️ Status", "Live League!")

    st.divider()

    # Display matches
    st.subheader(f"📈 Match Chronicles ({len(filtered_df)} battles)")

    display_matches = filtered_df[
        [
            "date",
            "team1_players",
            "team2_players",
            "team1_score",
            "team2_score",
            "game_type",
            "duration_minutes",
        ]
    ].copy()
    display_matches.loc[:, "date"] = display_matches["date"].apply(
        lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M")
    )
    display_matches.columns = ["Date", "Team 1", "Team 2", "Score 1", "Score 2", "Type", "Duration (min)"]

    # Add excitement column
    excitement = []
    for _, row in filtered_df.iterrows():
        excitement.append(get_match_excitement(row["team1_score"], row["team2_score"]))

    display_matches.insert(6, "Match Rating", excitement)

    st.dataframe(
        display_matches.sort_values("Date", ascending=False),
        use_container_width=True,
        column_config={
            "Date": st.column_config.DatetimeColumn("📅 Date"),
            "Team 1": st.column_config.TextColumn("🔴 Team 1"),
            "Team 2": st.column_config.TextColumn("🔵 Team 2"),
            "Score 1": st.column_config.NumberColumn("🎯 Score", width="small"),
            "Score 2": st.column_config.NumberColumn("🎯 Score", width="small"),
            "Type": st.column_config.TextColumn("🎮 Type", width="small"),
            "Match Rating": st.column_config.TextColumn("🎆 Rating"),
            "Duration (min)": st.column_config.NumberColumn("⏱️ Duration", width="small"),
        },
        hide_index=True,
    )
