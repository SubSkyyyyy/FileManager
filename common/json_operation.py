import os
import json

from common.config import HISTORY_FILE_PATH
from common.utils import CombineDict


def write_to_json(file_name: str, data, force=False):
    json_file_path = os.path.join(HISTORY_FILE_PATH, file_name)
    if not os.path.isdir(HISTORY_FILE_PATH):
        os.makedirs(HISTORY_FILE_PATH)
    if force:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    else:
        origin_data = read_json(file_name, type(data))
        if isinstance(data, list):
            origin_data.append(data)
        else:
            origin_data = CombineDict(origin_data)
            origin_data.update_each_level(data)
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(origin_data, f, ensure_ascii=False)


def read_json(file_name: str, target_type=dict):
    json_file_path = os.path.join(HISTORY_FILE_PATH, file_name)
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            origin_data = json.load(f)
    except Exception:
        origin_data = target_type()
    return origin_data
