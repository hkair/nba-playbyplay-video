from dataclasses import dataclass
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
from selenium.common.exceptions import WebDriverException

import time
import datetime

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

# Web Scraping Endpoint - /stats/events
BASE_URL = "https://www.nba.com/stats/events?"
# URL Example: "https://www.nba.com/stats/events/?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=28800&GameID=0042100307&RangeType=0&Season=2021-22&SeasonType=Playoffs&StartPeriod=0&StartRange=0&flag=3"

# flag - 1 (Video Only), flag - 2 (Plots Only), flag - 3 (Both)
flag = 3

# Optional Parameters
ContextMeasure = "FGA"
EndPeriod = 0
EndRange = 28800
RangeType = 0
StartPeriod = 0 
StartRange = 0


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
    driver.implicitly_wait(10)
    driver.get(req.url)

    # Click on All in row selector of table
    # <select class="stats-table-pagination__select ng-pristine ng-valid ng-not-empty ng-touched >
    selector_div = driver.find_element(By.CLASS_NAME, "stats-table-pagination__info")
    select = Select(selector_div.find_element(By.TAG_NAME, "select"))
    options = select.options

    print(selector_div.text)

    start = datetime.datetime.now()

    # iterate over selector 
    # start with option 1, and skip the string:All
    num_of_videos = 0
    option_idx = 1
    while option_idx < len(options):
        
        curr_option = options[option_idx].get_attribute("value")
        select.select_by_value(curr_option)
        print("Selector Clicked: ", curr_option)

        # Row Description
        # <div class="nba-stat-table__overflow" data-fixed="1" role="grid">
        stats_table_overflow = driver.find_element(By.CLASS_NAME, "nba-stat-table__overflow")
        stats_table_overflow_tbody = stats_table_overflow.find_element(By.TAG_NAME, "tbody")
        rows_overflow = stats_table_overflow_tbody.find_elements(By.TAG_NAME, "tr")

        print("Wait 1 seconds: ")
        time.sleep(1)

        # overflow contains play by play information 
        # overlay contains the button td
        prev_url = ''
        skipped_videos = []
        video_count = 0
        for idx, overflow in enumerate(rows_overflow):

            # List of td tags
            overflow_td = overflow.find_elements(By.TAG_NAME, "td")

            # # Click Button for next Video to Play
            button_td = overflow_td[0].find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", button_td)
            print("Row Clicked: ")

            video = driver.find_element(By.ID, 'stats-videojs-player_html5_api')
            video_url = video.get_attribute('src')

            # If the new video_url is the same as prev url
            # skip video
            if video_url == prev_url:
                prev_url = video_url
                skipped_videos.append(video_url)
                continue

            print("Video URL: ", video_url)

            # File Name
            pbp_text = [ overflow_td[i].text for i in range(len(overflow_td)) ]
            description = [ "_".join(pbp_text[i].lower().split()) for i in range(1, 5) ]
            file_name =  GameId + "_{0}_".format(num_of_videos + idx) + "-".join(description) +  ".mp4"

            rsp = urlopen(video_url)
            dest_file = os.path.join(output_dir, GameId, file_name)
            print(dest_file)
            with open(dest_file, 'wb') as f:
                f.write(rsp.read())

            print("Downloaded Video: ", file_name)

            video_count += 1

        # add to the number of videos downloaded
        num_of_videos += video_count
        # move to next option in selector
        option_idx += 1

    end = datetime.datetime.now()
    print("Elapsed Time: ", end-start)
    print("{0} videos downloaded".format(num_of_videos))
    print("Videos Skipped: ", skipped_videos)

def main():
    # Required Parameters
    GameId = "0042100307"
    SeasonId = "2021-22"
    SeasonType="Playoffs"

    output_dir = "./data/videos/playbyplay-game-videos"

    extractPlayByPlayVideos(output_dir, GameId, SeasonId, SeasonType)


if __name__ == "__main__":
    main()