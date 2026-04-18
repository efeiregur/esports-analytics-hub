import streamlit as st
from valorant_api import RiotAPIClient

def setup_page():
    st.set_page_config(
        page_title="E-Sports Analytics Hub",
        page_icon="🎯",
        layout="wide"
    )

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
                    st.json(result)
        else:
            st.warning("Please enter both Riot ID and Tagline.")

def render_cs2_view():
    st.title("CS2 Tournament Stats")
    st.markdown("---")
    st.warning("Kaggle dataset module is not connected yet.")

def main():
    setup_page()
    
    st.sidebar.title("Navigation")
    game_mode = st.sidebar.radio(
        "Select Environment",
        ["Valorant", "Counter-Strike 2"]
    )
    
    if game_mode == "Valorant":
        render_valorant_view()
    else:
        render_cs2_view()

if __name__ == "__main__":
    main()