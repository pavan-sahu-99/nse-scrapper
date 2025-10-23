from click import group
import pandas as pd
import sqlite3
from telegram_integration import send_telegram_message
from datetime import datetime,time

DB_PATH = "data/analysis.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            symbol TEXT,
            cmp_trend TEXT,
            oi_pchange REAL,
            volume_trend TEXT,
            oi_trend TEXT,
            first_candle_break TEXT,
            signal TEXT     
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")

def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analysis")
    df.to_sql("analysis", conn, if_exists="append", index=False)
    conn.close()

def read_oi_db_data():
    conn = sqlite3.connect("data/oi_spurts.db")
    df = pd.read_sql_query("SELECT * FROM oi_spurts", conn)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def compute_trends(df):
    trends = []

    df = df.sort_values(['symbol', 'timestamp'])

    grouped = df.groupby('symbol')

    first_candle_data = grouped.first().reset_index()
    latest_candle_data = grouped.last().reset_index()


    for symbol, group in grouped:
        if len(group) < 2:
            continue

        #Price trend
        price_diff = group['cmp'].diff().dropna()
        print(len(price_diff))
        threshold = 0.7 #change according to requirement
        #proportion of positive and negative ratios:
        pos_ratio = (price_diff > 0).sum() / len(price_diff)
        neg_ratio = (price_diff < 0).sum() / len(price_diff)
        
        if pos_ratio > threshold:
            cmp_trend = "UP"
        elif neg_ratio > threshold:
            cmp_trend = "DOWN"
        else:
            cmp_trend = "Normal"

        """TESTING ALTERNATE LOGIC FOR CMP TREND"""
        #first_cmp = group['cmp'].iloc[0]
        #last_cmp = group['cmp'].iloc[-1]
        #cmp_pchange = ((last_cmp - first_cmp) / first_cmp) * 100
        #
        #if cmp_pchange > 0.3:  # >0.3% up
        #    cmp_trend = "UP"
        #elif cmp_pchange < -0.3:  # <-0.3% down
        #    cmp_trend = "DOWN"
        #else:
        #    cmp_trend = "Normal"       
         
        first_timestamp = first_candle_data.loc[first_candle_data['symbol'] == symbol, 'timestamp'].values[0]
        first_timestamp = pd.to_datetime(first_timestamp).time()
        #first_candle_break:
        if time(9, 15) <= first_timestamp <= time(9, 30):
            first_cmp = first_candle_data.loc[first_candle_data['symbol'] == symbol, 'cmp'].values[0]
            latest_cmp = latest_candle_data.loc[latest_candle_data['symbol'] == symbol, 'cmp'].values[0]
            if latest_cmp > first_cmp:
                orb = "Broke Above"
            elif latest_cmp < first_cmp:
                orb = "Broke Below"
            else:
                orb = "Range Bound"
        else:
            orb = "N/A"
        # Volume trend: compare latest snapshot to average
        avg_vol = group['volume'].mean()
        latest_vol = group['volume'].iloc[-1]
        volume_trend = "UP" if latest_vol > avg_vol else "Normal"

        # OI trend: latest vs first in the group
        oi_change = group['changeInOI'].iloc[-1] - group['changeInOI'].iloc[0]
        oi_pchange = (group['changeInOI'].iloc[-1] - group['changeInOI'].iloc[0]) / abs(group['changeInOI'].iloc[0]) * 100 if group['changeInOI'].iloc[0] != 0 else 0
        oi_trend = "UP" if oi_change > 0 else ("DOWN" if oi_change < 0 else "Normal")

        # Signal logic
        if cmp_trend == "UP" and oi_trend == "UP" and volume_trend == "UP":
            signal = "Bullish"
        elif cmp_trend == "DOWN" and oi_trend == "UP" and volume_trend == "UP":
            signal = "Bearish"
        else:
            signal = "Neutral"

        trends.append({
            'symbol': symbol,
            'cmp_trend': cmp_trend,
            #'oi_change': oi_change,
            'oi_pchange': round(oi_pchange, 2),
            'volume_trend': volume_trend,
            'oi_trend': oi_trend,
            'first_candle_break': orb,
            'signal': signal
        })
    return pd.DataFrame(trends)

def send_message():
    data = read_oi_db_data()
    trend_df = compute_trends(data)
    print(trend_df['signal'].value_counts()) 
    trend_summary = trend_df['signal'].value_counts()
    bearish_trend_df = trend_df[(trend_df['signal'] == "Bearish") & ((trend_df['first_candle_break'] == "Broke Below") | (trend_df['first_candle_break'] == "N/A"))].sort_values('oi_pchange', ascending=False)
    bullish_trend_df = trend_df[(trend_df['signal'] == "Bullish") & ((trend_df['first_candle_break'] == "Broke Above") | (trend_df['first_candle_break'] == "N/A"))].sort_values('oi_pchange', ascending=False)
    total_df = trend_df[trend_df['signal'].isin(["Bullish", "Bearish"])]


    bearish_stocks = ", ".join(bearish_trend_df['symbol'].tolist())
    bullish_stocks = ", ".join(bullish_trend_df['symbol'].tolist())

    message = (
        f" *OI Spurts Summary*\n"
        "-------------------------\n"
        f" *Summary:*\n{trend_summary.to_string()}\n"
        f"-------------------------\n"
        f" *Bearish Stocks:* \n{bearish_stocks or 'None'}\n"
        f"-------------------------\n"
        f" *Bullish Stocks:* \n{bullish_stocks or 'None'}\n"
        f"-------------------------\n"
    )

    if len(message) > 4000:
        for i in range(0, len(message), 4000):
            send_telegram_message(message[i:i+4000])
    else:
        send_telegram_message(message)

    return total_df

if __name__ == "__main__":
    init_db()
    total_df = send_message()
    if not total_df.empty:
        save_to_db(total_df)