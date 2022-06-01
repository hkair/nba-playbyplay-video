import requests
from requests.models import PreparedRequest

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

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

params = {"ContextMeasure": ContextMeasure, "EndPeriod": EndPeriod, "EndRange": EndRange, "GameID": GameId, "RangeType": RangeType, "Season": SeasonId, "SeasonType": SeasonType, "StartPeriod": StartPeriod, "StartRange": StartRange, "flag": flag}

URL = "https://www.nba.com/stats/events/?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=28800&GameID=0042100307&RangeType=0&Season=2021-22&SeasonType=Playoffs&StartPeriod=0&StartRange=0&flag=3"

req = PreparedRequest()
req.prepare_url(BASE_URL, params)

print(req.url)
page = requests.get(req.url)

soup = BeautifulSoup(page.text, "html.parser")
video_div = soup.find("main")

stats_video_player = soup.find("stats-video-player")
print(stats_video_player)

# Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(req.url)

# video_container = driver.find_element(By.ID, 'stats-video-player_container')
# print(video_container.get_attribute('innerHTML'))
video = driver.find_element(By.ID, 'stats-videojs-player_html5_api')
video_url = video.get_attribute('src')
print(video_url)

file_name = video_url.split('/')[-1]   
print(file_name)

output_dir = "./data/test/"

rsp = urlopen(video_url)
with open(output_dir+file_name, 'wb') as f:
    f.write(rsp.read())

# id="stats-video-player_container"
# <video id="stats-videojs-player_html5_api" class="vjs-tech" tabindex="-1" role="application" preload="auto" autoplay="" poster="https://videos.nba.com/nba/pbp/media/2022/05/29/0042100307/7/527c26f9-68e1-a3d1-6a4b-e935f53c57d0_960x540.jpg" src="https://videos.nba.com/nba/pbp/media/2022/05/29/0042100307/7/527c26f9-68e1-a3d1-6a4b-e935f53c57d0_960x540.mp4">
#     <p class="vjs-no-js">
#       To view this video please enable JavaScript, and consider upgrading to a
#       web browser that supports HTML5 video.
#     </p>
#   </video>
