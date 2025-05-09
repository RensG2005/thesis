import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import time
import random
import seaborn as sns
import statsmodels.api as sm
import os
import re
from matplotlib.dates import DateFormatter

ticker = "Vopak"
id = 612967

def create_filename_from_url(url):
    match = re.search(r'Topic/(\d+)/([^/\.]+)', url)
    if match:
        topic_id = match.group(1)
        topic_name = match.group(2)
        return f"{topic_name}_{topic_id}.csv"
    else:
        # Fallback to a generic name if pattern doesn't match
        return "forum_posts.csv"

def scrape_forum(url):
    """
    Args:
        url: Starting URL for the forum page
        
    Returns:
        List of all collected topic links
    """
    all_hrefs = []
    current_url = url
    page_count = 1
    base_url = url
    
    while True:
        print(f"Scraping page {page_count}: {current_url}")
        
        # Get the page content
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            break
            
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract topic links from the current page
        topic_links = []
        topic_elements = soup.select('.topiclist__subject')
        
        for topic in topic_elements:
            href = topic.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                if href.startswith('../../'):
                    href = "https://www.iex.nl/Forum-Aandeel/" + href[6:]
                topic_links.append(href)
                
        print(f"Found {len(topic_links)} links on this page")
        all_hrefs.extend(topic_links)
        
        # Look for the "volgende pagina" (next page) button
        next_page = None
        pagination_link = soup.select_one('.forumpaging__next')
        try:
            next_page = pagination_link.get('href')
        except:
            if not next_page:
                print("No next page button found. Finished scraping.")
                print(pagination_link)
                break

                
        
        # For ABN AMRO forum, the next_page is just "ABN-AMRO.aspx?startpost=-{number}"
        # We need to construct the full URL by using the base domain + path from the original URL
        if f"{ticker}.aspx?startpost=" in next_page:
            # Extract the base path (everything before the filename)
            base_path = "/".join(base_url.split("/")[:-1]) + "/"
            current_url = base_path + next_page
        else:
            # Fallback for any other format
            if next_page.startswith('../../'):
                next_page = "https://www.iex.nl/Forum-Aandeel/" + next_page[6:]
            elif not next_page.startswith('http'):
                base_domain = re.match(r'(https?://[^/]+)', base_url).group(1)
                if not next_page.startswith('/'):
                    next_page = '/' + next_page
                next_page = base_domain + next_page
            current_url = next_page
        
        page_count += 1
        
        # Be nice to the server
        time.sleep(1)
        
    return all_hrefs

try:
    starting_url = f"https://www.iex.nl/Forum-Aandeel/{id}/{ticker}.aspx"
    topic_links = scrape_forum(starting_url)
    
    print(f"\nTotal links collected: {len(topic_links)}")
    
    # Optionally save to file
    with open("./iex/{ticker}list.txt", "w") as f:
        for link in topic_links:
            f.write(f"{link}\n")
    
    print(f"Links saved to {ticker}.txt")
except Exception as e:
    print(e)

class ForumScraperClass:
    def __init__(self, base_url):
        self.base_url = base_url
        self.output_file = create_filename_from_url(base_url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.data = []
        
    def get_page_url(self, page_num):
        """Generate URL for a specific page using query parameter"""
        # Use the ?page= parameter for pagination
        if page_num == 1:
            return self.base_url
        else:
            # Check if the URL already has query parameters
            if "?" in self.base_url:
                return f"{self.base_url}&page={page_num}"
            else:
                return f"{self.base_url}?page={page_num}"
    
    def parse_post(self, post):
        # print(post)        
        try:
            # Extract username
            username_element = post.select_one("article.forumpost header.forumpost__header div.forumpost__user a.forumpost__username")
            username = username_element.get_text(strip=True) if username_element else "Unknown"

            date_element = post.select_one("article.forumpost header.forumpost__header div.forumpost__user span.forumpost__userdate")
            post_date = date_element.get_text(strip=True) if date_element else "Unknown"
            
            content_element = post.select_one("article.forumpost div.forumpost__wrapper section.forumpost__maintext")
            content = content_element.get_text(strip=True) if content_element else "Empty"

            post_id = "Unknown"
            anchor_element = post.select_one("article.forumpost a[name]")
            if anchor_element and anchor_element.has_attr("name"):
                post_id = anchor_element["name"]
            
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
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all("li", class_='postlist__item')
            # print(posts)
            page_data = []
            for post in posts:
                post_data = self.parse_post(post)
                if post_data:
                    post_data["page"] = page_num
                    post_data["url"] = url
                    page_data.append(post_data)
            
            print(f"Page {page_num}: Scraped {len(page_data)} posts")
            
            return page_data
            
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            return [], False
    
    def scrape_all_pages(self):
        """Scrape all pages of the forum topic up to max_pages"""
        page_num = 1

        while True:
            page_posts = self.scrape_page(page_num)
            
            if page_posts:
                if page_num > 1 and any(post["post_id"] == page_posts[0]["post_id"] for post in self.data):
                    break
                self.data.extend(page_posts)
                if len(page_posts) < 20:
                    break
            else:
                break
                
                
            delay = random.uniform(0, 2)
            print(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
            
            page_num += 1
                
        # Final save of all data
        self.save_data()
        
        print(f"Completed scraping. Total posts collected: {len(self.data)}")
    
    def save_data(self, filename=None):
        """Save scraped data to CSV"""
        if filename is None:
            filename = self.output_file
            
        os.makedirs("./iex", exist_ok=True)
        
        try:
            filepath = os.path.join("./iex", filename)
            df = pd.DataFrame(self.data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"Successfully saved {len(self.data)} posts to {filepath}")
        except Exception as e:
            print(f"Error saving data: {e}")
        except Exception as e:
            print(f"Error saving data: {e}")

def get_allposts_of_thread(forum_url):
    scraper = ForumScraperClass(forum_url)
    print(f"Starting to scrape {forum_url}")
    scraper.scrape_all_pages()

get_allposts_of_thread("https://www.iex.nl/Forum/Topic/1330712/ABN-AMRO_Beursgang-Abn-Amro.aspx?page=2")

with open(f"./iex/{ticker}.txt", "r") as f:
    for i, line in enumerate(f, 1):
        if i < 68:
            continue  # Skip the first 17 lines
        url = line.strip()
        #abn amro link 18
        if url:  
            print(f"\nLink #{i}")
            get_allposts_of_thread(url)

import glob

# Set the folder path
folder_path = './iex'  # Change to your folder

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
print(csv_files)

# Read and concatenate all CSVs
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

merged_df = pd.concat(df_list, ignore_index=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv('./merged_outputABN.csv', index=False)

from transformers import pipeline

abndf = pd.read_csv("./iex/ABNAMRO.csv")
nlp = pipeline("sentiment-analysis", model="DTAI-KULeuven/robbert-v2-dutch-sentiment",truncation=True)

abndf['sentiment'] = abndf['content'].apply(lambda x: nlp(str(x))[0]['label'])
abndf['score'] = abndf['content'].apply(lambda x: nlp(str(x))[0]['score'])

abndf.to_csv("./iex/ABNAMRO.csv", index=False)