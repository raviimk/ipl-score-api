from flask import Flask, jsonify
import lxml
import requests
from bs4 import BeautifulSoup
import re
import time
from flask import Response
import json
from googlesearch import search  # pip install googlesearch-python
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "Hey there! This is a Cricket API. Endpoints: /players/<player_name>, /schedule, /live, /today"

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    # Placeholder - fill with your logic
    return jsonify({"player": player_name})

@app.route('/schedule')
def schedule():
    # Placeholder - fill with your logic
    return jsonify({"schedule": "Coming soon"})

@app.route('/live')
def live_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    ipl_teams_short = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
    live_ipl_matches = []

    match_blocks = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")
    for card in match_blocks:
        matches = card.find_all("div", class_="cb-mtch-lst cb-col cb-col-100 cb-lv-scrs-col")
        for match in matches:
            match_info = match.text.strip()
            found_teams = [team for team in ipl_teams_short if team in match_info]
            if len(found_teams) >= 2:
                live_ipl_matches.append(match_info)

    if not live_ipl_matches:
        return jsonify({
            "message": "No IPL match is live right now",
            "status": "no_live",
            "today_ipl_schedule": ["Use /today to see today’s matches"]
        })

    return jsonify({
        "status": "live",
        "matches": live_ipl_matches
    })

@app.route('/today')
def today_ipl_schedule():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    # 👇 Ye debugging output hai jo terminal me dikhayega HTML
    print("🔍 DEBUG OUTPUT START")
    print(soup.prettify()[:5000])  # Pehle 5000 characters print hoga
    print("🔍 DEBUG OUTPUT END")

    return jsonify({"message": "Debug mode on. Check terminal output."})

if __name__ == "__main__":
    app.run(debug=True)
