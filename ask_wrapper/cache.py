import json
import os


CACHE_DIR = 'ask_cache'


def save_dict(dict_obj: dict, title: str, root_dir: str):
    output_file = f'{os.path.join(root_dir, CACHE_DIR, title)}.json'
    output_folder = os.path.split(output_file)[0]
    os.makedirs(output_folder, exist_ok=True)
    json.dump(dict_obj, open(output_file, 'w'), indent=2, ensure_ascii=False)
    return output_file
