import requests
import os
import argparse

from pathvalidate import sanitize_filename
from urllib.parse import unquote, urlparse
from parse_book_info import parse_book_info
from download_txt import download_txt
from download_image import download_image
from tqdm import tqdm


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
    parser.add_argument(
        '--dest_folder',
        default='',
        help='Путь к каталогу "куда скачивать"',
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
        default=False,
        help='Не скачивать картинки',
    )
    parser.add_argument(
        '--skip_txt',
        action='store_true',
        default=False,
        help='Не скачивать книги',
    )
    parser.add_argument(
        '--json_path',
        help='Путь к .json файлу с результатами',
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    txt_filepath = os.path.join(args.dest_folder, 'books')
    img_filepath = os.path.join(args.dest_folder, 'images')
    os.makedirs(txt_filepath, exist_ok=True)
    os.makedirs(img_filepath, exist_ok=True)
    if args.json_path:
        json_filepath = args.json_path
    else:
        json_filepath = args.dest_folder
    if args.start_index < 1:
        args.start_index = 1
    if args.stop_index < args.start_index:
        raise ValueError('Input indexes range is wrong: '
                         f'from {args.start_index} to {args.stop_index}')
    book_items = list()
    for book_id in tqdm(range(args.start_index, args.stop_index+1)):
        params = {'id': book_id}
        response = requests.get(url='https://tululu.org/txt.php',
                                params=params)
        response.raise_for_status()
        try:
            book_url = 'https://tululu.org/b' + str(book_id)
            book_info = parse_book_info(book_url)
            if not args.skip_txt:
                download_txt(book_info['id'], book_info['title'], response.text, txt_filepath)
                book_info.update(book_path=os.path.join(txt_filepath, sanitize_filename(
                    f'{book_info["id"]}. {book_info["title"]}.txt')))
            if not args.skip_imgs:
                download_image(book_info['book_img_url'], img_filepath)
                book_info.update(
                    img_src=os.path.join(img_filepath, os.path.basename(
                        unquote(urlparse(book_info['book_img_url']).path)))
                )
            book_items.append(book_info)

        except requests.exceptions.HTTPError:
            continue
    json_filepath = os.path.join(json_filepath, 'book_items.json')
    with open(json_filepath, 'w', encoding='utf-8') as file:
        json.dump(book_items, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
