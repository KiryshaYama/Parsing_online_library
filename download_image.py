import requests
import os

from urllib.parse import unquote, urlparse
from make_file_path import get_file_path
from check_for_errors import check_for_errors


def download_image(book_img_url, root_path=None, folder_name='images'):
    response = requests.get(book_img_url)
    check_for_errors(response)
    file_path = get_file_path(root_path, folder_name,
                              os.path.basename(
                                  unquote(urlparse(book_img_url).path)))
    with open(file_path, 'wb') as file_obj:
        file_obj.write(response.content)
    return file_path
