from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import pandas as pd
import random
import time
import csv
import re


service = Service(ChromeDriverManager().install())

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=C:\\Users\\HP\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
chrome_options.add_argument("--profile-directory=Profile 2")


driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://www.linkedin.com/feed")


wait = WebDriverWait(driver, 10)


search_bar = driver.find_element(By.CLASS_NAME, "basic-input")
search_bar.clear()
text = "Software Engineering"
for t in text:
    search_bar.send_keys(t)
    ti = random.randint(1,5)
    ti = ti / 10
    time.sleep(ti)

time.sleep(2)
search_bar.send_keys(Keys.RETURN)

time.sleep(10)


main_job_df = []

job_element = driver.find_element(By.PARTIAL_LINK_TEXT, "See all job results")
time.sleep(random.randint(2,5))
job_element.click()


max_pages = 2

left_section = driver.find_element(
    By.CSS_SELECTOR, 
    ".uTXQwZXOqBdwsSbnNaoBUuXbeIyDqvnJDnimsY"
)

text_check = "LinkedIn Corporation © 2025"


while(max_pages>0):
    while True:
            driver.execute_script("arguments[0].scrollBy(0, 500);", left_section)
            time.sleep(random.randint(5,7))

            if text_check in driver.page_source:
                print("Text found!")
                break
            else:
                print("Text not found!")

    job_titles = []

    job_cards = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li.scaffold-layout__list-item")
    ))

    for job in job_cards:
        try:
            title_element = job.find_element(By.CSS_SELECTOR, "a.job-card-list__title--link")
            title = title_element.text.strip()
            job_titles.append(title)
        except:
            continue


    length = len(job_titles)

    for i, job in enumerate(job_cards[:length]):

        driver.execute_script("arguments[0].scrollIntoView();", job)
        time.sleep(random.randint(1, 5))

        job.click()
        time.sleep(random.randint(1,5))

        single_job_element = driver.find_element(By.CLASS_NAME, "jobs-search__job-details--container")
        company_name = single_job_element.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
        job_title = single_job_element.find_element(By.CSS_SELECTOR, "h1.t-24.t-bold.inline a").text
        job_meta_data = single_job_element.find_elements(By.CSS_SELECTOR, "span.tvm__text.tvm__text--low-emphasis")
        job_meta_data_text = [i.text for i in job_meta_data]
        job_details = single_job_element.find_element(By.CLASS_NAME, "jobs-box__html-content").text
        print(company_name + "   " + job_title +  "\n ")
        
        main_job_df.append({
            "Company Name": company_name,
            "Job Title": job_title,
            "Job Meta Data": job_meta_data_text,
            "Job Details": job_details
        })

        time.sleep(random.randint(6,12))


        if (i == (length - 1)) :
            next_button = driver.find_element(By.CLASS_NAME, "jobs-search-pagination__button--next")
            next_button.click()
            max_pages  = max_pages - 1


main_job_dff = pd.DataFrame(main_job_df)
main_job_dff.drop_duplicates(subset=["Job Details"], inplace=True)

main_job_dff.to_excel("searched_job.xlsx")