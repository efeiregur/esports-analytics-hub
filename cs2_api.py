import streamlit as st
api_key = st.secrets["RIOT_API_KEY"]
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class FaceItAPIClient:
    def __init__(self):
        self.api_key = os.getenv("FACEIT_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        self.base_url = "https://open.faceit.com/data/v4"

    def get_player_details(self, nickname):
        url = f"{self.base_url}/players"
        params = {"nickname": nickname}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Player not found. Status: {response.status_code}"}

    def get_player_stats(self, player_id):
        url = f"{self.base_url}/players/{player_id}/stats/cs2"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to fetch CS2 stats. Status: {response.status_code}"}

    def get_player_match_history(self, player_id, limit=5):
        """
        Fetches the recent match history and detailed individual stats for a specific player.
        Requires a two-step API call process due to FaceIt's endpoint architecture.
        """
        # Endpoint 1: Get the list of recent matches
        history_url = f"{self.base_url}/players/{player_id}/history"
        params = {
            "game": "cs2",
            "offset": 0,
            "limit": limit
        }
        
        try:
            response = requests.get(history_url, headers=self.headers, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to fetch match history (Status: {response.status_code})"}
            
            matches = response.json().get("items", [])
            match_details = []
            
            for match in matches:
                match_id = match.get("match_id")
                
                # Endpoint 2: Fetch detailed scoreboard for each specific match
                stats_url = f"{self.base_url}/matches/{match_id}/stats"
                stats_response = requests.get(stats_url, headers=self.headers)
                
                if stats_response.status_code != 200:
                    continue # Skip this match if detailed stats are unavailable
                    
                stats_data = stats_response.json()
                
                # FaceIt nests match data deeply inside a 'rounds' array
                if not stats_data.get("rounds"):
                    continue
                    
                round_data = stats_data["rounds"][0]
                teams = round_data.get("teams", [])
                
                player_stat_block = None
                player_team_id = None
                winner_team_id = round_data.get("round_stats", {}).get("Winner")
                
                # Scan both teams to find our specific player's data block
                for team in teams:
                    for player in team.get("players", []):
                        if player.get("player_id") == player_id:
                            player_stat_block = player.get("player_stats", {})
                            player_team_id = team.get("team_id")
                            break
                    if player_stat_block:
                        break # Stop searching once we find our guy
                        
                if not player_stat_block:
                    continue
                    
                # Compile the final dictionary expected by the UI (app.py)
                match_details.append({
                    "is_win": player_team_id == winner_team_id,
                    "map": round_data.get("round_stats", {}).get("Map", "Unknown"),
                    "score": round_data.get("round_stats", {}).get("Score", "N/A"),
                    "kills": player_stat_block.get("Kills", "0"),
                    "deaths": player_stat_block.get("Deaths", "0"),
                    "headshots": player_stat_block.get("Headshots", "0")
                })
                
            return match_details
            
        except Exception as e:
            return {"error": str(e)}