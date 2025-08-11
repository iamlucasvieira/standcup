"""Tests for Standcup models."""

import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from standcup.models import (
    GameType,
    Match,
    Player,
    StandcupData,
    Team,
    Tournament,
)


class TestPlayer:
    """Tests for Player model."""

    def test_player_creation(self):
        player = Player(id="player1", name="John Doe")
        assert player.id == "player1"
        assert player.name == "John Doe"

    @pytest.mark.parametrize(
        "player_id,name",
        [
            ("p1", "Alice"),
            ("p2", "Bob"),
            ("player123", "Charlie Brown"),
        ],
    )
    def test_player_creation_parametrized(self, player_id, name):
        player = Player(id=player_id, name=name)
        assert player.id == player_id
        assert player.name == name


class TestTeam:
    """Tests for Team model."""

    def test_team_single_player(self):
        team = Team(players=["player1"])
        assert team.players == ["player1"]
        assert team.is_singles is True

    def test_team_two_players(self):
        team = Team(players=["player1", "player2"])
        assert team.players == ["player1", "player2"]
        assert team.is_singles is False

    def test_team_validation_empty(self):
        with pytest.raises(ValueError):
            Team(players=[])

    def test_team_validation_too_many_players(self):
        with pytest.raises(ValueError):
            Team(players=["p1", "p2", "p3"])

    @pytest.mark.parametrize(
        "players,expected_singles",
        [
            (["p1"], True),
            (["p1", "p2"], False),
        ],
    )
    def test_is_singles_property(self, players, expected_singles):
        team = Team(players=players)
        assert team.is_singles == expected_singles


class TestGameType:
    """Tests for GameType enum."""

    def test_game_type_values(self):
        assert GameType.CASUAL == "casual"
        assert GameType.TOURNAMENT == "tournament"
        assert GameType.LEAGUE == "league"

    def test_game_type_enum_members(self):
        assert len(GameType) == 3
        assert "CASUAL" in GameType.__members__
        assert "TOURNAMENT" in GameType.__members__
        assert "LEAGUE" in GameType.__members__


class TestMatch:
    """Tests for Match model."""

    def test_match_creation_minimal(self):
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])
        match = Match(
            id="match1",
            team1=team1,
            team2=team2,
            team1_score=3,
            team2_score=1,
        )
        assert match.id == "match1"
        assert match.team1 == team1
        assert match.team2 == team2
        assert match.team1_score == 3
        assert match.team2_score == 1
        assert match.game_type == GameType.CASUAL
        assert match.duration_minutes is None
        assert match.notes is None

    def test_match_creation_full(self):
        team1 = Team(players=["p1", "p2"])
        team2 = Team(players=["p3", "p4"])
        match = Match(
            id="match1",
            team1=team1,
            team2=team2,
            team1_score=5,
            team2_score=3,
            game_type=GameType.TOURNAMENT,
            duration_minutes=15,
            notes="Great match!",
        )
        assert match.game_type == GameType.TOURNAMENT
        assert match.duration_minutes == 15
        assert match.notes == "Great match!"

    def test_match_negative_score_validation(self):
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])
        with pytest.raises(ValueError):
            Match(
                id="match1",
                team1=team1,
                team2=team2,
                team1_score=-1,
                team2_score=1,
            )

    @pytest.mark.parametrize(
        "team1_score,team2_score,expected_winner",
        [
            (3, 1, 1),
            (1, 3, 2),
            (2, 2, 2),
            (0, 0, 2),
            (5, 3, 1),
        ],
    )
    def test_winner_team_property(self, team1_score, team2_score, expected_winner):
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])
        match = Match(
            id="match1",
            team1=team1,
            team2=team2,
            team1_score=team1_score,
            team2_score=team2_score,
        )
        assert match.winner_team == expected_winner


class TestTournament:
    """Tests for Tournament model."""

    def test_tournament_creation_minimal(self):
        start_date = datetime(2023, 1, 1, 10, 0)
        tournament = Tournament(
            id="t1",
            name="Test Tournament",
            start_date=start_date,
            participants=["p1", "p2", "p3"],
        )
        assert tournament.id == "t1"
        assert tournament.name == "Test Tournament"
        assert tournament.start_date == start_date
        assert tournament.end_date is None
        assert tournament.participants == ["p1", "p2", "p3"]
        assert tournament.matches == []
        assert tournament.winner is None

    def test_tournament_creation_full(self):
        start_date = datetime(2023, 1, 1, 10, 0)
        end_date = datetime(2023, 1, 1, 18, 0)
        tournament = Tournament(
            id="t1",
            name="Test Tournament",
            start_date=start_date,
            end_date=end_date,
            participants=["p1", "p2"],
            matches=["m1", "m2"],
            winner="p1",
        )
        assert tournament.end_date == end_date
        assert tournament.matches == ["m1", "m2"]
        assert tournament.winner == "p1"


