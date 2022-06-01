import os
from telnetlib import ECHO
import requests
from requests.models import PreparedRequest

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

# Web Scraping Endpoint - /stats/events
BASE_URL = "https://www.nba.com/stats/events?"

# Required Parameters
GameId = "0042100307"
SeasonId = "2021-22"
SeasonType="Playoffs"
# flag - 1 (Video Only), flag - 2 (Plots Only), flag - 3 (Both)
flag = 3

# Optional Parameters
ContextMeasure = "FGA"
EndPeriod = 0
EndRange = 28800
RangeType = 0
StartPeriod = 0 
StartRange = 0

# URL Example: "https://www.nba.com/stats/events/?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=28800&GameID=0042100307&RangeType=0&Season=2021-22&SeasonType=Playoffs&StartPeriod=0&StartRange=0&flag=3"

def extractPlayByPlayVideos(output_dir, GameId, SeasonId, SeasonType):
    '''
        Scrapes the nba.com/stats/events page of a single game and downloads all play by play video clips.
    '''

    path = os.path.join(output_dir, GameId)
    print(path)

    # if path doesn't exist create new directory
    if not os.path.exists(path):
        # Create a new directory because it does not exist 
        os.makedirs(path)

    params = {"ContextMeasure": ContextMeasure, "EndPeriod": EndPeriod, "EndRange": EndRange, "GameID": GameId, "RangeType": RangeType, "Season": SeasonId, "SeasonType": SeasonType, "StartPeriod": StartPeriod, "StartRange": StartRange, "flag": flag}

    req = PreparedRequest()
    req.prepare_url(BASE_URL, params)

    print("Request URL: ", req.url)
    page = requests.get(req.url)

    # Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(req.url)


    # Click on All in row selector of table
    # <select class="stats-table-pagination__select ng-pristine ng-valid ng-not-empty ng-touched >
    selector_div = driver.find_element(By.CLASS_NAME, "stats-table-pagination__info")
    select = Select(selector_div.find_element(By.TAG_NAME, "select"))
    select.select_by_value('string:All')

    print("Selector Clicked: All")

    # Row Description
    # <div class="nba-stat-table__overflow" data-fixed="1" role="grid">
    stats_table_overflow = driver.find_element(By.CLASS_NAME, "nba-stat-table__overflow")
    stats_table_overflow_tbody = stats_table_overflow.find_element(By.TAG_NAME, "tbody")
    rows_overflow = stats_table_overflow_tbody.find_elements(By.TAG_NAME, "tr")

    # Button
    # <div class="nba-stat-table__overlay" data-fixed="1" role="grid">
    stats_table_overlay = driver.find_element(By.CLASS_NAME, "nba-stat-table__overlay")
    stats_table_overlay_tbody = stats_table_overlay.find_element(By.TAG_NAME, "tbody")
    rows_overlay = stats_table_overlay_tbody.find_elements(By.TAG_NAME, "tr")

    print("nba-stat-table__overflow Row Length: ", len(rows_overflow))
    print("nba-stat-table__overlay Row Length: ", len(rows_overlay))

    n = len(rows_overflow)
    
    # overflow contain play by play information 
    # overlay contains the button td
    for idx, x in enumerate(zip(rows_overflow, rows_overlay)):
        overflow, overlay = x

        # List of td tags
        overflow_td = overflow.find_elements(By.TAG_NAME, "td")
        overlay_td = overlay.find_element(By.TAG_NAME, "td")

        # # Click Button for next Video to Play
        button_td = overflow_td[0].find_element(By.TAG_NAME, "button")
        #button_td = overlay_td.find_element(By.TAG_NAME, "button")
        print(button_td.get_attribute("outerHTML"))
        #WebDriverWait(driver, 10)

        button_td.click()

        #overflow_td[1].click()
        
        #Extract Video
        video = driver.find_element(By.ID, 'stats-videojs-player_html5_api')
        video_url = video.get_attribute('src')

        # File Name
        pbp_text = [ overflow_td[i].text for i in range(len(overflow_td)) ]
        print(pbp_text)
        description = [ "_".join(overflow_td[i].text.lower().split()) for i in range(1, 5) ]
        file_name = "-".join(description)
        print(file_name)

        rsp = urlopen(video_url)
        dest_file = os.path.join(output_dir, GameId, file_name + ".mp4")
        print(dest_file)
        with open(dest_file, 'wb') as f:
            f.write(rsp.read())

        if idx == 1:
            break

    # i=0
    # while i < n:
    #     overflow, overlay = rows_overflow[i], rows_overlay[i]

    #      # List of td tags
    #     overflow_td = overflow.find_elements(By.TAG_NAME, "td")
    #     overlay_td = overlay.find_element(By.TAG_NAME, "td")
        
    #     #Extract Video
    #     video = driver.find_element(By.ID, 'stats-videojs-player_html5_api')
    #     video_url = video.get_attribute('src')

    #     # File Name
    #     pbp_text = [ overflow_td[i].text for i in range(len(overflow_td)) ]
    #     description = [ "_".join(overflow_td[i].text.lower().split()) for i in range(1, 5) ]
    #     file_name = "-".join(description)
    #     print(file_name)

    #     rsp = urlopen(video_url)
    #     dest_file = os.path.join(output_dir, GameId, file_name + ".mp4")
    #     print(dest_file)
    #     with open(dest_file, 'wb') as f:
    #         f.write(rsp.read())

    #     # # Click Button for next Video to Play
    #     overflow_next, overlay_next = rows_overflow[i+1], rows_overlay[i+1]
    #     overflow_td = overflow_next.find_elements(By.TAG_NAME, "td")
    #     overlay_td = overlay_next.find_element(By.TAG_NAME, "td")

    #     # button_td = overflow_td[0].find_element(By.TAG_NAME, "button")
    #     button_td = overlay_td.find_element(By.TAG_NAME, "button")
    #     # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))
    #     print(button_td.get_attribute("outerHTML"))
    #     button_td.click()

    #     if i == 1:
    #         break

    #     i += 1


def main():
    output_dir = "./data/videos/playbyplay-game-videos"
    extractPlayByPlayVideos(output_dir, GameId, SeasonId, SeasonType)


if __name__ == "__main__":
    main()