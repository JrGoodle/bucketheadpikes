import requests

def fetch_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

if __name__ == "__main__":
    url = "https://www.bucketheadpikes.com"
    html_content = fetch_html(url)
    with open("page.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("HTML content fetched and saved to page.html")
