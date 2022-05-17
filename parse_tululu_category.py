import requests
import argparse
import os
import json

from pathvalidate import sanitize_filename
from urllib.parse import urljoin, unquote, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_last_page(category_id):
    url = f'https://tululu.org/{category_id}/'
    response = requests.get(url)
    check_for_errors(response)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = int(soup.select_one('.npage:last-child').text)
    return last_page


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Download books in TXT'
    )
    parser.add_argument(
        '--start_page',
        default=1,
        type=int,
        help='Начальный номер страницы, по умолчанию: 1'
    )
    parser.add_argument(
        '--end_page',
        default=get_last_page(category_id) + 1,
        type=int,
        help='Номер последней страницы в категории',
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


def check_for_errors(response):
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError


def download_image(book_img_url, img_filepath):
    response = requests.get(book_img_url)
    check_for_errors(response)
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
    check_for_errors(response)
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
    book_id = urlparse(url).path[3:-1]
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
    if args.start_page < 1:
        args.start_page = 1
    if args.end_page < args.start_page:
        raise ValueError('Input indexes range is wrong: '
                         f'from {args.start_page} to {args.end_page}')
    books_details = list()
    for page in tqdm(range(args.start_page, args.end_page)):
        url = f'https://tululu.org/{category_id}/{page}/'
        response = requests.get(url)
        check_for_errors(response)
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.find('div', id='content').find_all('div',
                                                        class_='bookimage')
        try:
            for book in books:
                book_id = book.select_one("a")["href"][:-1]
                book_url = f'https://tululu.org/{book_id}/'
                response = requests.get(book_url)
                check_for_errors(response)
                parsed_book_info = parse_book_info(book_url)
                if not args.skip_txt:
                    params = {'id': parsed_book_info['id']}
                    response = requests.get(url='https://tululu.org/txt.php',
                                            params=params)
                    if not check_for_errors(response):
                        download_txt(
                            parsed_book_info['id'],
                            parsed_book_info['title'],
                            response.text,
                            txt_filepath
                        )
                        txt_filename = f'{parsed_book_info["id"]}.' \
                                       f'{parsed_book_info["title"]}.txt'
                        clean_txt_filename = sanitize_filename(txt_filename)
                        book_path = os.path.join(
                            txt_filepath,
                            clean_txt_filename
                        )
                        parsed_book_info.update(book_path=book_path)
                if not args.skip_imgs:
                    download_image(
                        parsed_book_info['book_img_url'],
                        img_filepath
                    )
                    img_filename = unquote(
                        urlparse(parsed_book_info['book_img_url']).path
                    )
                    clear_img_filename = os.path.basename(img_filename)
                    img_src = os.path.join(img_filepath, clear_img_filename)
                    parsed_book_info.update(img_src=img_src)
                books_details.append(parsed_book_info)
        except requests.exceptions.HTTPError:
            continue
    json_filepath = os.path.join(json_filepath, 'books.json')
    with open(json_filepath, 'w', encoding='utf-8') as file:
        json.dump(books_details, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    category_id = 'l55'
    main()
