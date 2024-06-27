import bs4
from bs4 import BeautifulSoup, NavigableString

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    ps = soup.find_all('p')
    ps_filtered = []
    was_separator = False
    current_div = soup.new_tag('div')
    for p in ps:
        children = list(p.children)
        num_children = len(children)
        if num_children == 0:
            if not was_separator:
                ps_filtered.append(current_div)
                current_div = soup.new_tag('div')
            was_separator = True
            continue
        elif num_children == 1:
            child = children[0]
            if isinstance(child, NavigableString):
                if child == '\xa0':
                    if not was_separator:
                        ps_filtered.append(current_div)
                        current_div = soup.new_tag('div')
                    was_separator = True
                    continue
        current_div.append(p)
        was_separator = False

    for para in ps_filtered:
        # Find all <img> tags within the <p> tag
        images = para.find_all('img')
        for img in images:
            if not str(img['src']).startswith('/static'):
                # Update the src attribute to point to static/images directory
                img['src'] = f"/static/{img['src']}"

    # Extract relevant information. For example, let's get all the links:
    # links = soup.find_all('a')
    # parsed_data = [{'text': link.get_text(), 'href': link.get('href')} for link in links]
    # return parsed_data
    text_content = [str(para) for para in ps_filtered]
    return text_content


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
