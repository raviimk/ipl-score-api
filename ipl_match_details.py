import requests
from bs4 import BeautifulSoup

def get_top_4_batsmen_scores(match_id):
    url = f"https://www.cricbuzz.com/live-cricket-scorecard/{match_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        data = []

        # Each innings block
        innings_blocks = soup.select("div.cb-col.cb-col-100.cb-ltst-wgt-hdr")

        for block in innings_blocks:
            team_header = block.select_one("span")
            team_name = team_header.text.replace(" Innings", "").strip() if team_header else "Unknown Team"

            batsmen = []
            rows = block.select("div.cb-col.cb-col-100.cb-scrd-itms")

            count = 0
            for row in rows:
                columns = row.find_all("div")
                if len(columns) >= 3 and columns[0].text.strip() and columns[1].text.strip().isdigit():
                    batsman_name = columns[0].text.strip()
                    runs = columns[1].text.strip()
                    batsmen.append({"name": batsman_name, "runs": runs})
                    count += 1
                    if count == 4:
                        break

            data.append({
                "team": team_name,
                "top_4_batsmen": batsmen
            })

        return data

    except Exception as e:
        return {"error": str(e)}
