"""Pages package for Standcup - Table Football Tracker."""

from standcup.pages.dashboard import render_overview_page
from standcup.pages.head_to_head import render_head_to_head_page
from standcup.pages.match_history import render_match_history_page
from standcup.pages.match_maker import render_match_maker_page
from standcup.pages.player_stats import render_player_stats_page

__all__ = [
    "render_head_to_head_page",
    "render_match_history_page",
    "render_match_maker_page",
    "render_overview_page",
    "render_player_stats_page",
]