class TestStandcupData:
    """Tests for StandcupData model."""

    def test_standcup_data_creation_empty(self):
        data = StandcupData()
        assert data.players == []
        assert data.matches == []
        assert data.tournaments == []

    def test_standcup_data_creation_with_data(self):
        players = [Player(id="p1", name="Alice")]
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])
        matches = [Match(id="m1", team1=team1, team2=team2, team1_score=3, team2_score=1)]
        tournaments = [
            Tournament(
                id="t1",
                name="Test",
                start_date=datetime.now(),
                participants=["p1", "p2"],
            )
        ]

        data = StandcupData(players=players, matches=matches, tournaments=tournaments)
        assert len(data.players) == 1
        assert len(data.matches) == 1
        assert len(data.tournaments) == 1

    def test_yaml_round_trip(self):
        players = [Player(id="p1", name="Alice"), Player(id="p2", name="Bob")]
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])
        matches = [Match(id="m1", team1=team1, team2=team2, team1_score=3, team2_score=1)]

        data = StandcupData(players=players, matches=matches)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            data.to_yaml(temp_path)
            loaded_data = StandcupData.from_yaml(temp_path)

            assert len(loaded_data.players) == 2
            assert loaded_data.players[0].id == "p1"
            assert loaded_data.players[1].name == "Bob"
            assert len(loaded_data.matches) == 1
            assert loaded_data.matches[0].team1_score == 3
        finally:
            Path(temp_path).unlink()

    def test_to_players_df(self):
        players = [
            Player(id="p1", name="Alice"),
            Player(id="p2", name="Bob"),
        ]
        data = StandcupData(players=players)
        df = data.to_players_df()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["id", "name"]
        assert df.iloc[0]["id"] == "p1"
        assert df.iloc[0]["name"] == "Alice"

    def test_to_matches_df(self):
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2", "p3"])
        match = Match(
            id="m1",
            team1=team1,
            team2=team2,
            team1_score=5,
            team2_score=3,
            game_type=GameType.TOURNAMENT,
            duration_minutes=20,
            notes="Great match",
        )
        data = StandcupData(matches=[match])
        df = data.to_matches_df()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["match_id"] == "m1"
        assert row["team1_players"] == "p1"
        assert row["team2_players"] == "p2, p3"
        assert row["team1_score"] == 5
        assert row["team2_score"] == 3
        assert row["winner_team"] == 1
        assert row["game_type"] == GameType.TOURNAMENT
        assert row["duration_minutes"] == 20
        assert row["notes"] == "Great match"
        assert not row["is_singles"]
        assert row["total_goals"] == 8

    def test_to_player_match_df(self):
        team1 = Team(players=["p1", "p2"])
        team2 = Team(players=["p3"])
        match = Match(
            id="m1",
            team1=team1,
            team2=team2,
            team1_score=4,
            team2_score=2,
        )
        data = StandcupData(matches=[match])
        df = data.to_player_match_df()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3  # 2 players in team1 + 1 player in team2

        # Check team1 players
        team1_rows = df[df["team"] == 1]
        assert len(team1_rows) == 2
        for _, row in team1_rows.iterrows():
            assert row["match_id"] == "m1"
            assert row["goals_for"] == 4
            assert row["goals_against"] == 2
            assert row["won"]
            assert not row["lost"]
            assert row["opponent1"] == "p3"
            assert row["opponent2"] is None
            assert row["is_singles"] is False

        # Check team2 player
        team2_row = df[df["team"] == 2].iloc[0]
        assert team2_row["player_id"] == "p3"
        assert team2_row["teammate"] is None
        assert team2_row["goals_for"] == 2
        assert team2_row["goals_against"] == 4
        assert not team2_row["won"]
        assert team2_row["lost"]

    def test_to_matches_df_empty(self):
        data = StandcupData()
        df = data.to_matches_df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_to_player_match_df_empty(self):
        data = StandcupData()
        df = data.to_player_match_df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
