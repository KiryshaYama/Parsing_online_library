from pathvalidate import sanitize_filename
import os

def download_txt(book_id, title, text, txt_filepath):
    txt_filepath = os.path.join(txt_filepath, sanitize_filename(f'{book_id}. {title}.txt'))
    with open(txt_filepath, 'w', encoding='utf-8') as file_obj:
        file_obj.write(text)
