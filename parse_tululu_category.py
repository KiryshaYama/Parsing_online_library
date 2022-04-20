import requests
import argparse

from save_to_json import save_to_json
from parse_book_info import parse_book_info
from download_txt import download_txt
from download_image import download_image
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm


def parse_pages(start_page, end_page):
    book_items = list()
    for page in tqdm(range(start_page, end_page)):
        url = f'https://tululu.org/l55/{page}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.find('div', id='content').find_all('div',
                                                        class_='bookimage')
        try:
            for book in books:
                book_url = urljoin('https://tululu.org',
                                   book.select_one('a')['href'][:-1])
                response = requests.get(book_url)
                response.raise_for_status()
                book_info = parse_book_info(book_url)
                params = {'id': book_info['id']}
                response = requests.get(url='https://tululu.org/txt.php',
                                        params=params)
                download_txt(book_info['id'], book_info['title'],
                             response.text)
                download_image(book_info['book_img_url'])
                book_items.append(book_info)
        except requests.exceptions.HTTPError:
            continue
    save_to_json(book_items)


def get_last_page():
    url = 'http://tululu.org/l55'
    response = requests.get(url)
    response.raise_for_status()
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
        default=get_last_page() + 1,
        type=int,
        help='Конечный номер страницы, по умолчанию: 701',
    )
    return parser.parse_args()


def main():

    args = parse_arguments()
    if args.start_page < 1:
        args.start_page = 1
    if args.end_page < args.start_page:
        raise ValueError('Input indexes range is wrong: '
                         f'from {args.start_page} to {args.end_page}')
    parse_pages(args.start_page, args.end_page)


if __name__ == '__main__':
    main()
