import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

def scrape_data():
    URL = "https://www.bola.net/jadwal-pertandingan/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to retrieve the webpage")
        return {
            "status": "error",
            "message": "Failed to retrieve the webpage",
            "data": []
        }
    
    soup = BeautifulSoup(response.content, 'html.parser')

    structured_data = { 
        "status": "success",
        "message": "Data retrieved successfully",
        "data": [] 
    }
    
    # Find the main tabs content div
    tabs_content = soup.find("div", class_="tabs_content")
    if not tabs_content:
        return {
            "status": "error",
            "message": "No data found",
            "data": []
        }

    date_map = {}  # Dictionary to track dates and their indices

    # Process only active and visible tabs
    for tab in tabs_content.find_all("div", class_="tabs_content_item"):
        # Skip hidden tabs
        if 'style' in tab.attrs and 'display: none' in tab.attrs['style']:
            continue

        current_date = None
        current_date_data = None

        # Process each element in the tab
        for element in tab.children:
            # If we find a date header
            if element.name == "h3" and "ligaList_title" in element.get("class", []):
                current_date = element.text.strip()
                
                # Check if we've seen this date before
                if current_date in date_map:
                    # Use existing date data
                    current_date_data = structured_data["data"][date_map[current_date]]
                else:
                    # Create new date data
                    current_date_data = {
                        "date": current_date,
                        "leagues": []
                    }
                    date_map[current_date] = len(structured_data["data"])
                    structured_data["data"].append(current_date_data)
            
            # If we find a league list and have a current date
            elif element.name == "ul" and "ligaList" in element.get("class", []) and current_date_data:
                for liga_item in element.find_all("li", class_="ligaList_item"):
                    table = liga_item.find("table", class_="main-table")
                    if not table:
                        continue
                    
                    league_name = table.find("th").text.strip() if table.find("th") else "Unknown League"
                    
                    # Check if league already exists for this date
                    existing_league = next(
                        (league for league in current_date_data["leagues"] 
                            if league["league_name"] == league_name),
                        None
                    )

                    if existing_league:
                        league_data = existing_league
                    else:
                        league_data = {
                            "league_name": league_name,
                            "matches": []
                        }
                        current_date_data["leagues"].append(league_data)
                    
                    # Process matches
                    tbody = table.find("tbody")
                    if tbody:
                        for row in tbody.find_all("tr"):
                            cells = row.find_all("td")
                            if len(cells) < 3:
                                continue
                            
                            team_info = cells[0]
                            match_time = cells[1].text.strip()
                            match_link = cells[2].find("a")["href"] if cells[2].find("a") else ""

                            logos = [img["src"] for img in team_info.find_all("img")]
                            team_names = list(filter(lambda x: x != "-", [t.strip() for t in team_info.stripped_strings]))

                            league_data["matches"].append({
                                "teams": team_names,
                                "logos": logos,
                                "time": match_time,
                                "link": match_link
                            })

    # Check if data is empty before returning
    if len(structured_data["data"]) == 0:
        structured_data["status"] = "error"
        structured_data["message"] = "No matches data found"
    elif len(structured_data["data"]) > 0:
        structured_data["status"] = "success"
        structured_data["message"] = f"Successfully retrieved {len(structured_data['data'])} days of matches"

    return structured_data