import requests

from check_for_errors import check_for_errors
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def parse_book_info(url):
    response = requests.get(url)
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
    book_id = urlparse(url).path[2:-1]
    book_info = {'title': title.strip(), 'author': author.strip(), 'book_img_url': book_img_url, 'comments': comments,
                 'genres': genres, 'id': book_id, }
    return book_info