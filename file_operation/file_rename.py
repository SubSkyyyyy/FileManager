import os
import shutil
import re

from common.json_operation import write_to_json, read_json


def get_longest_same_part(o_pattern, c_pattern):
    same_part = ''
    for sidx in range(len(c_pattern) - 1):
        for eidx in range(sidx + 2, len(c_pattern) + 1):
            substr = c_pattern[sidx: eidx]
            if substr in o_pattern and len(substr) > 1 and len(substr) > len(same_part):
                same_part = substr
    return same_part


def get_same_parts(pattern1, pattern2):
    same_parts = []
    pattern1s = [pattern1]
    pattern2s = [pattern2]
    while True:
        same_part = ''
        for p1 in pattern1s:
            for p2 in pattern2s:
                _sp = get_longest_same_part(p1, p2)
                if len(_sp) > len(same_part):
                    same_part = _sp
        if same_part:
            same_parts.append(same_part)
            patterns = [pattern1s, pattern2s]
            for pattern in patterns:
                for i in range(len(pattern)):
                    if same_part in pattern[i]:
                        pattern[i: i + 1] = pattern[i].split(same_part, 1)
                        break
                removed_list = []
                for i in range(len(pattern)):
                    if len(pattern[i]) < 2:
                        removed_list.append(i)
                removed_list.sort(reverse=True)
                for i in removed_list:
                    pattern.remove(pattern[i])
        else:
            break
    same_part_dict = {}
    for same_part in same_parts:
        idx = pattern1.index(same_part)
        while idx in same_part_dict:
            idx = pattern1.index(same_part, idx + 1)
        same_part_dict[idx] = same_part
    same_part_dict = dict(sorted(same_part_dict.items(), key=lambda i: i[0]))
    same_parts = list(same_part_dict.values())
    return same_parts


def replace_by_re(pattern_same_parts, origin_str, origin_pattern, target_pattern):
    o_str = re.search(origin_pattern, origin_str).group()
    o_str_back_up = o_str
    for same_part in pattern_same_parts:
        matched_str = re.search(same_part, o_str).group()
        target_pattern = target_pattern.replace(same_part, matched_str, 1)
        o_str = o_str.split(matched_str, 1)[-1]

    return origin_str.replace(o_str_back_up, target_pattern)


def file_rename(root_path, origin_pattern, replace_format, replace_dir_name=False, replace_file_name=False):
    file_name_replace = {}
    dir_name_replace = {}
    for root, dirs, files in os.walk(root_path):
        if replace_file_name:
            for file in files:
                origin_path = os.path.join(root, file)
                if not os.path.isfile(origin_path) or not re.search(origin_pattern, file):
                    continue
                file_name_list = file_name_replace.get(root, [])
                file_name_list.append(file)
                file_name_replace[root] = file_name_list
        if replace_dir_name:
            for dir in dirs:
                origin_path = os.path.join(root, dir)
                if not os.path.isdir(origin_path) or not re.search(origin_pattern, dir):
                    continue
                dir_name_list = dir_name_replace.get(root, [])
                dir_name_list.append(dir)
                dir_name_replace[root] = dir_name_list

    pattern_same_parts = get_same_parts(origin_pattern, replace_format)

    replace_mapping = {}
    for replace_dict in [file_name_replace, dir_name_replace]:
        for item_root in replace_dict:
            items = replace_dict[item_root]
            for item in items:
                target_name = replace_by_re(pattern_same_parts, item, origin_pattern, replace_format)
                target_path = os.path.join(item_root, target_name)
                suffix = 1
                while os.path.exists(target_path) and target_path != os.path.join(item_root, item):
                    name, ext = os.path.splitext(target_name)
                    target_name = '{}-{}{}'.format(name, suffix, ext)
                    suffix += 1
                    target_path = os.path.join(item_root, target_name)
                replace_mapping[os.path.join(item_root, item)] = target_path

    replace_mapping = dict(sorted(replace_mapping.items(), key=lambda i: i[0], reverse=True))
    for origin_item in replace_mapping:
        shutil.move(origin_item, replace_mapping[origin_item])
    history_json = {
        root_path: {
            origin_pattern:
                {
                    replace_format: replace_mapping
                }
        }
    }
    write_to_json('file_rename.json', history_json)


def file_suffix_change(root_path, origin_pattern, replace_format):
    change_dict = {}
    for root, dirs, files in os.walk(root_path):
        for file in files:
            o_path = os.path.join(root, file)
            if not os.path.isfile(o_path) or file.split('.')[-1] != origin_pattern:
                continue
            new_name = file.replace(origin_pattern, replace_format)
            t_path = os.path.join(root, new_name)
            change_dict[o_path] = t_path
    for o_path in change_dict:
        shutil.move(o_path, change_dict[o_path])
    history_json = {
        root_path: {
            origin_pattern:
                {
                    replace_format: change_dict
                }
        }
    }
    write_to_json('file_rename.json', history_json)


def rename_roll_back(root_path, origin_pattern, replace_format):
    record_json = read_json('file_rename.json')
    path_dict = record_json.get(root_path, {})
    o_dict = path_dict.get(origin_pattern, {})
    r_dict = o_dict.get(replace_format, {})
    if not r_dict:
        raise Exception('没有对应的历史记录, 无法回退')
    for o_path in r_dict:
        shutil.move(r_dict[o_path], o_path)
    o_dict.pop(r_dict)
    if not o_dict:
        path_dict.pop(origin_pattern)
    else:
        path_dict.update({origin_pattern: o_dict})
    if not path_dict:
        record_json.pop(root_path)
    else:
        record_json.update({root_path: path_dict})
    write_to_json('file_rename.json', record_json)
