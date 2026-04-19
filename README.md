# 🎯 E-Sports Analytics Hub

A professional, real-time interactive dashboard built with Python and Streamlit that tracks, analyzes, and compares player performance across major competitive tactical shooters.

**Live Application:** [esports-analytics-hub.streamlit.app](https://efe-esports-analytics.streamlit.app/)

## Features

* **Valorant Match Analytics:** Connects to the official Riot Games API to fetch player PUUIDs, lifetime metrics, and detailed match-by-match breakdowns (K/D, Headshot %, Agent picks).
* **Counter-Strike 2 Integration:** Utilizes the FaceIt API to bypass private Steam profiles, directly pulling hidden ELO, Skill Levels, and real-time recent match histories.
* **Head-to-Head Comparison:** A dedicated battle module that pits two players against each other, calculating and visualizing statistical deltas.
* **Responsive UI/UX:** Built with Streamlit's layout containers and metrics elements, featuring a custom dark e-sports theme.

## Technical Stack

* **Language:** Python 3.x
* **Frontend/Framework:** Streamlit
* **Data Processing:** Pandas
* **API Integration:** `requests` library for RESTful API consumption (Riot API, FaceIt Data API)
* **Deployment:** Streamlit Community Cloud

## Local Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/esports-analytics-hub.git](https://github.com/yourusername/esports-analytics-hub.git)
