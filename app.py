import psycopg2
import requests
from datetime import datetime, timezone

# 1. Fetch live asset prices from the free public API
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
try:
    data = requests.get(url).json()
    btc_price = data['bitcoin']['usd']
    eth_price = data['ethereum']['usd']
    current_time = datetime.now(timezone.utc)
except Exception as e:
    print(f"Failed to fetch data from API: {e}")
    exit()

# 2. Connect to your Timescale Cloud Database
# Using your exact connection parameters provided during cluster initialization
DB_URL = "postgres://tsdbadmin:YOUR_DB_PASSWORD@tdmfst51vt.oztevl7cid.tsdb.cloud.timescale.com:32098/tsdb?sslmode=require"

try:
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    # 3. Write relational records directly into your Hypertable split partition
    query = "INSERT INTO crypto_prices (time, ticker, price) VALUES (%s, %s, %s);"
    cursor.execute(query, (current_time, 'BTC', btc_price))
    cursor.execute(query, (current_time, 'ETH', eth_price))

    conn.commit()
    print(f"🚀 Success! Saved to TimescaleDB -> BTC: ${btc_price} | ETH: ${eth_price}")

except Exception as e:
    print(f"Database connection or insertion failed: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()