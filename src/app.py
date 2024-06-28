from flask import Flask, render_template
import parse_html

from constants import BUILD_DIR

app = Flask(__name__)

# Set the destination directory for Frozen-Flask
app.config['FREEZER_DESTINATION'] = 'path/to/your/static_site'


@app.route('/')
def home():
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    parsed_data = parse_html.parse_html(html_content)

    indexed_data = [{'index': idx + 1, 'content': text} for idx, text in enumerate(parsed_data)]

    rendered_template = render_template('index.html', texts=indexed_data)

    generated_index_html = BUILD_DIR / 'index.html'
    with open(generated_index_html, "w", encoding="utf-8") as file:
        file.write(rendered_template)
    print("HTML content rendered and saved to index.html")

    return rendered_template


if __name__ == "__main__":
    app.run(debug=True)
