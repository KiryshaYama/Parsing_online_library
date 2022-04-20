import requests
import os

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def parse_book_info(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_header_layout = soup.select_one('h1')
    title, author = book_header_layout.text.split('::')
    book_img_layout = soup.select_one('.bookimage img')
    book_img_url = urljoin(response.url, book_img_layout['src'])
    comment_soups = soup.select('.texts')
    comments = [
        comment_layout.select_one('span').text for comment_layout in comment_soups]
    genres_soups = soup.select('span.d_book')
    genres = [genre.select_one('a').text for genre in genres_soups]
    book_id = urlparse(url).path[2:]
    book_info = {
        'title': title.strip(),
        'author': author.strip(),
        'book_img_url': book_img_url,
        'img_src': f'/images/{os.path.split(book_img_layout["src"])[-1]}',
        'book_path': f'/books/{book_id}.txt',
        'comments': comments,
        'genres': genres,
        'id': book_id
    }
    return book_info
