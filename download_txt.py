from make_file_path import get_file_path
from pathvalidate import sanitize_filename


def download_txt(book_id, title, text, root_path=None, folder_name='books'):
    file_path = get_file_path(root_path, folder_name, sanitize_filename(
        f'{book_id}. {title}.txt'))
    with open(file_path, 'w', encoding='utf-8') as file_obj:
        file_obj.write(text)
