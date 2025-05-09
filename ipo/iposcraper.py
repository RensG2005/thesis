import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import yfinance as yf


def scrape_euronext_ipo_page(page_num):
    url = f"https://live.euronext.com/en/ipo-showcase?combine=&field_iponi_ipo_date_value%5Bmin%5D=&field_iponi_ipo_date_value%5Bmax%5D=&field_trading_location_target_id%5B404%5D=404&page={page_num}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://live.euronext.com/en/ipo-showcase'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='views-table')
        if not table:
            print(f"No table found on page {page_num}. This could be the end of available data.")
            return []
        
        rows = table.find_all('tr')
        if len(rows) <= 1:  # Only header row or empty
            print(f"No data rows found on page {page_num}.")
            return []
        
        ipo_data = []
        
        for row in rows[1:]:
            cells = row.find_all('td')
            
            if len(cells) >= 5:
                company_elem = cells[1].find('a')
                company_name = company_elem.text.strip() if company_elem else cells[1].text.strip()
                
                # Extract data from cells
                ipo_date = cells[0].text.strip()
                ticker = cells[2].text.strip()
                companyID = cells[3].text.strip()
                trading_location = cells[4].text.strip()
                
                # Create a dictionary for this IPO
                ipo_dict = {
                    'IPOdate': ipo_date,
                    'company': company_name,
                    'companyID': companyID,
                    'Trading Location': trading_location
                }
                
                ipo_data.append(ipo_dict)
        
        return ipo_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        return []
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        return []

def scrape_multiple_pages(start_page=0, end_page=10):
    all_ipo_data = []
    
    for page_num in range(start_page, end_page + 1):
        ipo_data = scrape_euronext_ipo_page(page_num)
        all_ipo_data.extend(ipo_data)
        
        # Sleep between requests to avoid getting blocked
        if page_num < end_page:
            sleep_time = random.uniform(1.0, 3.0)
            print(f"Waiting {sleep_time:.2f} seconds before next request...")
            time.sleep(sleep_time)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_ipo_data)
    
    print(f"Scraped a total of {len(df)} IPOs")
    return df

ipo_df = scrape_multiple_pages(0, 10)

ipo_df.to_csv("euronextIPOAms.csv", index=False)
print("\nSample of scraped data:")
print(ipo_df.head())
# ipo_df = pd.read_csv("euronextIPOAms.csv")

# def get_returns(ticker, ipo_date):
#     try:
#         ipo_date = pd.to_datetime(ipo_date)
#         df = yf.download(ticker, start=ipo_date, end=ipo_date + timedelta(days=35))

#         df = df['Close']
#         df = df[df.notna()]

#         if len(df) < 2:
#             return None  # Not enough data
#         # First trading price
#         first_price = df.iloc[0]
        
#         # First day return (close - open same day)
#         first_day_return = (df.iloc[0] - first_price) / first_price
#         return first_day_return
    
#     except Exception as e:
#         print(e)
#         return None

# valu = get_returns("FERGR.AS", "2025-02-13")
# print(valu)

# ipo_df['first_day_return'] = ipo_df.apply(lambda row: get_returns(row["ticker"], row['IPOdate']), axis=1)
ipo_df.to_csv("euronextIPOAms.csv")

print(ipo_df.head())
