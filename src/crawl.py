import os
import shutil

import requests
from urllib.parse import urlparse, urljoin, urldefrag


# Function to fetch a web page and return its content
def fetch_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None


# Function to save content to a file or copy static assets
def save_content(url, content, base_dir):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('/'):
        path += 'index.html'  # If URL ends with '/', save as index.html
    elif not path.endswith('.html'):
        # if path.endswith('.mp3') or path.endswith('.jpg'):
        #     return
        path += '.html'  # Append .html if not already present

    # Create directory structure based on URL path
    full_path = os.path.join(base_dir, parsed_url.netloc, path.lstrip('/'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Write content to file
    with open(full_path, 'wb') as f:
        f.write(content)
    print(f"Saved: {url} => {full_path}")

    # Copy static assets (images, CSS, JS) if applicable
    if full_path.endswith(('.html', '.htm')):
        copy_static_assets(url, content, base_dir, os.path.dirname(full_path))


def copy_static_assets(base_url, html_content, base_dir, dest_dir):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all tags that contain static assets (img, link, script, etc.)
    for tag in soup.find_all(['img', 'link', 'script'], src=True):
        url = urljoin(base_url, tag.get('src'))

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, stream=True, headers=headers)
            if response.status_code == 200:
                parsed_path = urlparse(url).path
                parsed_path = parsed_path.removeprefix('/')
                # temp_path = os.path.basename(parse_url)
                file_path = os.path.join(dest_dir, parsed_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print(f"Copied asset: {url} => {file_path}")
            else:
                print(f"Failed to fetch asset: {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching asset: {url}: {e}")


# Function to crawl a website recursively
def crawl_site(url, base_dir):
    visited_urls = set()
    original_domain = urlparse(url).netloc.lower()

    def is_valid(url):
        parsed_url = urlparse(url)
        return parsed_url.netloc.lower() == original_domain

    def crawl(url):
        if url in visited_urls:
            return
        visited_urls.add(url)

        content = fetch_page(url)
        if content:
            save_content(url, content, base_dir)

            # Parse links and recursively crawl them
            links = parse_links(url, content)
            for link in links:
                if is_valid(link):
                    crawl(link)

    crawl(url)


# Function to parse links from HTML content
def parse_links(base_url, html_content):
    from bs4 import BeautifulSoup
    links = set()
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        absolute_url = urljoin(base_url, link['href'])
        # Remove fragments to avoid duplicates (e.g., page#section)
        absolute_url = urldefrag(absolute_url)[0]
        links.add(absolute_url)
    return links


if __name__ == "__main__":
    # Replace with your starting URL and base directory to save files
    start_url = "http://www.bucketheadpikes.com/"
    save_directory = "static_site"

    crawl_site(start_url, save_directory)
