import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import re
import glob

tickers_and_ids = [
    # ("ASM-International", 11808),
    # ("ASML-Holding", 16923),
    # ("ASR-Nederland", 596718),
    # ("ING-Groep", 11773),
    # ("KPN-Koninklijke", 25845),
    # ("SHELL-PLC", 210964)
    ("Akzo-Nobel", 11756)
]

def create_filename_from_url(url, ticker):
    match = re.search(r'Topic/(\d+)/([^/\.]+)', url)
    if match:
        topic_id = match.group(1)
        topic_name = match.group(2)
        return f"{ticker}_{topic_name}_{topic_id}.csv"
    else:
        return f"{ticker}_forum_posts.csv"

class ForumScraperClass:
    def __init__(self, base_url, ticker):
        self.base_url = base_url
        self.ticker = ticker
        self.output_file = create_filename_from_url(base_url, ticker)
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.data = []

    def get_page_url(self, page_num):
        return f"{self.base_url}&page={page_num}" if "?" in self.base_url else f"{self.base_url}?page={page_num}" if page_num > 1 else self.base_url

    def parse_post(self, post):
        try:
            username = post.select_one("a.forumpost__username").get_text(strip=True)
            post_date = post.select_one("span.forumpost__userdate").get_text(strip=True)
            content = post.select_one("section.forumpost__maintext").get_text(strip=True)
            post_id = post.select_one("a[name]")["name"] if post.select_one("a[name]") else "Unknown"
            return {
                "post_id": post_id,
                "username": username,
                "post_date": post_date,
                "content": content
            }
        except Exception as e:
            print(f"Error parsing post: {e}")
            return None

    def scrape_page(self, page_num):
        url = self.get_page_url(page_num)
        try:
            print(f"Fetching page {page_num}: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all("li", class_='postlist__item')
            page_data = []
            for post in posts:
                post_data = self.parse_post(post)
                if post_data:
                    post_data["page"] = page_num
                    post_data["url"] = url
                    page_data.append(post_data)
            return page_data
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return []

    def scrape_all_pages(self):
        page_num = 1
        while page_num < 10:
            page_posts = self.scrape_page(page_num)
            if page_posts:
                if page_num > 1 and any(post["post_id"] == page_posts[0]["post_id"] for post in self.data):
                    break
                self.data.extend(page_posts)
                if len(page_posts) < 25:
                    break
            else:
                break
            time.sleep(random.uniform(0, 2))
            page_num += 1
        self.save_data()

    def save_data(self):
        os.makedirs("./iex/postslist", exist_ok=True)
        try:
            filepath = os.path.join("./iex/postslist", self.output_file)
            df = pd.DataFrame(self.data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"Saved {len(self.data)} posts to {filepath}")
        except Exception as e:
            print(f"Error saving data: {e}")

def get_allposts_of_thread(forum_url, ticker):
    scraper = ForumScraperClass(forum_url, ticker)
    scraper.scrape_all_pages()

for ticker, id in tickers_and_ids:
    try:
        list_path = f"/home/rens/scriptie/iex/linklist/{ticker}list.txt"
        print(f"\nProcessing {ticker}...")
        
        with open(list_path, "r") as f:
            for i, line in enumerate(f, 1):
                url = line.strip()
                if url:
                    cleaned_url = url.replace("/Forum-Aandeel", "")
                    print(f"\nScraping link #{i}")
                    get_allposts_of_thread(cleaned_url, ticker)

        csv_files = glob.glob(os.path.join('/home/rens/scriptie/iex/postslist/', f'{ticker}_*.csv'))
        df_list = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                if not df.empty:
                    df_list.append(df)
                else:
                    print(f"Skipped empty file: {file}")
            except pd.errors.EmptyDataError:
                print(f"Skipped truly empty file: {file}")

        if df_list:
            merged_df = pd.concat(df_list, ignore_index=True)
            merged_path = f'/home/rens/scriptie/iex/postslist/{ticker}.csv'
            merged_df.to_csv(merged_path, index=False)
            print(f"Merged file saved to: {merged_path}")

            # Delete individual CSVs
            for file in csv_files:
                try:
                    os.remove(file)
                    print(f"Deleted file: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")
        else:
            print(f"No valid data found for {ticker}, skipping merge.")
    except Exception as main_err:
        print(f"Fatal error during processing of {ticker}: {main_err}")