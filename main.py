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

        match_cards = soup.find_all("div", class_="cb-col cb-col-100 cb-mtch-crd cb-pos-rel")

        today_matches = []
        for card in match_cards:
            # Match title
            title_tag = card.find("div", class_="cb-mtch-crd-hdr cb-font-10")
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Match series name
            series_tag = card.find("div", class_="cb-col-90 cb-color-light-sec cb-ovr-flo")
            series = series_tag.get_text(strip=True) if series_tag else ""

            # Match teams
            teams_tag = card.find("a")
            teams = teams_tag.get("title") if teams_tag else ""

            # Match time
            time_tag = card.find("div", string=lambda text: text and ("Today" in text or ":" in text))
            time_text = time_tag.get_text(strip=True) if time_tag else ""

            if teams and time_text:
                today_matches.append({
                    "match": teams,
                    "title": title,
                    "series": series,
                    "time": time_text
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
