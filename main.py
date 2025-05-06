from flask import Flask, jsonify
import lxml
import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "Hey there! This is a Cricket API. Endpoints: /players/<player_name>, /schedule, /live, /today"

# ---------- PLAYER PROFILE ENDPOINT ----------
@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    # Same logic as before (unchanged)
    return jsonify({"message": "Player endpoint working. Please implement full logic."})

# ---------- MATCH SCHEDULE ENDPOINT ----------
@app.route('/schedule')
def schedule():
    url = "https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    matches = []
    for container in soup.find_all("div", class_="cb-col-100 cb-col"):
        date = container.find("div", class_="cb-lv-grn-strip text-bold")
        match_info = container.find("div", class_="cb-col-100 cb-col")
        if date and match_info:
            matches.append(f"{date.text.strip()} - {match_info.text.strip()}")
    
    return jsonify(matches)

# ---------- LIVE IPL MATCHES ----------
@app.route('/live')
def live_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    ipl_teams_short = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
    match_blocks = soup.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    live_ipl = []

    for match in match_blocks:
        text = match.text.strip()
        if any(team in text for team in ipl_teams_short):
            live_ipl.append(text)

    if not live_ipl:
        return jsonify({
            "status": "no_live",
            "message": "No IPL match is live currently.",
            "tip": "Use /today to see upcoming matches."
        })

    return jsonify({
        "status": "live",
        "matches": live_ipl
    })

# ---------- TODAY’S IPL MATCHES ----------
@app.route('/today')
def today_ipl_schedule():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    today_matches = []
    now = datetime.now().strftime("%Y-%m-%d")

    match_cards = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")[0]
    games = match_cards.find_all("div", class_="cb-mtch-lst cb-col cb-col-100 cb-lv-scrs-col")

    for match in games:
        match_title = match.find("a")
        match_text = match.text.strip()
        if match_title:
            today_matches.append(match_text)

    if not today_matches:
        return jsonify({"status": "no_match", "message": "No IPL match found for today."})
    
    return jsonify({
        "status": "today",
        "matches": today_matches
    })

# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)
