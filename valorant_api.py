import streamlit as st
import requests

class RiotAPIClient:
    def __init__(self):
        # Fetching Riot API key directly from Streamlit Secrets
        self.api_key = st.secrets["RIOT_API_KEY"]
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def get_player_puuid(self, game_name, tag_line):
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Connection failed with status: {response.status_code}"}

    def get_match_history(self, game_name, tag_line, count=5):
        """
        Fetches match history using HenrikDev v3 (by-name) which is more reliable 
        for development keys.
        """
        # We use name and tag instead of PUUID for better stability
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{game_name}/{tag_line}"
        
        headers = {
            "Authorization": st.secrets["HENRIK_API_KEY"]
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                matches = response.json().get('data', [])
                # Returning the full match objects so we can extract stats easily
                return matches[:count]
            else:
                return {"error": f"HenrikDev Error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}

    def get_agent_mapping(self):
        # Fetches agent UUIDs to clear names mapping from a public API
        url = "https://valorant-api.com/v1/agents?isPlayableCharacter=true"
        response = requests.get(url)
        if response.status_code == 200:
            agents = response.json().get('data', [])
            return {agent['uuid']: agent['displayName'] for agent in agents}
        return {}

    def get_player_match_stats(self, match_id, puuid):
        url = f"https://europe.api.riotgames.com/val/match/v1/matches/{match_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            match_data = response.json()
            map_name = match_data['matchInfo']['mapId']
            agent_mapping = self.get_agent_mapping()
            
            # Find which team the player was on
            player_team = ""
            for player in match_data['players']:
                if player['puuid'] == puuid:
                    player_team = player['teamId']
                    stats = player['stats']
                    agent_name = agent_mapping.get(player['characterId'], "Unknown Agent")
            
            # Find if that team won
            is_win = False
            for team in match_data['teams']:
                if team['teamId'] == player_team:
                    is_win = team['won']
            
            # Headshot calculation
            total_headshots = 0
            total_shots = 0
            if 'roundResults' in match_data:
                for round_res in match_data['roundResults']:
                    for player_stat in round_res.get('playerStats', []):
                        if player_stat['puuid'] == puuid:
                            for damage in player_stat.get('damage', []):
                                total_headshots += damage.get('headshots', 0)
                                total_shots += damage.get('headshots', 0) + damage.get('bodyshots', 0) + damage.get('legshots', 0)
            
            hs_percentage = round((total_headshots / max(1, total_shots)) * 100, 1) if total_shots > 0 else 0.0
            
            return {
                "map": map_name.split("/")[-1],
                "kills": stats['kills'],
                "deaths": stats['deaths'],
                "assists": stats['assists'],
                "agent_name": agent_name,
                "hs_percentage": hs_percentage,
                "is_win": is_win
            }
        return {"error": "Failed to fetch stats"}
     
    def get_esports_schedule(self):
        """
        Fetches live and upcoming VCT esports matches using the HenrikDev API.
        Requires a valid HDEV API key passed in the headers.
        """
        url = "https://api.henrikdev.xyz/valorant/v1/esports/schedule"
        
        try:
            # Fetch HenrikDev key from secrets and securely add to headers
            henrik_key = st.secrets["HENRIK_API_KEY"]
            henrik_headers = {
                "Authorization": henrik_key
            }
            
            response = requests.get(url, headers=henrik_headers, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"API Access Refused (Status: {response.status_code})"}
            
            return response.json().get("data", [])
            
        except Exception as e:
            return {"error": f"Connection Failure: {str(e)}"}