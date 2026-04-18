import streamlit as st
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
        if game_name and tag_line:
            with st.spinner("Fetching data from Riot Servers..."):
                api_client = RiotAPIClient()
                result = api_client.get_player_puuid(game_name, tag_line)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("Player found successfully!")
                    puuid = result["puuid"]
                    
                    with st.spinner("Loading recent matches..."):
                        matches = api_client.get_match_history(puuid, count=5)
                        st.write(matches)
                        
                        if isinstance(matches, list) and len(matches) > 0:
                            st.subheader("Match History (Last 5 Games)")
                            
                            for i, match_id in enumerate(matches):
                                stats = api_client.get_player_match_stats(match_id, puuid)
                                
                                if "error" not in stats:
                                    # Expanders labeled with Map and Agent
                                    with st.expander(f"Game {i+1} | Map: {stats['map']} | Agent: {stats['agent_name']}"):
                                        col_a, col_b, col_c, col_d, col_e = st.columns(5)
                                        
                                        col_a.metric("Kills", stats["kills"])
                                        col_b.metric("Deaths", stats["deaths"])
                                        col_c.metric("Assists", stats["assists"])
                                        
                                        kda_ratio = round((stats["kills"] + stats["assists"]) / max(1, stats["deaths"]), 2)
                                        col_d.metric("KDA Ratio", kda_ratio)
                                        
                                        col_e.metric("Headshot %", f"{stats['hs_percentage']}%")
                                else:
                                    st.error(f"Data unavailable for match: {match_id}")
                        else:
                            st.warning("No recent match history found for this player.")
        else:
            st.warning("Please enter both Riot ID and Tagline.")

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