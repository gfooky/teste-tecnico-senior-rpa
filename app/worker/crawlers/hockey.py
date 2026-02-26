import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

BASE_URL = "https://www.scrapethissite.com/pages/forms/"


def scrape_hockey_teams() -> List[Dict[str, Any]]:
    """Scrapes hockey team data across all pages using requests and BeautifulSoup."""
    teams = []
    page = 1
    
    with requests.Session() as session:
        while True:
            response = session.get(BASE_URL, params={"page_num": page}, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr", class_="team")
            
            if not rows:
                break
                
            for row in rows:
                ot_losses_str = row.find("td", class_="ot-losses").text.strip()
                ot_losses = int(ot_losses_str) if ot_losses_str else None
                
                teams.append({
                    "team_name": row.find("td", class_="name").text.strip(),
                    "year": int(row.find("td", class_="year").text.strip()),
                    "wins": int(row.find("td", class_="wins").text.strip()),
                    "losses": int(row.find("td", class_="losses").text.strip()),
                    "ot_losses": ot_losses,
                    "win_percentage": float(row.find("td", class_="pct").text.strip()),
                    "goals_for": int(row.find("td", class_="gf").text.strip()),
                    "goals_against": int(row.find("td", class_="ga").text.strip()),
                    "goal_difference": int(row.find("td", class_="diff").text.strip()),
                })
            page += 1
            
    return teams