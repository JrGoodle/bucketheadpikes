from bs4 import BeautifulSoup, NavigableString

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    ps = soup.find_all('p')
    ps_filtered = []
    for p in ps:
        children = list(p.children)
        num_children = len(children)
        if num_children == 0:
            continue
        elif num_children == 1:
            child = children[0]
            if isinstance(child, NavigableString):
                if child == '\xa0':
                    continue
        ps_filtered.append(p)
    # Extract relevant information. For example, let's get all the links:
    # links = soup.find_all('a')
    # parsed_data = [{'text': link.get_text(), 'href': link.get('href')} for link in links]
    # return parsed_data
    return ps_filtered


def extract_images(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract image URLs
    images = soup.find_all('img')
    image_urls = [img.get('src') for img in images if img.get('src')]
    return image_urls


if __name__ == "__main__":
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    parsed_data = parse_html(html_content)
    print(parsed_data)
