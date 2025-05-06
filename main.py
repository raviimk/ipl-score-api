from flask import Flask, jsonify
import lxml
import requests
from bs4 import BeautifulSoup
import re
import time
from flask import Response
import json
from googlesearch import search #pip install googlesearch-python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hey there! This is a Cricket API. You can use the following endpoints: /players/<player_name>, /schedule, /live, /today, /today-selenium."

@app.route('/live')
def live_matches():
    link = f"https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    page = page.find("div", class_="cb-col cb-col-100 cb-bg-white")
    matches = page.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    live_matches = []

    for i in range(len(matches)):
        live_matches.append(matches[i].text.strip())

    return jsonify(live_matches)

@app.route('/today-selenium')
def today_matches_selenium():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.cricbuzz.com/cricket-match/live-scores")

    wait = WebDriverWait(driver, 10)
    today_ipl_matches = []

    try:
        blocks = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "cb-col-100.cb-col.cb-ltst-wgt-hdr")))

        for block in blocks:
            try:
                header = block.find_element(By.TAG_NAME, "h2")
                if "IPL" in header.text:
                    matches = block.find_elements(By.CLASS_NAME, "cb-mtch-lst.cb-col.cb-col-100.cb-tms-itm")
                    for match in matches:
                        title = match.find_element(By.CLASS_NAME, "text-hvr-underline").text.strip()
                        try:
                            status = match.find_element(By.CLASS_NAME, "cb-text-live").text.strip()
                        except:
                            try:
                                status = match.find_element(By.CLASS_NAME, "cb-text-complete").text.strip()
                            except:
                                try:
                                    status = match.find_element(By.CLASS_NAME, "cb-text-preview").text.strip()
                                except:
                                    status = "Match info not available"
                        today_ipl_matches.append({"title": title, "status": status})
            except:
                continue

    finally:
        driver.quit()

    if today_ipl_matches:
        return jsonify({"status": "success", "matches": today_ipl_matches})
    else:
        return jsonify({"message": "No IPL matches found today", "status": "no_match"})

if __name__ =="__main__":
    app.run(debug=True)


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
