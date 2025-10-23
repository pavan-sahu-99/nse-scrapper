from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
import json

def get_oi_spurts():
    # Set up headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Load NSE homepage to get cookies
        driver.get("https://www.nseindia.com")
        time.sleep(3)

        # Step 2: Hit actual API endpoint
        url = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.TAG_NAME, "body").text.strip().startswith("{")
        )
        #time.sleep(2)

        # Step 3: Parse JSON response
        text = driver.find_element(By.TAG_NAME, "body").text
        data = json.loads(text).get("data", [])
        df = pd.DataFrame(data)
        print(df.columns)
        #print(df.head())
        filtered_df = df[['symbol', 'underlyingValue', 'latestOI', 'prevOI', 'changeInOI', 'avgInOI', 'volume']].copy()
        filtered_df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filtered_df.rename(columns={    
            "underlyingValue": "cmp",
            "avgInOI": "pctChangeInOI",
            "prevOI": "prev_oi_d",
            "latestOI": "latest_oi_d"
        }, inplace=True)
        filtered_df.columns = [["symbol", "cmp", 'latest_oi_d', 'prev_oi_d', "changeInOI", "pctChangeInOI", "volume", "timestamp"]]

    except Exception as e:
        print(f"Error occurred: {e}")
        filtered_df = pd.DataFrame()

    finally:
        driver.quit()

    return filtered_df


if __name__ == "__main__":
    data = get_oi_spurts()
    print(data.head())
