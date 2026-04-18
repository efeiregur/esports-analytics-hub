import os
import requests
from dotenv import load_dotenv

load_dotenv()

class RiotAPIClient:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        self.headers = {
            "X-Riot-Token": self.api_key
        }
        self.account_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id"

    def get_player_puuid(self, game_name, tag_line):
        url = f"{self.account_url}/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Connection failed with status: {response.status_code}"}