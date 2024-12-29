from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from pymongo import MongoClient
import uuid
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")  
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")  
MONGODB_URI = os.getenv("MONGODB_URI")  

PATH = "driver/chromedriver.exe"  
service = Service(PATH)  

client = MongoClient(MONGODB_URI)  
db = client["twitter_trends"]  
collection = db["trending_topics"]  

PROXY_FILE = "proxy.txt"

def load_proxies(file_path):
    proxies = []
    with open(file_path, "r") as f:
        for line in f:
            proxy = line.strip()
            if proxy:  
                proxies.append(proxy)
    return proxies

proxies = load_proxies(PROXY_FILE)

def configure_chrome_options(proxy):
    ip, port, username, password = proxy.split(":")
    proxy_auth = f"{username}:{password}@{ip}:{port}"
    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server=http://{ip}:{port}")
    chrome_options.add_argument(f"--proxy-auth={proxy_auth}")
    return chrome_options, ip

for proxy in proxies:
    chrome_options, proxy_ip = configure_chrome_options(proxy)

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://twitter.com/login")

        sleep(60)  
        username = driver.find_element(By.XPATH, "//input[@name='text']")
        username.send_keys(TWITTER_USERNAME)
        next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
        next_button.click()

        sleep(3)  
        password = driver.find_element(By.XPATH, "//input[@name='password']")
        password.send_keys(TWITTER_PASSWORD)
        log_in = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
        log_in.click()

        sleep(5)

        sleep(3)

        driver.execute_script("window.scrollTo(0, 1500);")
        sleep(3)

        trending_topics = []
        try:
            trending_section = driver.find_element(By.XPATH, "//div[@aria-label='Timeline: Trending now']")
            trends = trending_section.find_elements(By.XPATH, ".//span[@dir='ltr']")

            for trend in trends[:5]:
                trending_topics.append(trend.text)

            if len(trending_topics) < 5:
                print("Not enough trending topics found.")
            else:
                print("Trending Topics:", trending_topics)

        except Exception as e:
            print("Error scraping trends:", e)

        unique_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now()

        data = {
            "unique_id": unique_id, 
            "trends": trending_topics,  
            "timestamp": timestamp,  
            "ip_address": proxy_ip  
        }

        collection.insert_one(data)
        print(f"Data inserted with unique ID: {unique_id} using Proxy: {proxy_ip}")

    except Exception as e:
        print(f"Error with proxy {proxy}: {e}")

    finally:
        driver.quit()

    sleep(5)
