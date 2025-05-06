from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import lxml

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to IPL Cricket API. Endpoints: /players/<player_name>, /schedule, /live"

@app.route('/schedule')
def schedule():
    url = "https://www.cricbuzz.com/cricket-schedule/upcoming-matches"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    matches_data = []
    blocks = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

    for block in blocks:
        match_cards = block.find_all("div", class_="cb-col cb-col-100 cb-mtch-blk")
        for card in match_cards:
            series_name = card.find("h2")
            if series_name and "IPL" in series_name.text:
                matches = card.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")
                for match in matches:
                    match_name = match.find("a")
                    match_time = match.find("div", class_="schedule-date")
                    if match_name and match_time:
                        matches_data.append({
                            "match": match_name.text.strip(),
                            "time": match_time.text.strip()
                        })

    if not matches_data:
        return jsonify({"message": "No IPL matches found in upcoming schedule", "status": "no_match"})

    return jsonify({
        "status": "success",
        "total_matches": len(matches_data),
        "matches": matches_data
    })

@app.route('/live')
def live_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    live_matches = []
    matches = soup.find_all("div", class_="cb-mtch-lst cb-col cb-col-100 cb-lv-scrs-col")

    for match in matches:
        match_text = match.text.strip()
        if "IPL" in match_text or any(team in match_text for team in ['MI', 'CSK', 'RCB', 'KKR', 'GT', 'RR', 'PBKS', 'DC', 'LSG', 'SRH']):
            live_matches.append(match_text)

    if not live_matches:
        return jsonify({
            "message": "No IPL match is live right now",
            "status": "no_live"
        })

    return jsonify({
        "status": "live",
        "matches": live_matches
    })

if __name__ == "__main__":
    app.run(debug=True)
