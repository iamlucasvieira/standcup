"""Page components for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from standcup.charts import (
    create_cumulative_wins_chart,
    create_goals_chart,
    create_head_to_head_chart,
    create_match_timeline,
    create_win_rate_chart,
)
from standcup.matchmaker import calculate_player_strengths, generate_match_suggestions
from standcup.models import StandcupData
from standcup.utils import calculate_head_to_head


def render_overview_page(data: StandcupData, stats_df: pd.DataFrame, matches_df: pd.DataFrame) -> None:
    """Render the overview/dashboard page."""
    st.header("📊 Dashboard Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Players", len(data.players))

    with col2:
        st.metric("Total Matches", len(data.matches))

    with col3:
        if not matches_df.empty:
            avg_goals = matches_df["total_goals"].mean()
            st.metric("Avg Goals/Match", f"{avg_goals:.1f}")

    with col4:
        if not stats_df.empty:
            top_player = stats_df.loc[stats_df["win_rate"].idxmax(), "player_name"]
            st.metric("Top Win Rate", top_player)

    # Charts
    if not stats_df.empty:
        # Leaderboard progression chart - full width
        st.plotly_chart(create_cumulative_wins_chart(data), use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_win_rate_chart(stats_df), use_container_width=True)

        with col2:
            st.plotly_chart(create_goals_chart(stats_df), use_container_width=True)

        st.plotly_chart(create_match_timeline(data), use_container_width=True)


def render_player_stats_page(stats_df: pd.DataFrame) -> None:
    """Render the player statistics page."""
    st.header("👥 Player Statistics")

    if stats_df.empty:
        st.warning("No player statistics available.")
        return

    # Player selection
    selected_player = st.selectbox(
        "Select a player for detailed stats:", options=stats_df["player_name"].tolist(), index=0
    )

    player_stats = stats_df[stats_df["player_name"] == selected_player].iloc[0]

    # Display detailed stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Matches Played", int(player_stats["matches_played"]))
        st.metric("Wins", int(player_stats["wins"]))
        st.metric("Win Rate", f"{player_stats['win_rate']:.1f}%")

    with col2:
        st.metric("Losses", int(player_stats["losses"]))
        st.metric("Ties", int(player_stats["ties"]))
        st.metric("Goal Difference", f"{player_stats['goal_difference']:+.0f}")

    with col3:
        st.metric("Goals For", int(player_stats["goals_for"]))
        st.metric("Goals Against", int(player_stats["goals_against"]))
        st.metric("Avg Goals/Match", f"{player_stats['avg_goals_per_match']:.2f}")

    # Overall stats table
    st.subheader("All Players Comparison")
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

    st.dataframe(display_stats.sort_values("Win Rate (%)", ascending=False), use_container_width=True)


def render_match_history_page(matches_df: pd.DataFrame) -> None:
    """Render the match history page."""
    st.header("🏆 Match History")

    if matches_df.empty:
        st.warning("No matches available.")
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

    # Display matches
    st.subheader(f"Matches ({len(filtered_df)} total)")

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

    st.dataframe(display_matches.sort_values("Date", ascending=False), use_container_width=True)


def render_head_to_head_page(data: StandcupData) -> None:
    """Render the head-to-head analysis page."""
    st.header("🆚 Head-to-Head Analysis")

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


def render_match_maker_page(data: StandcupData, stats_df: pd.DataFrame) -> None:
    """Render the match maker page."""
    st.header("🎯 Match Maker")
    st.markdown("Generate balanced matches based on player statistics and pairing history.")

    if len(data.players) < 2:
        st.warning("Need at least 2 players to generate matches.")
        return

    selection_result = _render_player_selection_section(data)
    if selection_result:
        _render_match_suggestions_section(data, stats_df, selection_result)
    _render_player_strengths_section(data, stats_df)
    _render_match_making_tips()


def _render_player_selection_section(data: StandcupData) -> tuple[list[str], str, int] | None:
    """Render player selection and match configuration."""
    st.subheader("Select Available Players")
    player_names = [p.name for p in data.players]

    selected_players = st.multiselect(
        "Choose players who are available to play:",
        options=player_names,
        default=player_names,
        help="Select all players who are currently available for a match",
    )

    if len(selected_players) < 2:
        st.warning("Please select at least 2 players.")
        return None

    col1, col2 = st.columns(2)
    with col1:
        match_type = st.radio("Match Type:", ["singles", "doubles"], index=1, help="Singles: 1v1, Doubles: 2v2")
    with col2:
        num_suggestions = st.slider(
            "Number of suggestions:", min_value=1, max_value=10, value=5, help="How many match suggestions to generate"
        )

    required_players = 2 if match_type == "singles" else 4
    if len(selected_players) < required_players:
        st.warning(f"Need at least {required_players} players for {match_type} matches.")
        return None

    return selected_players, match_type, num_suggestions


def _render_match_suggestions_section(
    data: StandcupData, stats_df: pd.DataFrame, selection_result: tuple[list[str], str, int]
) -> None:
    """Render the match suggestions generation section."""
    selected_players, match_type, num_suggestions = selection_result
    player_name_to_id = {p.name: p.id for p in data.players}

    if st.button("🎲 Generate Match Suggestions", type="primary"):
        selected_player_ids = [player_name_to_id[name] for name in selected_players]

        with st.spinner("Generating optimal matches..."):
            suggestions = generate_match_suggestions(data, selected_player_ids, match_type, num_suggestions)

        if not suggestions:
            st.error("No match suggestions could be generated.")
            return

        _display_match_suggestions(data, suggestions)


def _display_match_suggestions(data: StandcupData, suggestions) -> None:
    """Display the generated match suggestions."""
    st.subheader("🏆 Suggested Matches")
    st.markdown("Matches are ranked by quality score (balance + variety).")

    for i, suggestion in enumerate(suggestions, 1):
        with st.expander(f"Match {i} (Score: {suggestion.score:.3f})", expanded=i == 1):
            _render_single_match_suggestion(data, suggestion)


def _render_single_match_suggestion(data: StandcupData, suggestion) -> None:
    """Render a single match suggestion."""
    col1, col2, col3 = st.columns([2, 1, 2])

    # Team 1
    with col1:
        team1_names = [next(p.name for p in data.players if p.id == pid) for pid in suggestion.team1_players]
        st.markdown("**Team 1:**")
        for name in team1_names:
            st.write(f"• {name}")

    # VS
    with col2:
        st.markdown(
            "<div style='text-align: center; font-size: 2em; font-weight: bold; margin-top: 20px;'>VS</div>",
            unsafe_allow_html=True,
        )

    # Team 2
    with col3:
        team2_names = [next(p.name for p in data.players if p.id == pid) for pid in suggestion.team2_players]
        st.markdown("**Team 2:**")
        for name in team2_names:
            st.write(f"• {name}")

    # Reasoning
    st.markdown("**Why this match:**")
    st.info(suggestion.reasoning)


def _render_player_strengths_section(data: StandcupData, stats_df: pd.DataFrame) -> None:
    """Render the player strengths information section."""
    st.subheader("📊 Player Strengths")
    st.markdown("Understanding how players are rated for match making:")

    if stats_df.empty:
        return

    strengths = calculate_player_strengths(data)
    if not strengths:
        return

    strength_data = _build_strength_data(data, stats_df, strengths)
    if strength_data:
        strength_df = pd.DataFrame(strength_data).sort_values("Strength", ascending=False)
        st.dataframe(strength_df, use_container_width=True)
        _render_strength_explanation()


def _build_strength_data(data: StandcupData, stats_df: pd.DataFrame, strengths: dict) -> list[dict]:
    """Build strength data for display."""
    strength_data = []
    for player in data.players:
        if player.id in strengths:
            player_stats = stats_df[stats_df["player_id"] == player.id]
            if not player_stats.empty:
                row = player_stats.iloc[0]
                strength_data.append({
                    "Player": player.name,
                    "Strength": f"{strengths[player.id]:.3f}",
                    "Win Rate": f"{row['win_rate']:.1f}%",
                    "Matches": int(row["matches_played"]),
                    "Goal Diff": f"{row['goal_difference']:+.0f}",
                })
    return strength_data


def _render_strength_explanation() -> None:
    """Render explanation of how strength is calculated."""
    st.markdown("""
    **How strength is calculated:**
    - 70% win rate performance
    - 30% goal contribution (goals for vs goals against)
    - Weighted by experience (players with fewer matches get adjusted ratings)
    - Scale: 0.1 (weakest) to 1.0 (strongest)
    """)


def _render_match_making_tips() -> None:
    """Render match making tips section."""
    with st.expander("💡 Match Making Tips"):
        st.markdown("""
        **How the match maker works:**

        🎯 **Balance (70% of score):** Matches teams with similar combined strength ratings

        🔄 **Variety (30% of score):** Promotes new pairings and reduces repetitive matches

        📈 **Player Strength:** Calculated from win rate, goal difference, and experience

        🤝 **Pairing History:** Tracks teammate and opponent combinations to encourage variety

        **Tips for best results:**
        - Have at least 10 matches of history for accurate ratings
        - Select 4+ players for doubles to get multiple suggestions
        - Use the suggestions as a starting point - adjust based on player preferences
        """)
