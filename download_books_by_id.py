import requests
import os
import argparse
import json

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urlparse, urljoin
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


def download_image(book_img_url, img_filepath):
    response = requests.get(book_img_url)
    response.raise_for_status()
    img_filepath = os.path.join(img_filepath, os.path.basename(
                                  unquote(urlparse(book_img_url).path)))
    with open(img_filepath, 'wb') as file_obj:
        file_obj.write(response.content)
    return img_filepath


def download_txt(book_id, title, text, txt_filepath):
    txt_filepath = os.path.join(
        txt_filepath,
        sanitize_filename(f'{book_id}. {title}.txt')
    )
    with open(txt_filepath, 'w', encoding='utf-8') as file_obj:
        file_obj.write(text)


def parse_book_info(url):
    response = requests.get(url)
    response.raise_for_status()
    if len(response.history) > 1:
        raise requests.HTTPError
    soup = BeautifulSoup(response.text, 'lxml')
    book_header_layout = soup.select_one('h1')
    title, author = book_header_layout.text.split('::')
    book_img_layout = soup.select_one('.bookimage img')
    book_img_url = urljoin(response.url, book_img_layout['src'])
    comment_soups = soup.select('.texts')
    comments = [comment_layout.select_one('span').text
                for comment_layout in comment_soups]
    genres_soups = soup.select('span.d_book')
    genres = [genre.select_one('a').text for genre in genres_soups]
    book_id = urlparse(url).path[2:]
    book_info = {
        'title': title.strip(),
        'author': author.strip(),
        'book_img_url': book_img_url,
        'comments': comments,
        'genres': genres,
        'id': book_id
    }
    return book_info


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
    books_json = list()
    for book_id in tqdm(range(args.start_index, args.stop_index+1)):
        params = {'id': book_id}
        response = requests.get(url='https://tululu.org/txt.php',
                                params=params)
        response.raise_for_status()
        try:
            book_url = 'https://tululu.org/b' + str(book_id)
            parsed_book_info = parse_book_info(book_url)
            if not args.skip_txt:
                download_txt(
                    parsed_book_info['id'],
                    parsed_book_info['title'],
                    response.text,
                    txt_filepath
                )
                parsed_book_info.update(
                    book_path=os.path.join(
                        txt_filepath,
                        sanitize_filename(
                            f'{parsed_book_info["id"]}. '
                            f'{parsed_book_info["title"]}.txt')
                    )
                )
            if not args.skip_imgs:
                download_image(parsed_book_info['book_img_url'], img_filepath)
                parsed_book_info.update(
                    img_src=os.path.join(
                        img_filepath,
                        os.path.basename(
                            unquote(
                                urlparse(
                                    parsed_book_info['book_img_url']).path
                            )
                        )
                    )
                )
            books_json.append(parsed_book_info)

        except requests.exceptions.HTTPError:
            continue
    json_filepath = os.path.join(json_filepath, 'books.json')
    with open(json_filepath, 'w', encoding='utf-8') as file:
        json.dump(books_json, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
