"""Chart creation utilities for player statistics."""

from __future__ import annotations

import plotly.graph_objects as go


def create_win_rate_gauge(win_rate: float) -> go.Figure:
    """Create a win rate gauge chart."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=win_rate,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Win Rate %", "font": {"size": 20}},
            delta={"reference": 50},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 70], "color": "yellow"},
                    {"range": [70, 85], "color": "orange"},
                    {"range": [85, 100], "color": "red"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
            },
        )
    )

    fig.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20})

    return fig


def create_goals_chart(goals_for: int, goals_against: int) -> go.Figure:
    """Create a goals comparison chart."""
    fig = go.Figure(
        data=[
            go.Bar(name="Goals For", x=["Goals"], y=[goals_for], marker_color="#00ff00"),
            go.Bar(name="Goals Against", x=["Goals"], y=[goals_against], marker_color="#ff0000"),
        ]
    )

    fig.update_layout(
        title="Goals For vs Against", height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, showlegend=True
    )

    return fig
