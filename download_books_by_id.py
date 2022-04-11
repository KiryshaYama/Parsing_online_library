import requests
import os
import argparse
from parse_book_info import parse_book_info
from check_for_errors import check_for_errors

from download_txt import download_txt
from download_image import download_image
from tqdm import tqdm


def get_file_path(root_path, folder_name, filename):
    path = os.path.join(root_path, folder_name) if root_path else folder_name
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)


def download_books(start_index, stop_index):
    for book_id in tqdm(range(start_index, stop_index)):
        params = {'id': book_id}
        response = requests.get(url='https://tululu.org/txt.php',
                                params=params)
        try:
            check_for_errors(response)
            book_url = 'https://tululu.org/b' + str(book_id)
            book_info = parse_book_info(book_url)
            download_txt(book_info['id'], book_info['title'], response.text)
            download_image(book_info['book_img_url'])
        except requests.exceptions.HTTPError:
            continue


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Download books in TXT'
    )
    parser.add_argument(
        'start_index',
        type=int,
        help='start index to download books in book ID\
        range from start to stop'
    )
    parser.add_argument(
        'stop_index',
        type=int,
        help='stop index to download books in book ID range from start to stop'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.start_index < 1:
        args.start_index = 1
    if args.stop_index < args.start_index:
        raise ValueError('Input indexes range is wrong: '
                         f'from {args.start_index} to {args.stop_index}')
    download_books(args.start_index, args.stop_index+1)


if __name__ == '__main__':
    main()
