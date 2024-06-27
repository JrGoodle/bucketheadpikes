import os
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


# Function to save content to a file
def save_page(url, content, base_dir):
    # if str(url).endswith('.'):
    #     print()
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('/'):
        path += 'index.html'  # If URL ends with '/', save as index.html
    elif not path.endswith('.html'):
        if path.endswith('.mp3') or path.endswith('.jpg'):
            return
        path += '.html'  # Append .html if not already present

    # Create directory structure based on URL path
    full_path = os.path.join(base_dir, parsed_url.netloc, path.lstrip('/'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Write content to file
    with open(full_path, 'wb') as f:
        f.write(content)
    print(f"Saved: {url} => {full_path}")


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
            save_page(url, content, base_dir)

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
    save_directory = "website_pages"

    crawl_site(start_url, save_directory)
