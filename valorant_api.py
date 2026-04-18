import requests
import os
from dotenv import load_dotenv

load_dotenv()

class RiotAPIClient:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def get_player_puuid(self, game_name, tag_line):
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Connection failed with status: {response.status_code}"}

    def get_match_history(self, puuid, count=5):
        url = f"https://europe.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # We slice the list directly here to get only the recent 'count' matches
            match_list = response.json().get('history', [])
            return [match['matchId'] for match in match_list][:count]
        return {"error": f"Match history failed with status: {response.status_code}"}

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
            
            # Fetch agent mapping
            agent_mapping = self.get_agent_mapping()
            
            for player in match_data['players']:
                if player['puuid'] == puuid:
                    stats = player['stats']
                    character_id = player['characterId']
                    agent_name = agent_mapping.get(character_id, "Unknown Agent")
                    
                    total_headshots = 0
                    total_shots = 0
                    
                    # Calculate Headshot percentage from round results
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
                        "hs_percentage": hs_percentage
                    }
            return {"error": "Player not found in match data"}
        return {"error": f"Failed to fetch match details. Status: {response.status_code}"}