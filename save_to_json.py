from make_file_path import get_file_path
from pathvalidate import sanitize_filename
import json

def save_to_json(book_items, root_path=None, folder_name='items'):
    file_path = get_file_path(root_path, folder_name, sanitize_filename(
        'book_items.json'))
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(book_items, file, indent=4, ensure_ascii=False)
