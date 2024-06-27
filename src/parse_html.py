from bs4 import BeautifulSoup

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract relevant information. For example, let's get all the links:
    links = soup.find_all('a')
    parsed_data = [{'text': link.get_text(), 'href': link.get('href')} for link in links]
    return parsed_data

if __name__ == "__main__":
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    parsed_data = parse_html(html_content)
    print(parsed_data)
