from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to IPL Cricket API. Endpoints: /players/<player_name>, /schedule, /live, /today"

@app.route("/today", methods=["GET"])
def today_ipl_schedule():
    try:
        url = "https://www.cricbuzz.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        match_cards = soup.find_all("li", class_="cb-view-all-ga cb-match-card cb-bg-white")

        today_matches = []
        for card in match_cards:
            title_tag = card.find("a")
            match_title = title_tag.get("title") if title_tag else "No title"

            match_link = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""

            time_div = card.find("div", class_="cb-ovr-flo cb-mtch-crd-time cb-font-12 cb-text-preview ng-binding ng-scope")
            match_time = time_div.get_text(strip=True) if time_div else ""

            if "Today" in match_time:
                today_matches.append({
                    "match": match_title,
                    "time": match_time,
                    "link": f"https://www.cricbuzz.com{match_link}"
                })

        if today_matches:
            return jsonify({"matches": today_matches, "status": "success"})
        else:
            return jsonify({"message": "No IPL matches found today", "status": "no_match"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})

@app.route("/live")
def live_matches():
    try:
        url = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
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

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})

if __name__ == '__main__':
    app.run(debug=True)
