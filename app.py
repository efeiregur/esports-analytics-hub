import streamlit as st
import pandas as pd
from valorant_api import RiotAPIClient
from cs2_api import FaceItAPIClient

def setup_page():
    st.set_page_config(
        page_title="E-Sports Analytics Hub",
        page_icon="logo.png", # Points to your custom local image file
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
    st.title("Valorant Match Analytics")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        game_name = st.text_input("Riot ID (e.g. qardesh0)")
    with col2:
        tag_line = st.text_input("Tagline (without #, e.g. 00000)")

    if st.button("Fetch Player Data"):
        if not game_name or not tag_line:
            st.warning("Please enter both Riot ID and Tagline.")
            return

        api_client = RiotAPIClient()
        
        with st.spinner("Connecting to Riot Servers..."):
            account_data = api_client.get_player_puuid(game_name, tag_line)

            if "error" in account_data:
                st.error(f"Account Error: {account_data['error']}")
                return

            puuid = account_data["puuid"]
            st.success(f"Player Found: {game_name}#{tag_line}")
            
            with st.spinner("Analyzing match history..."):
                match_ids = api_client.get_match_history(puuid, count=5)
                
                if isinstance(match_ids, dict) and "error" in match_ids:
                    st.error(f"API Access Denied: {match_ids['error']}")
                    st.info("Tip: Your API Key might be expired or the player's privacy settings are restricted.")
                    return

                if not match_ids:
                    st.warning("No recent match history found for this player.")
                    return

                all_stats = []
                for mid in match_ids:
                    data = api_client.get_player_match_stats(mid, puuid)
                    if "error" not in data:
                        all_stats.append(data)

                if not all_stats:
                    st.error("Match history exists, but detailed stats are restricted by Riot.")
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

def render_cs2_view():
    st.title("Counter-Strike 2 Analytics")
    st.markdown("---")

    # FaceIt API requires exact case-sensitive nicknames
    col1, col2 = st.columns(2)
    with col1:
        faceit_name = st.text_input("FaceIt Nickname (e.g. s1mple)")
    with col2:
        platform = st.selectbox("Platform", ["FaceIt (Official)"])

    if st.button("Fetch CS2 Data"):
        if faceit_name:
            with st.spinner("Connecting to FaceIt Servers..."):
                api_client = FaceItAPIClient()
                
                # Step 1: Fetch player ID and base stats
                details = api_client.get_player_details(faceit_name)
                
                if "error" in details:
                    st.error(f"API Error: {details['error']}")
                    st.info("Tip: FaceIt nicknames are case-sensitive. Make sure you typed it exactly right.")
                    return
                
                player_id = details.get("player_id")
                real_name = details.get("nickname")
                
                # Extract ELO and Skill Level
                cs2_data = details.get("games", {}).get("cs2", {})
                elo = cs2_data.get("faceit_elo", "Unranked")
                level = cs2_data.get("skill_level", "N/A")
                
                st.success(f"Player Found: {real_name} | FaceIt Level: {level} | ELO: {elo}")
                
                # Step 2: Fetch lifetime stats using the hidden player ID
                with st.spinner("Analyzing lifetime stats..."):
                    stats = api_client.get_player_stats(player_id)
                    
                    if "error" in stats:
                        st.warning("Player found, but CS2 stats are missing or private.")
                        return
                    
                    st.markdown("---")
                    st.subheader(f"Lifetime CS2 Metrics")
                    
                    # Extract data from the 'lifetime' dictionary
                    lifetime = stats.get("lifetime", {})
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Average K/D", lifetime.get("Average K/D Ratio", "N/A"))
                    m2.metric("Win Rate", f"{lifetime.get('Win Rate %', 'N/A')}%")
                    m3.metric("Headshot %", f"{lifetime.get('Average Headshots %', 'N/A')}%")
                    m4.metric("Total Matches", lifetime.get("Matches", "N/A"))

        else:
            st.warning("Please enter a valid FaceIt Nickname.")

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
        if p1_name and p1_tag and p2_name and p2_tag:
            st.balloons()
            st.info("Comparison engine is ready! Next step: Wire up the Riot API here.")
            # Placeholder for comparison logic
            c1, c2, c3 = st.columns(3)
            c1.metric(f"{p1_name}'s K/D", "1.2") 
            c2.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
            c3.metric(f"{p2_name}'s K/D", "1.1", delta="-0.1")
        else:
            st.warning("Fill in all fields for both players!")

def main():
    setup_page() # Critical: Moved to the very top!
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