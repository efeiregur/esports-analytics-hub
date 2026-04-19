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