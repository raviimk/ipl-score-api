import requests
from bs4 import BeautifulSoup

def get_ipl_live_match_details():
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    matches = soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

    for match in matches:
        series = match.find("span", class_="text-gray")
        if series and "Indian Premier League" in series.text:
            title = match.find("h3").text.strip()
            teams_score = match.find("div", class_="cb-ltst-wgt-hdr").text.strip()
            commentary = match.find("div", class_="cb-text-complete").text if match.find("div", class_="cb-text-complete") else ""

            # Match ID from URL
            match_link = match.find("a", href=True)
            if not match_link:
                continue
            match_id = match_link['href'].split('/')[2]  # e.g. '12345'
            match_url = f"https://www.cricbuzz.com/live-cricket-scorecard/{match_id}"
            detail_resp = requests.get(match_url, headers=headers)
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

            scorecard = detail_soup.find_all("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")[1:]  # Skip heading
            output = [teams_score.strip()]

            for idx, innings in enumerate(scorecard[:2]):  # Only first 2 innings
                team_name = innings.find("span").text.strip()
                output.append(f"{team_name} BATSMEN")

                batsmen = innings.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
                count = 0
                for batsman in batsmen:
                    if batsman.find_all("div")[0].text.strip() in ["", "Extras", "Total"]:
                        continue

                    name = batsman.find_all("div")[0].text.strip()
                    runs = batsman.find_all("div")[2].text.strip()
                    status = batsman.find_all("div")[1].text.strip()

                    out_status = "OUT" if "b " in status or "c " in status or "run out" in status.lower() else "PLY"
                    output.append(f"{count+1} {name} = {runs} {out_status}")
                    count += 1
                    if count == 4:
                        break

            return output

    return ["No IPL live match at the moment."]
