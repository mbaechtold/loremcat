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


def download_image(url, directory, filename):
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / filename
    print(f"save image: {path}")
    try:
        image = requests.get(url)
    except:
        print("image download failed")
        return
    with open(path, "wb") as f:
        f.write(image.content)


def handle_photos(search_results):
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
        download_image(url, IMAGES_PATH / orientation, filename)


def search(flickr, page=1):
    search_results = flickr.photos.search(
        text="cat",
        tags="-lion",
        per_page=os.getenv("FLICKR_PAGE_SIZE", "100"),
        extras=SIZE,
        content_types="0",
        license="2,3,4,5,6,9",
        sort="relevance",
        page=page,
    )
    if search_results["stat"] != "ok":
        return None
    return search_results


def get_number_pages(flickr):
    search_results = search(flickr)
    if search_results is None:
        return None
    return min(
        int(os.getenv("FLICKR_NB_PAGES", 1)),
        search_results["photos"]["pages"],
    )


def fetch():
    FLICKR_API_KEY = os.getenv("FLICKR_API_KEY")
    FLICKR_API_SECRET = os.getenv("FLICKR_API_SECRET")

    flickr = flickrapi.FlickrAPI(
        FLICKR_API_KEY,
        FLICKR_API_SECRET,
        format="parsed-json",
        cache=True,
        token_cache_location="cache",
    )

    pages = get_number_pages(flickr)
    if pages is None:
        print("no pages")
        return

    for page in range(1, pages + 1):
        print(f"page {page}")
        search_results = search(flickr, page)
        if search_results is not None:
            handle_photos(search_results)


if __name__ == "__main__":
    fetch()
