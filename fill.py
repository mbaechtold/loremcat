import os
import pathlib
import urllib
from urllib.parse import urlparse

from dotenv import load_dotenv
import flickrapi
import requests

from config import HEIGHT
from config import IMAGES_PATH
from config import SIZE
from config import WIDTH


load_dotenv()


def download(url, directory, filename):
    path = directory / filename
    print(f"downloading: {filename}")
    image = requests.get(url)
    with open(path, "wb") as f:
        f.write(image.content)


def store(search_results):
    if search_results["stat"] != "ok":
        return

    for photo in search_results["photos"]["photo"]:
        if SIZE not in photo:
            print("url missing")
            continue
        orientation = "landscape" if photo[WIDTH] > photo[HEIGHT] else "portrait"
        filename = pathlib.Path(urllib.parse.urlparse(photo[SIZE]).path).name
        path = IMAGES_PATH / orientation / filename
        if path.exists():
            print(f"image already exists: {filename}")
            continue
        url = photo[SIZE]
        download(url, IMAGES_PATH / orientation, filename)


def run():
    FLICKR_API_KEY = os.getenv("FLICKR_API_KEY")
    FLICKR_API_SECRET = os.getenv("FLICKR_API_SECRET")

    flickr = flickrapi.FlickrAPI(
        FLICKR_API_KEY,
        FLICKR_API_SECRET,
        format="parsed-json",
        cache=True,
        token_cache_location="cache",
    )
    search_results = flickr.photos.search(
        text="cat",
        tags="-lion",
        per_page="100",
        extras=SIZE,
        content_types="0",
        license="2,3,4,5,6,9",
        sort="relevance",
    )
    if search_results["stat"] != "ok":
        return
    pages = min(20, search_results["photos"]["pages"])
    for i in range(1, pages):
        print(f"page {i}")
        search_results = flickr.photos.search(
            text="cat",
            tags="-lion",
            per_page="100",
            page=i,
            extras=SIZE,
            content_types="0",
            license="2,3,4,5,6,9",
            sort="relevance",
        )
        store(search_results)


if __name__ == "__main__":
    run()
