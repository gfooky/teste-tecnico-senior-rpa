import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

BASE_URL = "https://www.scrapethissite.com/pages/ajax-javascript/"


def _parse_int(text: str) -> int:
    cleaned = text.strip()
    return int(cleaned) if cleaned else 0


def scrape_oscar_films() -> List[Dict[str, Any]]:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    SELENIUM_URL = "http://localhost:4444/wd/hub"
    
    driver = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=chrome_options
    )
    
    films = []
    
    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)
        
        year_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "year-link")))
        years = [link.text for link in year_links]
        
        for year in years:
            link = wait.until(EC.element_to_be_clickable((By.ID, year)))
            link.click()
            time.sleep(2) 
            
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "film")))
            rows = driver.find_elements(By.CLASS_NAME, "film")
            
            for i in range(len(rows)):
                attempts = 3
                while attempts > 0:
                    try:
                        current_rows = driver.find_elements(By.CLASS_NAME, "film")
                        row = current_rows[i]
                        
                        best_picture_elements = row.find_elements(By.CLASS_NAME, "film-best-picture")
                        best_picture = False
                        if best_picture_elements and best_picture_elements[0].find_elements(By.TAG_NAME, "i"):
                            best_picture = True
                        
                        nom_text = row.find_element(By.CLASS_NAME, "film-nominations").text
                        awards_text = row.find_element(By.CLASS_NAME, "film-awards").text
                            
                        films.append({
                            "year": year,
                            "title": row.find_element(By.CLASS_NAME, "film-title").text.strip(),
                            "nominations": _parse_int(nom_text),
                            "awards": _parse_int(awards_text),
                            "best_picture": best_picture
                        })
                        break
                    except StaleElementReferenceException:
                        attempts -= 1
                        time.sleep(1)
    finally:
        driver.quit()
        
    return films