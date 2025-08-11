"""Player insights module for personality analysis and performance insights."""

from .performance_analyzer import render_player_insights
from .personality_traits import get_player_personality

__all__ = [
    "get_player_personality",
    "render_player_insights",
]
