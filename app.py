import random

from flask import Flask
from flask import send_from_directory

from config import IMAGES_PATH


app = Flask(__name__)


@app.route("/")
def homepage():
    path = IMAGES_PATH / "landscape"
    files = list(path.glob("*.jpg"))
    file = random.choice(files)
    return send_from_directory(path, file.name)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
