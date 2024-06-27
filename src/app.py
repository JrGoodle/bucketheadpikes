from flask import Flask, render_template
import parse_html

app = Flask(__name__)


@app.route('/')
def home():
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    parsed_data = parse_html.parse_html(html_content)
    rendered_template = render_template('index.html', texts=parsed_data)
    return rendered_template


if __name__ == "__main__":
    app.run(debug=True)
