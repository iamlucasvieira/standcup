"""Match maker page for Standcup."""

from __future__ import annotations

from itertools import combinations
from typing import NamedTuple

import pandas as pd
import streamlit as st

from standcup.models import StandcupData
from standcup.utils import calculate_player_stats


class MatchSuggestion(NamedTuple):
    """Represents a suggested match with teams and scoring."""

    team1_players: list[str]
    team2_players: list[str]
    score: float
    reasoning: str


def calculate_player_strengths(data: StandcupData) -> dict[str, float]:
    """Calculate player strength ratings based on performance."""
    stats_df = calculate_player_stats(data)
    if stats_df.empty:
        return {}

    strengths = {}
    for _, row in stats_df.iterrows():
        # Combine win rate and goal difference for strength rating
        win_rate = row["win_rate"] / 100
        matches_played = row["matches_played"]
        goal_diff_per_match = row["goal_difference"] / max(matches_played, 1)

        # Weight by experience (min matches to be fully weighted)
        experience_weight = min(matches_played / 10, 1.0)

        # Strength combines win rate and offensive contribution
        base_strength = (win_rate * 0.7) + (min(goal_diff_per_match / 3, 0.3) + 0.5) * 0.3
        strength = base_strength * experience_weight + 0.5 * (1 - experience_weight)

        strengths[row["player_id"]] = max(0.1, min(1.0, strength))

    return strengths


def analyze_pairing_history(data: StandcupData) -> dict[str, dict[str, int]]:
    """Analyze how often players have been paired as teammates or opponents."""
    teammate_count = {}
    opponent_count = {}

    for match in data.matches:
        # Count teammate pairings
        for team in [match.team1.players, match.team2.players]:
            if len(team) == 2:
                p1, p2 = team
                teammate_count.setdefault(p1, {}).setdefault(p2, 0)
                teammate_count.setdefault(p2, {}).setdefault(p1, 0)
                teammate_count[p1][p2] += 1
                teammate_count[p2][p1] += 1

        # Count opponent pairings
        for p1 in match.team1.players:
            for p2 in match.team2.players:
                opponent_count.setdefault(p1, {}).setdefault(p2, 0)
                opponent_count.setdefault(p2, {}).setdefault(p1, 0)
                opponent_count[p1][p2] += 1
                opponent_count[p2][p1] += 1

    return {"teammates": teammate_count, "opponents": opponent_count}


def score_match_quality(
    team1: list[str], team2: list[str], strengths: dict[str, float], pairing_history: dict, max_pairings: int
) -> tuple[float, str]:
    """Score the quality of a potential match."""
    if not all(p in strengths for p in team1 + team2):
        return 0.0, "Missing player strength data"

    # Calculate team strengths
    team1_strength = sum(strengths[p] for p in team1)
    team2_strength = sum(strengths[p] for p in team2)

    # Balance score (closer strengths = better)
    max_strength = max(team1_strength, team2_strength)
    balance_score = 1.0 - abs(team1_strength - team2_strength) / max(max_strength, 1.0)

    # Variety score (fewer recent pairings = better)
    variety_score = _calculate_variety_score(team1, team2, pairing_history, max_pairings)

    # Combined score (70% balance, 30% variety)
    final_score = balance_score * 0.7 + variety_score * 0.3

    reasoning = f"Team balance: {balance_score:.2f}, Variety: {variety_score:.2f}"
    return final_score, reasoning


def _calculate_variety_score(team1: list[str], team2: list[str], pairing_history: dict, max_pairings: int) -> float:
    """Calculate variety score based on pairing history."""
    variety_score = 1.0
    total_pairings = 0

    # Check teammate variety
    teammates = pairing_history.get("teammates", {})
    for team in [team1, team2]:
        if len(team) == 2:
            p1, p2 = team
            pairings = teammates.get(p1, {}).get(p2, 0)
            total_pairings += pairings

    # Check opponent variety
    opponents = pairing_history.get("opponents", {})
    for p1 in team1:
        for p2 in team2:
            pairings = opponents.get(p1, {}).get(p2, 0)
            total_pairings += pairings

    # Penalize high pairing counts
    if max_pairings > 0:
        variety_score = max(0.1, 1.0 - (total_pairings / (max_pairings * 4)))

    return variety_score


def _get_max_pairings(pairing_history: dict) -> int:
    """Get the maximum pairing count for normalization."""
    max_pairings = 0

    if pairing_history["teammates"]:
        teammate_counts = pairing_history["teammates"]
        if isinstance(teammate_counts, dict):
            max_pairings = max(
                max(counts.values()) if isinstance(counts, dict) and counts else 0
                for counts in teammate_counts.values()
            )

    if pairing_history["opponents"]:
        opponent_counts = pairing_history["opponents"]
        if isinstance(opponent_counts, dict):
            max_opponent_pairings = max(
                max(counts.values()) if isinstance(counts, dict) and counts else 0
                for counts in opponent_counts.values()
            )
            max_pairings = max(max_pairings, max_opponent_pairings)

    return max_pairings


