import streamlit as st
import pandas as pd
from valorant_api import RiotAPIClient
from cs2_api import FaceItAPIClient

def setup_page():
    st.set_page_config(
        page_title="E-Sports Analytics Hub",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>ESPORTS ANALYTICS HUB</h1>", unsafe_allow_html=True)
    st.markdown("---")

def render_sidebar():
    with st.sidebar:
        st.title("Navigation")
        environment = st.radio(
            "Select Environment",
            ["Valorant", "Counter-Strike 2", "Compare Mode"]
        )
        return environment

def render_valorant_view():
    st.title("Valorant Hub: Analytics & Esports")
    st.markdown("---")

    tab_player, tab_esports = st.tabs(["🎯 Player Analytics", "🏆 VCT Tournaments"])

    with tab_player:
        col1, col2 = st.columns(2)
        with col1:
            game_name = st.text_input("Riot ID")
        with col2:
            tag_line = st.text_input("Tagline")

        if st.button("Fetch Player Data"):
            if not game_name or not tag_line:
                st.warning("Please enter both Riot ID and Tagline.")
                return

            api_client = RiotAPIClient()
            with st.spinner("Connecting to Valorant Services..."):
                matches = api_client.get_match_history(game_name, tag_line, count=5)
                
                if isinstance(matches, dict) and "error" in matches:
                    st.error(f"API Error: {matches['error']}")
                    return

                if not matches:
                    st.warning("No recent match history found.")
                    return

                st.success(f"Player Found: {game_name}#{tag_line}")
                
                all_stats = []
                for match in matches:
                    players = match.get('players', {}).get('all_players', [])
                    me = next((p for p in players if p['name'].lower() == game_name.lower()), None)
                    if me:
                        my_team = me.get('team', '').lower()
                        is_win = match.get('teams', {}).get(my_team, {}).get('has_won', False)
                        all_stats.append({
                            "map": match.get('metadata', {}).get('map', 'Unknown'),
                            "kills": me['stats'].get('kills', 0),
                            "deaths": me['stats'].get('deaths', 0),
                            "assists": me['stats'].get('assists', 0),
                            "agent_name": me.get('character', 'Unknown'),
                            "hs_percentage": me['stats'].get('headshot_percent', 0),
                            "is_win": is_win
                        })

                if all_stats:
                    st.subheader("Overall Performance (Last 5 Games)")
                    m1, m2, m3 = st.columns(3)
                    avg_kills = sum(s['kills'] for s in all_stats) / len(all_stats)
                    avg_hs = sum(s['hs_percentage'] for s in all_stats) / len(all_stats)
                    win_rate = (sum(1 for s in all_stats if s['is_win']) / len(all_stats)) * 100
                    m1.metric("Average Kills", f"{avg_kills:.1f}")
                    m2.metric("Average HS %", f"{avg_hs:.1f}%")
                    m3.metric("Win Rate", f"{win_rate:.0f}%")

                    chart_data = pd.DataFrame({
                        "Kills": [s['kills'] for s in reversed(all_stats)],
                        "Deaths": [s['deaths'] for s in reversed(all_stats)]
                    })
                    st.line_chart(chart_data)

    with tab_esports:
        st.subheader("Live & Upcoming VCT Matches")
        # (Esports kodların aynen burada kalacak...)

def render_cs2_view():
    st.title("Counter-Strike 2 Analytics")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        faceit_name = st.text_input("FaceIt Nickname")
    with col2:
        platform = st.selectbox("Platform", ["FaceIt (Official)"])

    if st.button("Fetch CS2 Data"):
        if faceit_name:
            api_client = FaceItAPIClient()
            
            with st.spinner("Connecting to FaceIt Servers..."):
                details = api_client.get_player_details(faceit_name)
                
                if "error" in details:
                    st.error(f"API Error: {details['error']}")
                    return
                
                player_id = details.get("player_id")
                real_name = details.get("nickname")
                cs2_data = details.get("games", {}).get("cs2", {})
                elo = cs2_data.get("faceit_elo", "Unranked")
                level = cs2_data.get("skill_level", "N/A")
                
                st.success(f"Player Found: {real_name} | Level: {level} | ELO: {elo}")
                
                stats = api_client.get_player_stats(player_id)
                
                if "error" not in stats:
                    st.markdown("---")
                    st.subheader("Lifetime CS2 Metrics")
                    lifetime = stats.get("lifetime", {})
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Avg K/D", lifetime.get("Average K/D Ratio", "N/A"))
                    m2.metric("Win Rate", f"{lifetime.get('Win Rate %', 'N/A')}%")
                    m3.metric("Headshot %", f"{lifetime.get('Average Headshots %', 'N/A')}%")
                    m4.metric("Total Matches", lifetime.get("Matches", "N/A"))

                # İŞTE BURAYI SİLMİŞİM, GERİ GELDİ:
                with st.spinner("Retrieving recent matches..."):
                    history = api_client.get_player_match_history(player_id, limit=5)
                    
                    if history and isinstance(history, list):
                        st.markdown("---")
                        st.subheader("Recent Matches (Last 5 Games)")
                        
                        for i, match in enumerate(history):
                            status = "🏆 WIN" if match.get("is_win") else "💀 LOSS"
                            map_name = match.get("map", "Unknown Map")
                            score = match.get("score", "N/A")
                            
                            label = f"{status} | Game {i+1} | {map_name} | Score: {score}"
                            
                            with st.expander(label):
                                c1, c2, c3, c4 = st.columns(4)
                                k = int(match.get("kills", 0))
                                d = max(1, int(match.get("deaths", 1)))
                                c1.metric("Kills", k)
                                c2.metric("Deaths", d)
                                c3.metric("K/D Ratio", round(k/d, 2))
                                c4.metric("Headshots", match.get("headshots", "N/A"))
                    else:
                        st.warning("No recent match history found.")
        else:
            st.warning("Please enter a FaceIt Nickname.")

def render_compare_view():
    st.title("Player Comparison: Valorant")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Player 1")
        p1_name = st.text_input("Riot ID 1")
        p1_tag = st.text_input("Tag 1")
    with col2:
        st.subheader("Player 2")
        p2_name = st.text_input("Riot ID 2")
        p2_tag = st.text_input("Tag 2")

    if st.button("Battle of Stats!"):
        if p1_name and p2_name:
            st.balloons()
            st.info("Comparison Mode is active! Both player data will be displayed side-by-side.")
            # Karşılaştırma mantığını buraya ekleyebilirsin

def main():
    setup_page()
    render_header()
    selected_env = render_sidebar()
    if selected_env == "Valorant": render_valorant_view()
    elif selected_env == "Counter-Strike 2": render_cs2_view()
    elif selected_env == "Compare Mode": render_compare_view()

if __name__ == "__main__":
    main()