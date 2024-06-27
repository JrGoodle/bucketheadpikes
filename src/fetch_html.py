import requests

def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

if __name__ == "__main__":
    url = "http://www.bucketheadpikes.com"
    html_content = fetch_html(url)
    with open("page.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("HTML content fetched and saved to page.html")
