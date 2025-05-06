from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to IPL Cricket API. Endpoints: /players/<player_name>, /schedule, /live, /today"

@app.route("/today", methods=["GET"])
def today_ipl_schedule():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get("https://www.cricbuzz.com/")
        time.sleep(5)  # wait for JS to load

        match_cards = driver.find_elements(By.CSS_SELECTOR, "li.cb-view-all-ga.cb-match-card.cb-bg-white")
        today_matches = []

        for card in match_cards:
            try:
                time_elem = card.find_element(By.CSS_SELECTOR, "div.cb-ovr-flo.cb-mtch-crd-time.cb-font-12.cb-text-preview")
                match_time = time_elem.text.strip()

                if "Today" in match_time:
                    title_elem = card.find_element(By.TAG_NAME, "a")
                    title = title_elem.get_attribute("title")
                    link = title_elem.get_attribute("href")
                    today_matches.append({
                        "match": title,
                        "time": match_time,
                        "link": link
                    })
            except:
                continue

        driver.quit()

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
