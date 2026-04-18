import streamlit as st
import pandas as pd
from valorant_api import RiotAPIClient

def setup_page():
    st.set_page_config(
        page_title="E-Sports Analytics Hub",
        page_icon="🎯",
        layout="wide"
    )

def render_sidebar():
    with st.sidebar:
        st.title("Navigation")
        environment = st.radio(
            "Select Environment",
            ["Valorant", "Counter-Strike 2"]
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
                
                # Check if we got a list or an error dict
                if isinstance(match_ids, dict) and "error" in match_ids:
                    st.error(f"API Access Denied: {match_ids['error']}")
                    st.info("Tip: Your API Key might be expired or the player's privacy settings are restricted.")
                    return

                if not match_ids:
                    st.warning("No recent match history found for this player.")
                    return

                # Fetch details for all matches
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
    st.title("CS2 Tournament Stats")
    st.markdown("---")
    st.info("CS2 Analytics Module is under development.")

def main():
    setup_page()
    selected_env = render_sidebar()

    if selected_env == "Valorant":
        render_valorant_view()
    else:
        render_cs2_view()

if __name__ == "__main__":
    main()