"""Pages package for Standcup - Table Football Tracker."""

from .dashboard import render_overview_page
from .head_to_head import render_head_to_head_page
from .leaderboard import render_leaderboard_page
from .match_history import render_match_history_page
from .match_maker import render_match_maker_page
from .player_stats import render_player_stats_page

__all__ = [
    "render_head_to_head_page",
    "render_leaderboard_page",
    "render_match_history_page",
    "render_match_maker_page",
    "render_overview_page",
    "render_player_stats_page",
]
