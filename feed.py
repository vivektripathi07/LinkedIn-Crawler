from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import random
import time
import csv
import re


def get_actual_date(date):
    today = datetime.today().strftime('%Y-%m-%d')
    current_year = datetime.today().strftime('%Y')

    def get_past_date(days=0, weeks=0, months=0, years=0):
        date_format = '%Y-%m-%d'
        dtObj = datetime.strptime(today, date_format)
        past_date = dtObj - relativedelta(days=days, weeks=weeks, months=months, years=years)
        past_date_str = past_date.strftime(date_format)
        return past_date_str

    date = re.sub(r"•.*", "", date).strip()

    match = re.match(r"(\d+)([a-zA-Z]+)", date)
    
    if match:
        number = int(match.group(1)) 
        unit = match.group(2).lower()  


        if unit == 'm' or unit == 'h':
            past_date = today
        if unit == 'd':
            past_date = get_past_date(days=number)
        elif unit == 'w':  
            past_date = get_past_date(weeks=number)
        elif unit == 'mo':  
            past_date = get_past_date(months=number)
        elif unit == 'y':  
            past_date = get_past_date(years=number)
        else:
            past_date = today 
    else:
        split_date = date.split("-")
        if len(split_date) == 2:  # MM-DD
            past_month = split_date[0]
            past_day = split_date[1]
            if len(past_month) < 2:
                past_month = "0" + past_month
            if len(past_day) < 2:
                past_day = "0" + past_day
            past_date = f"{current_year}-{past_month}-{past_day}"
        elif len(split_date) == 3: 
            past_month = split_date[0]
            past_day = split_date[1]
            past_year = split_date[2]
            if len(past_month) < 2:
                past_month = "0" + past_month
            if len(past_day) < 2:
                past_day = "0" + past_day
            past_date = f"{past_year}-{past_month}-{past_day}"
        else:
            past_date = today 

    return past_date



service = Service(ChromeDriverManager().install())

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=C:\\Users\\HP\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
chrome_options.add_argument("--profile-directory=Profile 2")


driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://www.linkedin.com/feed")


main_df = []

count = 50
while (count>0):

    post_elements = driver.find_elements(By.CLASS_NAME, "fie-impression-container")

    for post in post_elements:
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.update-components-actor__container")
            
            try:
                header_title = header_div.find_element(By.CSS_SELECTOR, "span.update-components-actor__title span[aria-hidden='true']").text
            except:
                header_title = None

            try:
                header_description = header_div.find_element(By.CSS_SELECTOR, "span.update-components-actor__description span[aria-hidden='true']").text
            except:
                header_description = None

            try:        
                header_sub_description = header_div.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description span[aria-hidden='true']").text
            except:
                header_sub_description = None


        except Exception as e:
            header_title = None


        try:
            content_div = post.find_element(By.CSS_SELECTOR, "div.update-components-text")

            try:
                content_text = content_div.text
            except:
                content_text = None
        
        except:
            content_div = None


        try:
            social_reach_div = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts")
            
            try:
                reaction_div = social_reach_div.find_element(By.CSS_SELECTOR, "span.social-details-social-counts__reactions-count")
                reaction_count = reaction_div.text.strip()
            except:
                reaction_count = 0

            try:
                comment_div = social_reach_div.find_element(By.CSS_SELECTOR, "button[aria-label*='comment'] span[aria-hidden='true']")
                comment_count = comment_div.text.strip()
            except:
                comment_count = 0

            try:
                repost_div = social_reach_div.find_element(By.CSS_SELECTOR, "button[aria-label*='reposts'] span[aria-hidden='true']")
                repost_count = repost_div.text.strip()
            except:
                repost_count = 0

            media_type = "text"
            media_links = []
            media_count = 0

            # Check for Video
            if post.find_elements(By.CSS_SELECTOR, ".update-components-linkedin-video"):
                media_type = "video"
                try:
                    video_element = post.find_element(By.CSS_SELECTOR, "video")
                    video_src = video_element.get_attribute("src")
                    media_links = [video_src]  # Store as list for consistency
                    media_count = 1
                except:
                    media_links = []
                    media_count = 0

            # Check for Image(s)
            elif post.find_elements(By.CSS_SELECTOR, ".update-components-image"):
                media_type = "image"
                try:
                    image_elements = post.find_elements(By.CSS_SELECTOR, ".update-components-image img.ivm-view-attr__img--centered")
                    media_links = [img.get_attribute("src") for img in image_elements]
                    media_count = len(media_links)
                except:
                    media_links = []
                    media_count = 0

            elif post.find_elements(By.CSS_SELECTOR, ".feed-shared-article__container") or \
                post.find_elements(By.CSS_SELECTOR, ".feed-shared-link__container") or \
                post.find_elements(By.CSS_SELECTOR, ".update-components-document__container"):

                media_type = "article"
                try:
                    iframe_elements = post.find_elements(By.CSS_SELECTOR, "iframe")
                    media_links = []

                    for iframe in iframe_elements:
                        iframe_src = iframe.get_attribute("src")

                        # Check if the iframe src contains the specific document link
                        if iframe_src and "feedshare-document-images" in iframe_src:
                            media_links.append(iframe_src)  # Append the iframe src (which is the image source)

                    media_count = len(media_links)

                except Exception as e:
                    print(f"Error extracting images from article: {e}")
                    media_links = []
                    media_count = 0

            # Fallback: Text-only post
            else:
                media_type = "text"
                media_links = []
                media_count = 0
        
        except:
            social_reach_div = None


        main_df.append({
            "name": header_title,
            "desc": header_description,
            "timestamp": header_sub_description,
            "content": content_text,
            'reaction_count' : reaction_count,
            "comments_count" : comment_count,
            "repost_count" : repost_count,
            "Media Type": media_type,
            "Media Link": media_links,
            "Media Count": media_count
        })


    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(10)
    count = count - 1

main_df = pd.DataFrame(main_df)
main_df = main_df.dropna(subset=["name"])
main_df.drop_duplicates(subset=["content"], inplace=True)
main_df['converted_date'] = main_df['timestamp'].apply(lambda x: get_actual_date(x))

main_df.to_csv('feed.csv', encoding='utf-8', index=False)

