"""Match making functionality for generating balanced matches."""

from __future__ import annotations

from itertools import combinations
from typing import NamedTuple

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
