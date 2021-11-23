import requests, os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

def check_for_redirect(response):
    response.raise_for_status()
    if len(response.history):
        raise requests.HTTPError()

def download_file(response, filepath, folder='books/'):
    with open(filepath, 'wb') as file:
        file.write(response.content)

def parse_book_page(soup):
    book_header_layout = soup.find('div', id='content').find('h1')
    title, author = book_header_layout.text.split('::')

    book_info = {
        'title': title.strip(),
        'author': author.strip(),
    }

    return book_info

def parse_book_info(book_id, url_template='https://tululu.org/b{book_id}/'):
    response = requests.get(
        url_template.format(book_id=book_id),allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_info = parse_book_page(soup)

    book_info['id'] = book_id

    return book_info

def main():
    site_url = "https://tululu.org/txt.php"
    folder = 'books'
    os.makedirs(folder, exist_ok=True)
    for book_id in range(1,11):
        params = {'id': book_id}
        response = requests.get(site_url, params=params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        book_info = parse_book_info(book_id)
        filename = f'{book_id}. {sanitize_filename(book_info["title"])}.txt'
        filepath = os.path.join(os.getcwd(), folder, filename)
        download_file(response,filepath)

if __name__ == '__main__':
    main()