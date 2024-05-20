import os
import re
import shutil

from common.json_operation import write_to_json, read_json

JSON_FILE_NAME_DICT = {
    'move_up': 'move_up.json',
    'move_to_target': 'move_to_target.json',
    'move_to_parent_folder': 'move_to_parent_folder.json',
    'move_single_file_to_parent_folder': 'move_single_file_to_parent_folder'
}


def move_file(root_path, pattern, operation, target_folder='', with_parent_name=False):
    json_file_name = JSON_FILE_NAME_DICT[operation]
    dir_list = list(os.walk(root_path))
    move_dicts = {}
    for root, dirs, files in dir_list:
        if operation != 'move_single_file_to_parent_folder':
            for file in files:
                origin_path = os.path.join(root, file)
                if not os.path.isfile(origin_path) or not re.match(pattern, file):
                    continue
                new_file_name: str = file
                parent_path, parent_name = os.path.split(root)
                if root < root_path:
                    continue
                if with_parent_name and (
                        not new_file_name.startswith(parent_name) or new_file_name.split('.')[0] == parent_name):
                    new_file_name = '{}_{}'.format(parent_name, file)

                if operation in 'move_up':
                    target_dir = parent_path
                elif operation == 'move_to_target':
                    target_dir = os.path.join(root_path, target_folder)
                else:
                    target_dir = os.path.join(root, target_folder)

                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, new_file_name)

                if os.path.isfile(target_path):
                    start_idx = 1
                    while os.path.isfile(target_path):
                        new_file_name_part, ext = os.path.splitext(new_file_name)
                        new_file_name = '{}_{}{}'.format(new_file_name, start_idx, ext)
                        target_path = os.path.join(parent_path, new_file_name)
                        start_idx += 1
                move_dicts[origin_path] = target_path
        else:
            for dir in dirs:
                origin_path = os.path.join(root, dir)
                if not os.path.isdir(origin_path):
                    continue
                file_list = os.listdir(origin_path)
                if len(file_list) != 1:
                    continue
                file = file_list[0]
                origin_path = os.path.join(origin_path, file)
                if not os.path.isfile(origin_path):
                    continue
                _, ext = os.path.splitext(file)
                target_path = os.path.join(root, '{}{}'.format(dir, ext))
                move_dicts[origin_path] = target_path

    for o_path in move_dicts:
        shutil.move(o_path, move_dicts[o_path])
        record_dict = {
            root_path: {
                pattern: {
                    o_path: move_dicts[o_path]
                }
            }
        }
        write_to_json(json_file_name, record_dict)

    remove_empty_dir(root_path)


def remove_empty_dir(root_path):
    for dir_p in os.listdir(root_path):
        path = os.path.join(root_path, dir_p)
        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                os.removedirs(path)
                continue
            remove_empty_dir(path)


def file_move_roll_back(root_path, pattern, operation):
    json_file_name = JSON_FILE_NAME_DICT.get(operation)
    json_record = read_json(json_file_name)
    records = json_record.get(root_path, {}).get(pattern, {})
    if not records:
        raise Exception('没有对该目录及正则式执行过该操作!')
    for origin_path in records:
        target_dir = records[origin_path]
        if os.path.isfile(target_dir):
            origin_dir = os.path.split(origin_path)[0]
            if not os.path.isdir(origin_dir):
                os.makedirs(origin_dir)
            shutil.move(target_dir, origin_path)
    json_record[root_path].pop(pattern)
    if not json_record[root_path]:
        json_record.pop(root_path)
    write_to_json(json_file_name, json_record, force=True)
    remove_empty_dir(root_path)