def _generate_singles_suggestions(
    available_players: list[str], strengths: dict, pairing_history: dict, max_pairings: int
) -> list[MatchSuggestion]:
    """Generate singles match suggestions."""
    suggestions = []
    for p1, p2 in combinations(available_players, 2):
        score, reasoning = score_match_quality([p1], [p2], strengths, pairing_history, max_pairings)
        suggestions.append(MatchSuggestion([p1], [p2], score, reasoning))
    return suggestions


def _generate_doubles_suggestions(
    available_players: list[str], strengths: dict, pairing_history: dict, max_pairings: int
) -> list[MatchSuggestion]:
    """Generate doubles match suggestions."""
    suggestions = []
    seen_matches = set()

    for team1 in combinations(available_players, 2):
        remaining = [p for p in available_players if p not in team1]
        for team2 in combinations(remaining, 2):
            if len(set(team1 + team2)) == 4:  # Ensure no duplicate players
                # Create a normalized match signature to avoid duplicates
                # Sort both teams and then sort the pair of teams
                normalized_team1 = tuple(sorted(team1))
                normalized_team2 = tuple(sorted(team2))
                match_signature = tuple(sorted([normalized_team1, normalized_team2]))

                if match_signature not in seen_matches:
                    seen_matches.add(match_signature)
                    score, reasoning = score_match_quality(
                        list(team1), list(team2), strengths, pairing_history, max_pairings
                    )
                    suggestions.append(MatchSuggestion(list(team1), list(team2), score, reasoning))
    return suggestions


def generate_match_suggestions(
    data: StandcupData, available_players: list[str], match_type: str = "doubles", num_suggestions: int = 5
) -> list[MatchSuggestion]:
    """Generate suggested matches for available players."""
    if len(available_players) < 2:
        return []

    # For singles, need exactly 2 players; for doubles, need exactly 4
    required_players = 2 if match_type == "singles" else 4
    if len(available_players) < required_players:
        return []

    strengths = calculate_player_strengths(data)
    pairing_history = analyze_pairing_history(data)
    max_pairings = _get_max_pairings(pairing_history)

    if match_type == "singles":
        suggestions = _generate_singles_suggestions(available_players, strengths, pairing_history, max_pairings)
    else:
        suggestions = _generate_doubles_suggestions(available_players, strengths, pairing_history, max_pairings)

    # Sort by score and return top suggestions
    suggestions.sort(key=lambda x: x.score, reverse=True)
    return suggestions[:num_suggestions]


def render_match_maker_page(data: StandcupData, stats_df: pd.DataFrame) -> None:
    """Render the match maker page."""
    st.markdown("### 🎯 Smart Match Maker")
    st.markdown(
        "Generate perfectly balanced matches using AI-powered analytics that consider player strengths, recent performance, and pairing history."
    )

    if len(data.players) < 2:
        st.error("🚫 Need at least 2 players to generate matches.")
        st.info("💡 Add more players to your league to use the match maker!")
        return

    st.divider()

    selection_result = _render_player_selection_section(data)
    if selection_result:
        _render_match_suggestions_section(data, stats_df, selection_result)

    st.divider()
    _render_player_strengths_section(data, stats_df)
    _render_match_making_tips()


def _render_player_selection_section(data: StandcupData) -> tuple[list[str], str, int] | None:
    """Render player selection and match configuration."""
    st.markdown("#### 🎮 Match Configuration")

    # Player selection with enhanced UI
    player_names = [p.name for p in data.players]
    st.markdown("**Available Players**")
    selected_players = st.multiselect(
        "Select players ready to play:",
        options=player_names,
        default=player_names,
        help="Choose all players who are currently available for a match",
    )

    if len(selected_players) < 2:
        st.warning("⚠️ Please select at least 2 players to continue.")
        return None

    st.markdown("**Match Settings**")
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        match_type = st.radio(
            "🎯 Match Format:",
            ["singles", "doubles"],
            index=1,
            help="• Singles: 1v1 competitive matches\n• Doubles: 2v2 team matches",
            format_func=lambda x: f"{'🏓' if x == 'singles' else '👬'} {x.title()} ({'1v1' if x == 'singles' else '2v2'})",
        )

    with col2:
        num_suggestions = st.slider(
            "📊 Suggestions to generate:",
            min_value=1,
            max_value=10,
            value=5,
            help="More suggestions = more match options to choose from",
        )

    # Validation with better messaging
    required_players = 2 if match_type == "singles" else 4
    if len(selected_players) < required_players:
        st.error(f"🚫 Need at least {required_players} players for {match_type} matches.")
        st.info(
            f"💡 You have {len(selected_players)} players selected. Add {required_players - len(selected_players)} more!"
        )
        return None

    # Success indicator
    st.success(f"✅ Ready to generate {match_type} matches for {len(selected_players)} players!")
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
    st.markdown("#### 📊 Player Strengths")
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
