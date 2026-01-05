import time
import random
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def random_sleep(min_s=1, max_s=3):
   time.sleep(random.uniform(min_s, max_s))


EMAIL       = "cla38379@gmail.com"
PASSWORD    = "2143658709QAZ!"
QUERY       = "Data Analyst"
PROFILE_DIR = "/Users/xiechen/selenium_chrome_profile"
OUT_DIR     = "/Users/xiechen/Desktop"
OUT_FILE    = os.path.join(OUT_DIR, "linkedin_ten_pages_names.csv")


opts = webdriver.ChromeOptions()
opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
driver = webdriver.Chrome(options=opts)
wait   = WebDriverWait(driver, 20)


try:
   driver.get("https://www.linkedin.com/login")
   random_sleep()


   if "login" in driver.current_url:
       wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
       driver.find_element(By.ID, "password").send_keys(PASSWORD, Keys.ENTER)
       random_sleep()


   search_box = wait.until(EC.element_to_be_clickable((
       By.XPATH, '//input[contains(@placeholder,"Search")]'
   )))
   search_box.click()
   random_sleep()
   search_box.send_keys(QUERY, Keys.RETURN)
   random_sleep()


   people_url = (
       "https://www.linkedin.com/search/results/people/"
       f"?keywords={QUERY.replace(' ', '%20')}"
   )
   driver.get(people_url)
   random_sleep()


   names = []
   titles = []
   locations = []


   for page in range(10):
       # Wait for cards to load
       prev = 0
       while True:
           driver.execute_script("window.scrollBy(0, window.innerHeight);")
           random_sleep(1, 2)
           cards = driver.find_elements(By.XPATH, "//ul[@role='list'][1]/li")
           if len(cards) == prev:
               break
           prev = len(cards)


       list_container = driver.find_elements(By.XPATH, "//ul[@role='list']")
       if list_container:
           for ele in list_container[0].find_elements(By.XPATH, "./li"):
               try:
                   # Name
                   name_el = ele.find_elements(
                       By.XPATH,
                       ".//a[contains(@href, 'https://www.linkedin.com/in')]/span/span"
                   )
                   name = name_el[0].text.strip() if name_el else ""
                   
                   # Title
                   title_el = ele.find_elements(By.XPATH, ".//div[contains(@class, 't-14 t-black t-normal')]")
                   title = title_el[0].text.strip() if title_el else ""
                   
                   # Location (find t-14 t-normal but not t-black)
                   location_el = ele.find_elements(By.XPATH, ".//div[contains(@class, 't-14 t-normal') and not(contains(@class, 't-black'))]")
                   location = location_el[0].text.strip() if location_el else ""
                   names.append(name)
                   titles.append(title)
                   locations.append(location)
               except Exception as e:
                   pass
       # Click Next for next page
       try:
           next_btn = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
           if next_btn.is_enabled():
               next_btn.click()
               random_sleep(2, 4)
           else:
               break
       except Exception as e:
           break


   os.makedirs(OUT_DIR, exist_ok=True)
   df = pd.DataFrame({"Name": names, "Title": titles, "Location": locations})
   df.to_csv(OUT_FILE, index=False, encoding="utf-8")
   print(f"Scraped {len(names)} profiles → {OUT_FILE}")


finally:
   driver.quit()


