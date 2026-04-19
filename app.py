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
            tag_line = st.text_input("Tagline (without #)")

        if st.button("Fetch Player Data"):
            if not game_name or not tag_line:
                st.warning("Please enter both Riot ID and Tagline.")
                return

            api_client = RiotAPIClient()
            
            with st.spinner("Connecting to Valorant Services..."):
                # HenrikDev v3 direkt isimle çalıştığı için direkt maçlara geçiyoruz
                matches = api_client.get_match_history(game_name, tag_line, count=5)
                
                if isinstance(matches, dict) and "error" in matches:
                    st.error(f"API Error: {matches['error']}")
                    st.info("Tip: Your API Key might be expired or the player's privacy settings are restricted.")
                    return

                if not matches:
                    st.warning("No recent match history found for this player.")
                    return

                st.success(f"Player Found: {game_name}#{tag_line}")
                
                all_stats = []
                # HenrikDev v3 veri yapısına göre parsing işlemi
                for match in matches:
                    metadata = match.get('metadata', {})
                    players = match.get('players', {}).get('all_players', [])
                    
                    # Kullanıcıyı maçtaki tüm oyuncular arasında bulalım
                    me = next((p for p in players if p['name'].lower() == game_name.lower()), None)
                    
                    if me:
                        # Kazanan takım kontrolü
                        my_team = me.get('team', '').lower() # 'Red' or 'Blue'
                        teams_data = match.get('teams', {})
                        # Eğer benim takımım kazandıysa is_win True olur
                        is_win = teams_data.get(my_team, {}).get('has_won', False)

                        all_stats.append({
                            "map": metadata.get('map', 'Unknown'),
                            "kills": me['stats'].get('kills', 0),
                            "deaths": me['stats'].get('deaths', 0),
                            "assists": me['stats'].get('assists', 0),
                            "agent_name": me.get('character', 'Unknown'),
                            "hs_percentage": me['stats'].get('headshot_percent', 0),
                            "is_win": is_win
                        })

                if not all_stats:
                    st.error("Stats could not be parsed from match history.")
                    return

                # --- GLOBAL PERFORMANCE SECTION ---
                st.subheader("Overall Performance (Last 5 Games)")
                m1, m2, m3 = st.columns(3)
                
                avg_kills = sum(s['kills'] for s in all_stats) / len(all_stats)
                avg_hs = sum(s['hs_percentage'] for s in all_stats) / len(all_stats)
                win_count = sum(1 for s in all_stats if s['is_win'])
                win_rate = (win_count / len(all_stats)) * 100

                m1.metric("Average Kills", f"{avg_kills:.1f}")
                m2.metric("Average HS %", f"{avg_hs:.1f}%")
                m3.metric("Win Rate", f"{win_rate:.0f}%")

                # --- PERFORMANCE TREND CHART ---
                st.markdown("---")
                st.subheader("Performance Trend")
                chart_data = pd.DataFrame({
                    "Kills": [s['kills'] for s in reversed(all_stats)],
                    "Deaths": [s['deaths'] for s in reversed(all_stats)]
                })
                st.line_chart(chart_data)

                # --- DETAILED MATCH LIST ---
                st.subheader("Detailed Match History")
                for i, stats in enumerate(all_stats):
                    status = "✅ WIN" if stats["is_win"] else "❌ LOSS"
                    label = f"{status} | Game {i+1} | {stats['map']} | {stats['agent_name']}"
                    
                    with st.expander(label):
                        c1, c2, c3, c4, c5 = st.columns(5)
                        c1.metric("Kills", stats["kills"])
                        c2.metric("Deaths", stats["deaths"])
                        c3.metric("Assists", stats["assists"])
                        
                        kda = round((stats["kills"] + stats["assists"]) / max(1, stats["deaths"]), 2)
                        c4.metric("KDA Ratio", kda)
                        c5.metric("HS %", f"{stats['hs_percentage']}%")

    with tab_esports:
        st.subheader("Live & Upcoming VCT Matches")
        
        selected_region = st.selectbox(
            "Filter by Region",
            ["All Regions", "EMEA", "Americas", "Pacific", "CN", "Game Changers"]
        )
        
        if st.button("Refresh Esports Schedule"):
            api_client = RiotAPIClient()
            with st.spinner("Fetching global esports data..."):
                schedule = api_client.get_esports_schedule()
                
                if isinstance(schedule, dict) and "error" in schedule:
                    st.error(schedule["error"])
                elif not schedule:
                    st.warning("No matches scheduled at the moment.")
                else:
                    filtered_schedule = []
                    for match in schedule:
                        event_name = match.get("league", {}).get("name", "Valorant Tournament")
                        if selected_region == "All Regions" or selected_region.lower() in event_name.lower():
                            filtered_schedule.append(match)

                    if not filtered_schedule:
                        st.info(f"No matches found for {selected_region}.")
                    else:
                        st.success(f"Displaying top {min(15, len(filtered_schedule))} matches")
                        for match in filtered_schedule[:15]:
                            match_state = match.get("state", "upcoming").upper()
                            team1 = match.get("match", {}).get("teams", [{}])[0].get("name", "TBD")
                            team2 = match.get("match", {}).get("teams", [{}, {}])[1].get("name", "TBD")
                            event_name = match.get("league", {}).get("name", "Valorant Tournament")
                            
                            state_color = "#00FF00" if match_state == "LIVE" else "#FF4B4B" if match_state == "COMPLETED" else "gray"
                            
                            with st.container():
                                st.markdown(f"**{event_name}**")
                                st.markdown(f"*{team1}* **VS** *{team2}* | <span style='color:{state_color};'>[{match_state}]</span>", unsafe_allow_html=True)
                                st.markdown("---")

def render_cs2_view():
    st.title("Counter-Strike 2 Analytics")
    st.markdown("---")
    # FaceIt implementasyonun zaten iyiydi, dokunmadım.
    # ... (FaceIt kodların buraya gelecek)

def render_compare_view():
    st.title("Player Comparison: Valorant")
    st.markdown("---")
    # ... (Compare Mode kodların buraya gelecek)

def main():
    setup_page()
    render_header()
    selected_env = render_sidebar()

    if selected_env == "Valorant":
        render_valorant_view()
    elif selected_env == "Counter-Strike 2":
        render_cs2_view()
    elif selected_env == "Compare Mode":
        render_compare_view()

if __name__ == "__main__":
    main()