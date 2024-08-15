import os
import requests
from bs4 import BeautifulSoup
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_pfps(base_url, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    page = 1
    while True:
        url = f"{base_url}&page={page}&sort=recent"
        logging.info(f"Scraping page {page}: {url}")
        
        response = requests.get(url, headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1"
        })
        
        if response.status_code != 200:
            logging.warning(f"Failed to scrape page {page}. status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', src=True)
        cdn_links = [img['src'] for img in images if 'cdn.pfps.gg' in img['src']]
        
        if not cdn_links:
            logging.info("No more images found. Stopping.")
            break
        
        for link in cdn_links:
            image_name = os.path.basename(link)
            image_path = os.path.join(save_dir, image_name)
            download_image(link, image_path)
        
        page += 1

def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Saved image: {path}")
    else:
        logging.warning(f"Failed to download image from {url}. Status code: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape PFPs from pfps.gg")
    parser.add_argument('base_url', type=str, help="URL for the specific pfps.gg catagory to scrape")
    parser.add_argument('save_dir', type=str, help="Directory to save the images")
    
    args = parser.parse_args()
    scrape_pfps(args.base_url, args.save_dir)
