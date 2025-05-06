from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# Setup Selenium WebDriver
def create_driver():
    options = Options()
    options.add_argument('--headless')  # Headless mode for server
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ------------------------------
# LIVE MATCH SCORE
# ------------------------------
@app.route('/live-score', methods=['GET'])
def live_score():
    url = "https://www.cricbuzz.com/live-cricket-scorecard/115336/mi-vs-gt-56th-match-indian-premier-league-2025"
    driver = create_driver()
    driver.get(url)

    time.sleep(5)

    try:
        score_block = driver.find_element(By.CLASS_NAME, "cb-min-lv")
        score_text = score_block.text
        driver.quit()
        return jsonify({"live_score": score_text})
    except Exception as e:
        driver.quit()
        return jsonify({"error": str(e)}), 500

# ------------------------------
# TODAY'S UPCOMING MATCHES
# ------------------------------
@app.route('/today-matches', methods=['GET'])
def today_matches():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    driver = create_driver()
    driver.get(url)

    time.sleep(5)

    matches = []
    try:
        match_blocks = driver.find_elements(By.CLASS_NAME, "cb-mtch-lst")

        for block in match_blocks:
            try:
                status = block.find_element(By.CLASS_NAME, "cb-text-complete").text
                continue  # Skip completed matches
            except:
                pass  # Not completed

            try:
                title = block.find_element(By.CLASS_NAME, "cb-ltst-wgt-hdr").text
                teams = block.find_element(By.CLASS_NAME, "cb-ovr-flo").text
                time_info = block.find_element(By.CLASS_NAME, "cb-text-live").text if block.find_elements(By.CLASS_NAME, "cb-text-live") else "Upcoming"
                matches.append({
                    "title": title,
                    "teams": teams,
                    "status": time_info
                })
            except:
                continue

        driver.quit()
        return jsonify({"today_matches": matches})
    except Exception as e:
        driver.quit()
        return jsonify({"error": str(e)}), 500

# ------------------------------
# Run Server
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
