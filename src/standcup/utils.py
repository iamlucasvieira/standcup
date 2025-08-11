"""Utility functions for data processing and calculations."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from standcup.models import StandcupData


@st.cache_data
def load_data() -> StandcupData:
    """Load data with caching from Google Sheets or YAML file."""
    try:
        return StandcupData.from_google_sheets()
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return StandcupData.from_yaml(Path(__file__).parent / "data.yml")


def calculate_player_stats(data: StandcupData) -> pd.DataFrame:
    """Calculate comprehensive player statistics."""
    player_df = data.to_player_match_df()

    if player_df.empty:
        return pd.DataFrame()

    # Get player names mapping
    players_dict = {p.id: p.name for p in data.players}

    stats = (
        player_df.groupby("player_id")
        .agg({
            "won": ["count", "sum"],
            "lost": "sum",
            "tied": "sum",
            "goals_for": "sum",
            "goals_against": "sum",
        })
        .round(2)
    )

    # Flatten column names
    stats.columns = ["matches_played", "wins", "losses", "ties", "goals_for", "goals_against"]

    # Calculate additional metrics
    stats["win_rate"] = (stats["wins"] / stats["matches_played"] * 100).round(1)
    stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]
    stats["avg_goals_per_match"] = (stats["goals_for"] / stats["matches_played"]).round(2)
    stats["avg_goals_against_per_match"] = (stats["goals_against"] / stats["matches_played"]).round(2)

    # Add player names
    stats["player_name"] = stats.index.map(players_dict)
    stats = stats.reset_index()

    return stats


def calculate_head_to_head(data: StandcupData, player1_id: str, player2_id: str) -> dict:
    """Calculate head-to-head statistics between two players."""
    player_matches = data.to_player_match_df()

    # Find matches where both players participated
    player1_matches = set(player_matches[player_matches["player_id"] == player1_id]["match_id"])
    player2_matches = set(player_matches[player_matches["player_id"] == player2_id]["match_id"])
    common_matches = player1_matches & player2_matches

    if not common_matches:
        return {"p1_wins": 0, "p2_wins": 0, "ties": 0, "total_matches": 0}

    p1_wins = 0
    p2_wins = 0
    ties = 0

    for match_id in common_matches:
        match = next(m for m in data.matches if m.id == match_id)

        # Determine which team each player was on
        p1_team = 1 if player1_id in match.team1.players else 2
        p2_team = 1 if player2_id in match.team1.players else 2

        # If they're on the same team, skip (this is a doubles match where they're teammates)
        if p1_team == p2_team:
            continue

        winner = match.winner_team
        if winner == p1_team:
            p1_wins += 1
        elif winner == p2_team:
            p2_wins += 1
        else:
            ties += 1

    return {"p1_wins": p1_wins, "p2_wins": p2_wins, "ties": ties, "total_matches": p1_wins + p2_wins + ties}
