import requests
import os

from urllib.parse import unquote, urlparse


def download_image(book_img_url, img_filepath):
    response = requests.get(book_img_url)
    response.raise_for_status()
    img_filepath = os.path.join(img_filepath, os.path.basename(
                                  unquote(urlparse(book_img_url).path)))
    with open(img_filepath, 'wb') as file_obj:
        file_obj.write(response.content)
    return img_filepath
