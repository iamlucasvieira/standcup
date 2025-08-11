"""Tests for Standcup models."""

import tempfile
from datetime import datetime, timedelta
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
            ("champion_2024", "Maria Garcia"),
            ("rookie_001", "Alex Chen"),
        ],
    )
    def test_player_creation_parametrized(self, player_id, name):
        player = Player(id=player_id, name=name)
        assert player.id == player_id
        assert player.name == name

    def test_player_unicode_names(self):
        """Test players with international names and special characters."""
        players = [
            Player(id="p1", name="José María"),
            Player(id="p2", name="Björk Guðmundsdóttir"),
            Player(id="p3", name="李小龙"),
            Player(id="p4", name="François-Xavier"),
        ]

        for player in players:
            assert len(player.name) > 0
            assert player.id.startswith("p")


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

    def test_team_dynamic_players(self):
        """Test team with dynamic player assignments."""
        team = Team(players=["captain", "striker"])
        assert len(team.players) == 2

        # Simulate player substitution
        new_team = Team(players=["captain", "defender"])
        assert new_team.players == ["captain", "defender"]
        assert new_team.is_singles is False


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
            (10, 0, 1),  # Dominant win
            (0, 10, 2),  # Dominant loss
            (15, 14, 1),  # Close win
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

    def test_match_duration_edge_cases(self):
        """Test match duration with various time scenarios."""
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])

        # Very short match
        quick_match = Match(
            id="quick",
            team1=team1,
            team2=team2,
            team1_score=3,
            team2_score=0,
            duration_minutes=2,
        )
        assert quick_match.duration_minutes == 2

        # Long match
        marathon_match = Match(
            id="marathon",
            team1=team1,
            team2=team2,
            team1_score=15,
            team2_score=14,
            duration_minutes=120,
        )
        assert marathon_match.duration_minutes == 120

    def test_match_notes_variations(self):
        """Test various note formats and content."""
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])

        notes_variations = [
            "Great match!",
            "Controversial referee decision",
            "Amazing comeback from 0-5 to 10-5",
            "First tournament match",
            "Practice session",
            "🏆 Championship final",
            "New player debut",
        ]

        for note in notes_variations:
            match = Match(
                id=f"match_{note[:10]}",
                team1=team1,
                team2=team2,
                team1_score=5,
                team2_score=3,
                notes=note,
            )
            assert match.notes == note

    def test_match_date_handling(self):
        """Test match date creation and handling."""
        team1 = Team(players=["p1"])
        team2 = Team(players=["p2"])

        # Test with specific date
        specific_date = datetime(2024, 12, 25, 15, 30)
        match = Match(
            id="christmas_match",
            date=specific_date,
            team1=team1,
            team2=team2,
            team1_score=5,
            team2_score=3,
        )
        assert match.date == specific_date

        # Test with default date (should be close to now)
        default_match = Match(
            id="default_date",
            team1=team1,
            team2=team2,
            team1_score=5,
            team2_score=3,
        )
        time_diff = abs((datetime.now() - default_match.date).total_seconds())
        assert time_diff < 10  # Should be within 10 seconds


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

    def test_tournament_scenarios(self):
        """Test various tournament scenarios."""
        start_date = datetime(2024, 6, 1, 9, 0)

        # Single elimination tournament
        single_elim = Tournament(
            id="single_elim",
            name="Single Elimination Championship",
            start_date=start_date,
            participants=["p1", "p2", "p3", "p4"],
        )
        assert len(single_elim.participants) == 4

        # League tournament
        league_tournament = Tournament(
            id="league",
            name="Round Robin League",
            start_date=start_date,
            participants=["p1", "p2", "p3", "p4", "p5", "p6"],
        )
        assert len(league_tournament.participants) == 6

        # Championship with winner
        championship = Tournament(
            id="championship",
            name="World Cup Final",
            start_date=start_date,
            end_date=start_date + timedelta(hours=8),
            participants=["p1", "p2"],
            winner="p1",
        )
        assert championship.winner == "p1"
        assert championship.end_date is not None
        assert championship.end_date > championship.start_date

    def test_tournament_duration_calculation(self):
        """Test tournament duration calculations."""
        start_date = datetime(2024, 1, 1, 9, 0)
        end_date = datetime(2024, 1, 3, 18, 0)

        tournament = Tournament(
            id="long_tournament",
            name="3-Day Championship",
            start_date=start_date,
            end_date=end_date,
            participants=["p1", "p2", "p3", "p4"],
        )

        assert tournament.end_date is not None
        duration = tournament.end_date - tournament.start_date
        assert duration.days == 2  # 3 days total, but 2 full days difference
        assert duration.seconds > 0


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

    def test_complex_scenario_analysis(self):
        """Test complex scenario with multiple players, matches, and tournaments."""
        # Create a realistic tournament scenario
        players = [
            Player(id="champion", name="Tournament Champion"),
            Player(id="runner_up", name="Runner Up"),
            Player(id="semifinalist1", name="Semifinalist 1"),
            Player(id="semifinalist2", name="Semifinalist 2"),
            Player(id="quarterfinalist1", name="Quarterfinalist 1"),
            Player(id="quarterfinalist2", name="Quarterfinalist 2"),
            Player(id="quarterfinalist3", name="Quarterfinalist 3"),
            Player(id="quarterfinalist4", name="Quarterfinalist 4"),
        ]

        # Create tournament matches
        matches = []
        match_id = 1

        # Quarterfinals
        for i in range(0, 8, 2):
            team1 = Team(players=[players[i].id])
            team2 = Team(players=[players[i + 1].id])
            match = Match(
                id=f"qf_{match_id}",
                team1=team1,
                team2=team2,
                team1_score=5,
                team2_score=3,
                game_type=GameType.TOURNAMENT,
                duration_minutes=15,
            )
            matches.append(match)
            match_id += 1

        # Semifinals
        for i in range(0, 4, 2):
            team1 = Team(players=[players[i].id])
            team2 = Team(players=[players[i + 1].id])
            match = Match(
                id=f"sf_{match_id}",
                team1=team1,
                team2=team2,
                team1_score=5,
                team2_score=4,
                game_type=GameType.TOURNAMENT,
                duration_minutes=20,
            )
            matches.append(match)
            match_id += 1

        # Final
        final_team1 = Team(players=[players[0].id])
        final_team2 = Team(players=[players[1].id])
        final_match = Match(
            id=f"final_{match_id}",
            team1=final_team1,
            team2=final_team2,
            team1_score=10,
            team2_score=8,
            game_type=GameType.TOURNAMENT,
            duration_minutes=30,
            notes="Epic championship final!",
        )
        matches.append(final_match)

        # Create tournament
        tournament = Tournament(
            id="championship_2024",
            name="2024 Table Football Championship",
            start_date=datetime(2024, 12, 1, 9, 0),
            end_date=datetime(2024, 12, 1, 18, 0),
            participants=[p.id for p in players],
            matches=[m.id for m in matches],
            winner="champion",
        )

        # Create data container
        data = StandcupData(players=players, matches=matches, tournaments=[tournament])

        # Test data integrity
        assert len(data.players) == 8
        assert len(data.matches) == 7  # 4 QF + 2 SF + 1 Final
        assert len(data.tournaments) == 1

        # Test match analysis
        matches_df = data.to_matches_df()
        assert len(matches_df) == 7

        # Test player analysis
        player_match_df = data.to_player_match_df()
        assert len(player_match_df) == 14  # 2 players per match * 7 matches

        # Verify tournament winner
        assert tournament.winner == "champion"
        assert len(tournament.participants) == 8
        assert len(tournament.matches) == 7

    def test_data_validation_edge_cases(self):
        """Test edge cases and validation scenarios."""
        # Test with very long names and IDs
        long_name_player = Player(
            id="very_long_player_id_that_exceeds_normal_length_expectations",
            name="Dr. Professor Sir Lord Baron von der Longest Name in the Universe III, Esq.",
        )

        # Test with special characters in names
        special_char_player = Player(id="special_chars", name="José María O'Connor-Smith 🏆⚽")

        # Test with minimal valid data
        minimal_team = Team(players=["p1"])
        minimal_match = Match(
            id="minimal",
            team1=minimal_team,
            team2=minimal_team,
            team1_score=0,
            team2_score=0,
        )

        # Test with maximum valid data
        max_team = Team(players=["p1", "p2"])
        max_match = Match(
            id="maximum",
            team1=max_team,
            team2=max_team,
            team1_score=999,
            team2_score=998,
            game_type=GameType.LEAGUE,
            duration_minutes=999,
            notes="A" * 1000,  # Very long note
        )

        # Create data container with edge cases
        data = StandcupData(
            players=[long_name_player, special_char_player],
            matches=[minimal_match, max_match],
        )

        # Verify data integrity
        assert len(data.players) == 2
        assert len(data.matches) == 2
        assert data.players[0].name == long_name_player.name
        assert data.players[1].name == special_char_player.name
        assert data.matches[0].team1_score == 0
        assert data.matches[1].team1_score == 999
