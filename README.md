# nse-scrapper
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Project Overview:
-----------------------
This project performs three core functions:
1. Scrapes Data from NSE: Uses Selenium with Chromium WebDriver in headless mode to fetch OI data and format it into a clean, readable structure.
2. Stores & Analyzes Data:
    * Saves the scraped data into a database.
    * Performs mathematical computations to identify stocks showing strong OI change, price change, and volume change.
    * Filters results using Opening Range Breakout (ORB) logic to find the most promising intraday candidates.
    * Saves the filtered results into another database.
3. Automated Alerts:
   * Sends bullish and bearish stock signals to a Telegram channel using a bot.
   * The entire process runs automatically every 6 minutes.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
File Breakdown:
-----------------------
1. oi_scrapper.py:
  * Handles data scraping using Selenium in headless mode.
  * Waits until the NSE site returns a valid response.
  * Occasionally, NSE may return no data—simply rerun the script (an auto-retry mechanism can be added later).

2. db_manager.py:
  * The core integration module of the project.
  * Creates and manages the database.
  * Uploads scraped data from CSV to the DB.
  * Schedules recurring jobs every 6 minutes.
  * Integrates all modules and sends filtered stock signals to Telegram.

3. oi_comparator.py:
  * The analytical engine of the project.
  * Performs all mathematical computations to compare OI, price, and volume changes.
  * Identifies the best-performing stocks for intraday trades and stores them in a separate database.

4. telegram_integration.py:
  * Handles Telegram Bot API integration.
  * Sends filtered bullish/bearish stock updates to the configured Telegram chat.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Future Improvements:
-----------------------
1. Add retry logic in oi_scrapper.py for “No Data” responses.
2. Integrate live candle data for more accurate ORB checks.
3. Add exception handling and logging for better reliability.
4. Extend support for futures and index-based filtering.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tech Stack:
-----------------------
1. Python 3.10+
2. Selenium (for scraping)
3. SQLite (for DB management)
4. Pandas (for data computation)
5. Telegram Bot API
6. Scheduler(for periodic tasks)
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Output Example:
-----------------------------------------------------
Every 6 minutes, a Telegram message is sent with:
--------------------------------------------------------
OI Spurts Summary
-------------------------
 Summary:
signal
Neutral    208
Bullish      3
Bearish      3
-------------------------
 Bearish Stocks: 
BRITANNIA, BOSCHLTD, MARUTI
-------------------------
 Bullish Stocks: 
CUMMINSIND, ALKEM, SOLARINDS
-------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------
