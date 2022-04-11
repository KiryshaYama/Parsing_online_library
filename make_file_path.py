import os


def get_file_path(root_path, folder_name, filename):
    path = os.path.join(root_path, folder_name) if root_path else folder_name
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)
