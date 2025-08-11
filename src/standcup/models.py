"""Data models for Standcup - Table Football Tracker."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml
from pydantic import BaseModel, Field
from streamlit_gsheets import GSheetsConnection


class Player(BaseModel):
    """Represents a player in the table football league."""

    id: str
    name: str


class Team(BaseModel):
    """Represents a team (1 or 2 players)."""

    players: list[str] = Field(min_length=1, max_length=2)

    @property
    def is_singles(self) -> bool:
        return len(self.players) == 1


class GameType(str, Enum):
    """Types of games that can be played."""

    CASUAL = "casual"
    TOURNAMENT = "tournament"
    LEAGUE = "league"


class Match(BaseModel):
    """Represents a single table football match."""

    id: str
    date: datetime = Field(default_factory=datetime.now)
    team1: Team
    team2: Team
    team1_score: int = Field(ge=0)
    team2_score: int = Field(ge=0)
    game_type: GameType = GameType.CASUAL
    duration_minutes: int | None = None
    notes: str | None = None

    @property
    def winner_team(self) -> int | None:
        """Returns 1 if team1 wins, 2 if team2 wins, None if tie."""
        if self.team1_score > self.team2_score:
            return 1
        elif self.team2_score > self.team1_score:
            return 2
        return None


class Tournament(BaseModel):
    """Represents a tournament."""

    id: str
    name: str
    start_date: datetime
    end_date: datetime | None = None
    participants: list[str]
    matches: list[str] = Field(default_factory=list)
    winner: str | None = None


class StandcupData(BaseModel):
    """Main data container for all table football data."""

    players: list[Player] = Field(default_factory=list)
    matches: list[Match] = Field(default_factory=list)
    tournaments: list[Tournament] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, file_path: str | Path) -> StandcupData:
        """Load data from YAML file."""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_google_sheets(_cls) -> StandcupData:
        """Load data from Google Sheets."""
        # Connect to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Load players
        players_df = conn.read(worksheet="0", ttl="5m")
        players = [Player(id=row["id"], name=row["name"]) for _, row in players_df.iterrows()]

        # Load matches
        matches_df = conn.read(worksheet="322680090", ttl="5m")
        matches = []

        for _, row in matches_df.iterrows():
            # Build teams from individual player columns
            team1_players = [p for p in [row.get("team_1_p1"), row.get("team_1_p2")] if pd.notna(p) and p]
            team2_players = [p for p in [row.get("team_2_p1"), row.get("team_2_p2")] if pd.notna(p) and p]

            # Handle date parsing
            parsed_date = datetime.strptime(row["date"], "%d/%m/%Y")

            match = Match(
                id=str(row["id"]),
                date=parsed_date,
                team1=Team(players=team1_players),
                team2=Team(players=team2_players),
                team1_score=int(row["team_1_score"]),
                team2_score=int(row["team_2_score"]),
                game_type=row.get("game_type", "casual"),
                notes=row.get("notes") if pd.notna(row.get("notes")) else None,
            )
            matches.append(match)

        return _cls(players=players, matches=matches)

    def to_yaml(self, file_path: str | Path) -> None:
        """Save data to YAML file."""
        with open(file_path, "w", encoding="utf-8") as f:
            data_dict = self.model_dump(mode="json")
            yaml.safe_dump(data_dict, f, default_flow_style=False, sort_keys=False)

    def to_players_df(self) -> pd.DataFrame:
        """Convert players to DataFrame."""
        return pd.DataFrame([player.model_dump() for player in self.players])

    def to_matches_df(self) -> pd.DataFrame:
        """Convert matches to a flat DataFrame for easy analysis."""
        matches_data = []
        for match in self.matches:
            # Create a flat row for each match
            row = {
                "match_id": match.id,
                "date": match.date,
                "team1_players": ", ".join(match.team1.players),
                "team2_players": ", ".join(match.team2.players),
                "team1_score": match.team1_score,
                "team2_score": match.team2_score,
                "winner_team": match.winner_team,
                "game_type": match.game_type,
                "duration_minutes": match.duration_minutes,
                "notes": match.notes,
                "is_singles": match.team1.is_singles and match.team2.is_singles,
                "total_goals": match.team1_score + match.team2_score,
            }
            matches_data.append(row)

        return pd.DataFrame(matches_data)

    def to_player_match_df(self) -> pd.DataFrame:
        """Convert to player-centric DataFrame (one row per player per match)."""
        player_matches = []

        for match in self.matches:
            # Add row for each player in team1
            for player_id in match.team1.players:
                row = {
                    "player_id": player_id,
                    "match_id": match.id,
                    "date": match.date,
                    "team": 1,
                    "teammate": match.team1.players[1]
                    if len(match.team1.players) == 2 and match.team1.players[0] == player_id
                    else (match.team1.players[0] if len(match.team1.players) == 2 else None),
                    "opponent1": match.team2.players[0],
                    "opponent2": match.team2.players[1] if len(match.team2.players) == 2 else None,
                    "goals_for": match.team1_score,
                    "goals_against": match.team2_score,
                    "won": match.winner_team == 1,
                    "lost": match.winner_team == 2,
                    "tied": match.winner_team is None,
                    "game_type": match.game_type,
                    "is_singles": match.team1.is_singles and match.team2.is_singles,
                }
                player_matches.append(row)

            # Add row for each player in team2
            for player_id in match.team2.players:
                row = {
                    "player_id": player_id,
                    "match_id": match.id,
                    "date": match.date,
                    "team": 2,
                    "teammate": match.team2.players[1]
                    if len(match.team2.players) == 2 and match.team2.players[0] == player_id
                    else (match.team2.players[0] if len(match.team2.players) == 2 else None),
                    "opponent1": match.team1.players[0],
                    "opponent2": match.team1.players[1] if len(match.team1.players) == 2 else None,
                    "goals_for": match.team2_score,
                    "goals_against": match.team1_score,
                    "won": match.winner_team == 2,
                    "lost": match.winner_team == 1,
                    "tied": match.winner_team is None,
                    "game_type": match.game_type,
                    "is_singles": match.team1.is_singles and match.team2.is_singles,
                }
                player_matches.append(row)

        return pd.DataFrame(player_matches)
