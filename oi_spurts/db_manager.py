import sqlite3
import schedule
import pandas as pd
from datetime import datetime, time as dt_time
import time
import subprocess
import os
from oi_scrapper import get_oi_spurts

DB_PATH = "data/oi_spurts.db"


def save_to_csv():
    df_new = get_oi_spurts()
    df_new.to_csv("data/oi_spurts.csv", index=False)
    print("Data saved to data/oi_spurts.csv")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oi_spurts (
            symbol TEXT,
            cmp REAL,
            latest_oi_d REAL,
            prev_oi_d REAL,
            changeInOI REAL,
            pctChangeInOI REAL,
            volume REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")

def get_last_snapshot():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT * FROM oi_spurts 
        WHERE timestamp = (SELECT MAX(timestamp) FROM oi_spurts)
    """
    df_prev = pd.read_sql_query(query, conn)
    conn.close()
    return df_prev

def clear_db_if_old():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT timestamp FROM oi_spurts"
    df = pd.read_sql_query(query, conn)

    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        last_ts = df['timestamp'].max()
        if last_ts.date() != datetime.now().date():
            print("🧹 Clearing database for new trading day...")
            conn.execute("DELETE FROM oi_spurts")
            conn.commit()
        else:
            print(f"DB date: {last_ts.date()} | Today: {datetime.now().date()} -> No clearing needed.")
    conn.close()

def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("oi_spurts", conn, if_exists="append", index=False)
    conn.close()

def main_code():
    print("\nRunning main data job...")
    clear_db_if_old()
    save_to_csv()
    data = pd.read_csv("data/oi_spurts.csv")
    data_db = get_last_snapshot()

    if not data_db.empty:
        if pd.to_datetime(data['timestamp']).max() == pd.to_datetime(data_db['timestamp']).max():
            print("✅ Latest data already exists in DB.")
        else:
            save_to_db(data)
            print("New data inserted into DB.")
    else:
        save_to_db(data)
        print("DB was empty. Data inserted.")

    new_data = get_last_snapshot()
    print(new_data.head())
    print("⚙️ Running OI Comparator after DB update...")
    subprocess.run(["python", "oi_spurts\oi_comparator.py"])

def job():
    current_time = datetime.now().time()
    start = dt_time(9, 15)
    end = dt_time(15, 30)

    if start <= current_time <= end:
        print(f"{current_time} within market hours -> running job")
        main_code()
    else:
        print(f"{current_time} outside market hours -> skipping")

if __name__ == "__main__":
    init_db()
    job()
    schedule.every(6).minutes.do(job)
    print("Scheduler started, running every 6 minutes...")

    while True:
        now = datetime.now().time()
        if now > datetime.strptime("15:30", "%H:%M").time():
            print(f"{now} outside market hours -> stopping scheduler")
            break
        schedule.run_pending()
        time.sleep(60)
