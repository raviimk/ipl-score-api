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
    # ... [your original /players code stays unchanged] ...
    return jsonify(player_data)

@app.route('/schedule')
def schedule():
    # ... [your original /schedule code stays unchanged] ...
    return jsonify(matches)

@app.route('/live')
def live_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    match_blocks = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

    # SHORT NAMES for live matches
    ipl_teams_short = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
    live_ipl_matches = []

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

    match_cards = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

    # FULL NAMES for upcoming/today matches
    ipl_teams_full = [
        'Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bangalore', 'Gujarat Titans',
        'Rajasthan Royals', 'Lucknow Super Giants', 'Delhi Capitals', 'Punjab Kings',
        'Kolkata Knight Riders', 'Sunrisers Hyderabad'
    ]
    today_matches = []

    for card in match_cards:
        blocks = card.find_all("div", class_="cb-mtch-lst cb-col cb-col-100 cb-tms-itm")
        for block in blocks:
            match_info = block.text.strip()
            found_teams = [team for team in ipl_teams_full if team in match_info]
            if len(found_teams) >= 2:
                today_matches.append(match_info)

    if today_matches:
        return jsonify({
            "status": "today",
            "matches": today_matches
        })
    else:
        return jsonify({
            "message": "No IPL matches found today",
            "status": "no_match"
        })

if __name__ == "__main__":
    app.run(debug=True)
