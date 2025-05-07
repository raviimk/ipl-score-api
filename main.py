from flask import Flask, jsonify
import lxml
import requests
from bs4 import BeautifulSoup
from googlesearch import search

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Cricket API. Endpoints: /players/<player_name>, /schedule, /live, /match/<match_id>"

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    query = f"{player_name} cricbuzz"
    profile_link = None
    try:
        results = search(query, num_results=5)
        for link in results:
            if "cricbuzz.com/profiles/" in link:
                profile_link = link
                break
                
        if not profile_link:
            return {"error": "No player profile found"}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
    
    c = requests.get(profile_link).text
    cric = BeautifulSoup(c, "lxml")
    profile = cric.find("div", id="playerProfile")
    pc = profile.find("div", class_="cb-col cb-col-100 cb-bg-white")

    name = pc.find("h1", class_="cb-font-40").text
    country = pc.find("h3", class_="cb-font-18 text-gray").text
    image_url = pc.find('img')['src']

    personal = cric.find_all("div", class_="cb-col cb-col-60 cb-lst-itm-sm")
    role = personal[2].text.strip()

    icc = cric.find_all("div", class_="cb-col cb-col-25 cb-plyr-rank text-right")
    tb = icc[0].text.strip()
    ob = icc[1].text.strip()
    twb = icc[2].text.strip()
    tbw = icc[3].text.strip()
    obw = icc[4].text.strip()
    twbw = icc[5].text.strip()

    summary = cric.find_all("div", class_="cb-plyr-tbl")
    batting = summary[0]
    bowling = summary[1]

    bat_rows = batting.find("tbody").find_all("tr")
    batting_stats = {}
    for row in bat_rows:
        cols = row.find_all("td")
        format_name = cols[0].text.strip().lower()
        batting_stats[format_name] = {
            "matches": cols[1].text.strip(),
            "runs": cols[3].text.strip(),
            "highest_score": cols[5].text.strip(),
            "average": cols[6].text.strip(),
            "strike_rate": cols[7].text.strip(),
            "hundreds": cols[12].text.strip(),
            "fifties": cols[11].text.strip(),
        }

    bowl_rows = bowling.find("tbody").find_all("tr")
    bowling_stats = {}
    for row in bowl_rows:
        cols = row.find_all("td")
        format_name = cols[0].text.strip().lower()
        bowling_stats[format_name] = {
            "balls": cols[3].text.strip(),
            "runs": cols[4].text.strip(),
            "wickets": cols[5].text.strip(),
            "best_bowling_innings": cols[9].text.strip(),
            "economy": cols[7].text.strip(),
            "five_wickets": cols[11].text.strip(),
        }

    player_data = {
        "name": name,
        "country": country,
        "image": image_url,
        "role": role,
        "rankings": {
            "batting": {"test": tb, "odi": ob, "t20": twb},
            "bowling": {"test": tbw, "odi": obw, "t20": twbw}
        },
        "batting_stats": batting_stats,
        "bowling_stats": bowling_stats
    }

    return jsonify(player_data)


@app.route('/schedule')
def schedule():
    link = f"https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    match_containers = page.find_all("div", class_="cb-col-100 cb-col")
    matches = []

    for container in match_containers:
        date = container.find("div", class_="cb-lv-grn-strip text-bold")
        match_info = container.find("div", class_="cb-col-100 cb-col")
        if date and match_info:
            match_date = date.text.strip()
            match_details = match_info.text.strip()
            matches.append(f"{match_date} - {match_details}")
    
    return jsonify(matches)


@app.route('/live')
def live_matches():
    link = f"https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")
    page = page.find("div", class_="cb-col cb-col-100 cb-bg-white")
    matches = page.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    live_matches = []
    for match in matches:
        live_matches.append(match.text.strip())
    
    return jsonify(live_matches)


# ✅ NEW: Match details by match ID
@app.route('/match/<match_id>', methods=['GET'])
def match_details(match_id):
    try:
        url = f"https://www.cricbuzz.com/live-cricket-scorecard/{match_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")

        title = soup.find("h1", class_="cb-nav-hdr").text.strip()
        innings = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

        match_data = {"title": title, "innings": []}

        for inning in innings:
            lines = inning.text.strip().split('\n')
            if len(lines) > 1 and "Batsman" not in lines[0]:
                match_data["innings"].append(lines)

        return jsonify(match_data)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
