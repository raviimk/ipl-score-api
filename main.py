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
    # Paste the existing get_player() function here
    return jsonify(player_data)


@app.route('/schedule')
def schedule():
    # ... [your original /schedule code stays unchanged] ...
    return jsonify(matches)


@app.route('/live')
def live_matches():
    link = "https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    container = page.find("div", class_="cb-col cb-col-100 cb-bg-white")
    if not container:
        return jsonify({"message": "Could not fetch data", "status": "error"})

    matches = container.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    ipl_teams = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
    live_ipl_matches = []

    for match in matches:
        match_text = match.text.strip()
        found_teams = [team for team in ipl_teams if team in match_text]
        if len(found_teams) >= 2:
            live_ipl_matches.append(match_text)

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
    link = "https://www.cricbuzz.com/cricket-schedule"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    containers = page.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")
    ipl_teams = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
    today_date = datetime.now().strftime("%d %b")  # e.g., "06 May"

    today_matches = []

    for container in containers:
        match_blocks = container.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")
        for block in match_blocks:
            match_text = block.text.strip()
            if today_date in match_text:
                found_teams = [team for team in ipl_teams if team in match_text]
                if len(found_teams) >= 2:
                    today_matches.append(match_text)

    if not today_matches:
        return jsonify({"message": "No IPL matches found today", "status": "no_match"})
    else:
        return jsonify({
            "status": "today",
            "matches": today_matches
        })


if __name__ == "__main__":
    app.run(debug=True)
