import requests, os

def check_for_redirect(response):
    response.raise_for_status()
    if len(response.history):
        raise requests.HTTPError()

def download_file(response, file_path):
    with open(file_path, 'wb') as file:
        file.write(response.content)

def main():
    site_url = "https://tululu.org/txt.php"
    folder = 'books'
    os.makedirs(folder, exist_ok=True)
    for book_id in range(1,11):
        params = {'id': book_id}
        file_name = f'id{book_id}.txt'
        file_path = os.path.join(os.getcwd(), folder, file_name)
        response = requests.get(site_url, params=params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue
        download_file(response,file_path)

if __name__ == '__main__':
    main()