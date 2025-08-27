"""Head-to-head analysis page for Standcup."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from standcup.models import StandcupData
from standcup.utils import calculate_head_to_head
from standcup.wilson_score import get_wilson_win_rate


def get_rivalry_status(h2h_stats: dict) -> tuple[str, str]:
    """Generate rivalry description based on head-to-head stats."""
    total = h2h_stats["total_matches"]
    p1_wins = h2h_stats["p1_wins"]
    p2_wins = h2h_stats["p2_wins"]

    if total == 0:
        return "🤝 Fresh Rivalry", "The stage is set for an epic showdown!"

    win_diff = abs(p1_wins - p2_wins)

    if total >= 20:
        rivalry_level = "🏆 Legendary Rivalry"
    elif total >= 10:
        rivalry_level = "⚔️ Epic Rivalry"
    elif total >= 5:
        rivalry_level = "🔥 Heated Rivalry"
    else:
        rivalry_level = "🌱 Growing Rivalry"

    if win_diff <= 1 and total >= 5:
        description = f"Dead even at {total} matches! This is what championship rivalries are made of!"
    elif win_diff <= 2 and total >= 8:
        description = f"Tight competition across {total} battles - neither player gives an inch!"
    elif win_diff > total * 0.6:
        description = "One-sided domination, but every rivalry has its comeback story waiting!"
    else:
        description = f"Classic back-and-forth battle across {total} matches - the competition never ends!"

    return rivalry_level, description


def get_head_to_head_personality(player_name: str, wins: int, total: int) -> str:
    """Generate personality text for player performance."""
    if total == 0:
        return "Ready to battle! 🚀"

    win_rate = get_wilson_win_rate(wins, total, method="center")

    if win_rate >= 80:
        return f"Dominating! 👑 ({wins}/{total})"
    elif win_rate >= 70:
        return f"In control! 🔥 ({wins}/{total})"
    elif win_rate >= 60:
        return f"Ahead! ⚡ ({wins}/{total})"
    elif win_rate >= 55:
        return f"Slight edge! 🎯 ({wins}/{total})"
    elif win_rate >= 45:
        return f"Even match! ⚖️ ({wins}/{total})"
    elif win_rate >= 30:
        return f"Fighting back! 💪 ({wins}/{total})"
    else:
        return f"Comeback time! 🚀 ({wins}/{total})"


def create_head_to_head_chart(player1: str, player2: str, p1_win_rate: float, p2_win_rate: float) -> go.Figure:
    """Create a head-to-head win rate chart."""
    # Determine colors based on performance
    p1_color = "gold" if p1_win_rate > p2_win_rate else "lightblue" if p1_win_rate == p2_win_rate else "lightcoral"
    p2_color = "gold" if p2_win_rate > p1_win_rate else "lightblue" if p2_win_rate == p1_win_rate else "lightcoral"

    fig = go.Figure(
        data=[
            go.Bar(
                name=f"🔴 {player1}",
                x=[player1],
                y=[p1_win_rate],
                marker_color=p1_color,
                text=f"{p1_win_rate:.1f}%",
                textposition="auto",
            ),
            go.Bar(
                name=f"🔵 {player2}",
                x=[player2],
                y=[p2_win_rate],
                marker_color=p2_color,
                text=f"{p2_win_rate:.1f}%",
                textposition="auto",
            ),
        ]
    )

    fig.update_layout(
        title=f"⚔️ {player1} vs {player2} - Championship Showdown",
        yaxis_title="Win Rate (%)",
        height=400,
        yaxis={"range": [0, 100]},
        showlegend=False,
    )

    return fig


def render_head_to_head_page(data: StandcupData) -> None:
    """Render the head-to-head analysis page."""
    st.header("⚔️ Rivalry Central")
    st.markdown(
        "🏆 **Where legends clash and rivalries are born!** Select two warriors and witness their epic battle history unfold."
    )

    if len(data.players) < 2:
        st.warning("🎮 **Assemble the fighters!**")
        st.info(
            "🚀 You need at least 2 players to witness epic head-to-head battles. Recruit more warriors for your league!"
        )
        return

    # Player selection
    col1, col2 = st.columns(2)

    player_names = [p.name for p in data.players]

    with col1:
        player1 = st.selectbox("Player 1", player_names, index=0)

    with col2:
        player2_options = [p for p in player_names if p != player1]
        player2 = st.selectbox("Player 2", player2_options, index=0 if player2_options else None)

    if not (player1 and player2 and player1 != player2):
        return

    # Get player IDs
    player1_id = next(p.id for p in data.players if p.name == player1)
    player2_id = next(p.id for p in data.players if p.name == player2)

    # Calculate head-to-head stats
    h2h_stats = calculate_head_to_head(data, player1_id, player2_id)

    if h2h_stats["total_matches"] == 0:
        st.info(f"🎆 **{player1} vs {player2} - The rivalry awaits!**")
        st.markdown("""
        🚀 **First battle pending!** These two legends haven't faced off yet, but when they do, sparks will fly!

        🎯 Who will strike first? The anticipation is building...
        """)
        return

    # Get rivalry status
    rivalry_level, rivalry_desc = get_rivalry_status(h2h_stats)

    st.markdown(f"### {rivalry_level}")
    st.markdown(f"*{rivalry_desc}*")

    st.divider()

    # Display results with personality
    col1, col2, col3 = st.columns(3)

    with col1:
        p1_personality = get_head_to_head_personality(player1, h2h_stats["p1_wins"], h2h_stats["total_matches"])
        st.metric(f"🔴 {player1}", h2h_stats["p1_wins"], delta=p1_personality)

    with col2:
        st.metric("⚔️ Total Matches", h2h_stats["total_matches"], delta="Epic battles!")

    with col3:
        p2_personality = get_head_to_head_personality(player2, h2h_stats["p2_wins"], h2h_stats["total_matches"])
        st.metric(f"🔵 {player2}", h2h_stats["p2_wins"], delta=p2_personality)

    # Win percentage chart
    if h2h_stats["total_matches"] > 0:
        p1_win_rate = get_wilson_win_rate(h2h_stats["p1_wins"], h2h_stats["total_matches"], method="center")
        p2_win_rate = get_wilson_win_rate(h2h_stats["p2_wins"], h2h_stats["total_matches"], method="center")

        st.markdown("### 📊 Battle Statistics")
        st.markdown("*The numbers that tell the story of this epic rivalry*")
        st.plotly_chart(create_head_to_head_chart(player1, player2, p1_win_rate, p2_win_rate), width="stretch")

        # Add some fun facts
        total_matches = h2h_stats["total_matches"]
        if total_matches >= 10:
            st.markdown("#### 🎆 Rivalry Facts")
            col1, col2 = st.columns(2)

            with col1:
                st.info(f"📈 **{total_matches} epic battles** have shaped this rivalry!")

            with col2:
                win_diff = abs(h2h_stats["p1_wins"] - h2h_stats["p2_wins"])
                if win_diff <= 2:
                    st.success("⚔️ **Ultra-competitive!** This rivalry is too close to call!")
                elif win_diff <= 5:
                    st.warning("🔥 **Heating up!** The momentum can shift any moment!")
                else:
                    st.error("💥 **Domination mode!** But every champion has their challenger!")
