import requests, os

import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlparse
from tqdm import tqdm

def check_for_errors(response):
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError()

def get_file_path(root_path, folder_name, filename):
    path = os.path.join(root_path, folder_name) if root_path else folder_name
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)

def download_image(book_img_url, root_path=None, folder_name='images'):
    response = requests.get(book_img_url)
    response.raise_for_status()
    check_for_errors(response)

    file_path = get_file_path(root_path, folder_name, os.path.basename(unquote(urlparse(book_img_url).path)))

    with open(file_path, 'wb') as file_obj:
        file_obj.write(response.content)
    return file_path

def parse_book_info(book_id, url_template='https://tululu.org/b{book_id}/'):
    response = requests.get(
        url_template.format(book_id=book_id),allow_redirects=False)
    response.raise_for_status()
    check_for_errors(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_header_layout = soup.find('div', id='content').find('h1')
    title, author = book_header_layout.text.split('::')
    book_img_layout = soup.find('div', class_='bookimage').find('img')
    book_img_url = urljoin(response.url, book_img_layout['src'])
    comment_soups = soup.find_all('div', class_='texts')
    comments = [comment_layout.find('span').text for comment_layout in comment_soups]
    genres_soups = soup.find_all('span', class_='d_book')
    genres = [genre.find('a').text for genre in genres_soups]
    book_info = {'title': title.strip(), 'author': author.strip(), 'book_img_url': book_img_url, 'comments': comments,
                 'genres': genres, 'id': book_id, }
    return book_info

def download_books(start_index, stop_index):
    for book_id in tqdm(range(start_index, stop_index)):
        params = {'id': book_id}
        response = requests.get(url='https://tululu.org/txt.php', params=params)
        try:
            check_for_errors(response)
            book_info = parse_book_info(book_id)
            save_book(book_info['id'], book_info['title'], response.text)
            download_image(book_info['book_img_url'])
        except requests.exceptions.HTTPError:
            continue

def save_book(book_id, title, text, root_path=None, folder_name='books'):
    file_path = get_file_path(root_path, folder_name, sanitize_filename(f'{book_id}. {title}.txt'))

    with open(file_path, 'w', encoding='utf-8') as file_obj:
        file_obj.write(text)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Download books in TXT'
    )
    parser.add_argument(
        'start_index',
        type=int,
        help='start index to download books in book ID range from start to stop',
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