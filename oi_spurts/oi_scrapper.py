import pandas as pd
import time
from datetime import datetime
import json
import requests

headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

def fetch_data(payload):
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=10)
        s.get("https://www.nseindia.com/option-chain", headers=headers, timeout=10)
        output = s.get(payload, headers=headers, timeout=10).json()
    except ValueError:
        output = {}
    return output

def get_oi_spurts():

    url = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
    response = fetch_data(url)
    data = response.get("data", [])
    
    if not data:
        print("No data found in API response")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    print("Available columns:", df.columns.tolist())
    print(f"Found {len(df)} records")
    
    column_mapping = {
        'symbol': 'symbol',
        'underlyingValue': 'cmp', 
        'latestOI': 'latest_oi_d',
        'prevOI': 'prev_oi_d',
        'changeInOI': 'changeInOI',
        'avgInOI': 'pctChangeInOI',
        'volume': 'volume'
    }
    available_columns = [col for col in column_mapping.keys() if col in df.columns]
    filtered_df = df[available_columns].copy()
    
    filtered_df.rename(columns=column_mapping, inplace=True)
    
    filtered_df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return filtered_df


if __name__ == "__main__":

    print("Fetching OI spurts data...")   
    data = get_oi_spurts()
    
    if not data.empty:
        data.to_csv("data/oi_spurts.csv", index=False)
        print("Data saved successfully!")
        print(f"Data shape: {data.shape}")
        print("\nFirst few rows:")
        print(data.head())
    else:
        print("Failed to fetch data")
