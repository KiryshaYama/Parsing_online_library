import requests
import os

from check_for_redirect import check_for_redirect
from urllib.parse import unquote, urlparse
from make_file_path import get_file_path


def download_image(book_img_url, img_filepath):
    response = requests.get(book_img_url)
    check_for_redirect(response)
    img_filepath = os.path.join(img_filepath, os.path.basename(
                                  unquote(urlparse(book_img_url).path)))
    with open(img_filepath, 'wb') as file_obj:
        file_obj.write(response.content)
    return img_filepath
