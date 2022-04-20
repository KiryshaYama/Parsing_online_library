import json
import os

def save_to_json(book_items, json_filepath):
    json_filepath = os.path.join(json_filepath, 'book_items.json')
    with open(json_filepath, 'w', encoding='utf-8') as file:
        json.dump(book_items, file, indent=4, ensure_ascii=False)
