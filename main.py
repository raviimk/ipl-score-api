from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# IPL teams short and full forms
IPL_TEAMS_SHORT = ['CSK', 'MI', 'RCB', 'GT', 'RR', 'LSG', 'DC', 'PBKS', 'KKR', 'SRH']
IPL_TEAMS_FULL = [
    'Chennai Super Kings', 'Mumbai Indians', 'Royal Challengers Bangalore',
    'Gujarat Titans', 'Rajasthan Royals', 'Lucknow Super Giants',
    'Delhi Capitals', 'Punjab Kings', 'Kolkata Knight Riders', 'Sunrisers Hyderabad'
]

@app.route('/')
def index():
    return "Welcome to IPL Score API. Endpoints: /today, /live"

@app.route('/today')
def today_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")

    matches = []
    match_blocks = soup.find_all("div", class_="cb-col cb-col-100 cb-tms-itm")

    if not match_blocks:
        return jsonify({
            "message": "Structure not found on Cricbuzz page",
            "status": "error"
        })

    for block in match_blocks:
        match_text = block.text.strip()
        found_teams = [team for team in IPL_TEAMS_FULL if team in match_text]
        if len(found_teams) >= 2:
            matches.append(match_text)

    if matches:
        return jsonify({
            "status": "today",
            "matches": matches
        })
    else:
        return jsonify({
            "message": "No IPL matches found today",
            "status": "no_match"
        })

@app.route('/live')
def live_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")

    matches = []
    blocks = soup.find_all("div", class_="cb-mtch-lst cb-col cb-col-100 cb-lv-scrs-col")

    for block in blocks:
        match_text = block.text.strip()
        found_teams = [team for team in IPL_TEAMS_SHORT if team in match_text]
        if len(found_teams) >= 2:
            matches.append(match_text)

    if matches:
        return jsonify({
            "status": "live",
            "matches": matches
        })
    else:
        return jsonify({
            "message": "No IPL match is live right now",
            "status": "no_live"
        })

if __name__ == '__main__':
    app.run(debug=True)
