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


ticker = "SHELL-PLC"
id = 210964

def scrape_forum(url):
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
        
        if f".aspx?startpost=" in next_page:
            base_path = "/".join(base_url.split("/")[:-1]) + "/"
            current_url = base_path + next_page
        else:
            if next_page.startswith('../../'):
                next_page = "https://www.iex.nl/Forum-Aandeel/" + next_page[6:]
            elif not next_page.startswith('http'):
                base_domain = re.match(r'(https?://[^/]+)', base_url).group(1)
                if not next_page.startswith('/'):
                    next_page = '/' + next_page
                next_page = base_domain + next_page
            current_url = next_page
        
        page_count += 1
        
        time.sleep(1)
        
    return all_hrefs

try:
    starting_url = f"https://www.iex.nl/Forum-Aandeel/{id}/{ticker}.aspx"
    topic_links = scrape_forum(starting_url)
    
    print(f"\nTotal links collected: {len(topic_links)}")
    
    # Optionally save to file
    with open(f"./iex/{ticker}list.txt", "w") as f:
        for link in topic_links:
            f.write(f"{link}\n")
    
    print(f"Links saved to {ticker}.txt")
except Exception as e:
    print(e)