import os
import requests
from parse_html import extract_images


def download_image(url, folder='images'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, stream=True, headers=headers)
    if response.status_code == 200:
        image_name = os.path.join(folder, url.split("/")[-1])
        with open(image_name, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded {url}")
    else:
        print(f"Failed to download {url}")


if __name__ == "__main__":
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    image_urls = extract_images(html_content)

    for url in image_urls:
        # Handle relative URLs
        if not url.startswith('https'):
            url = f"https://www.bucketheadpikes.com/{url}"
        download_image(url)
