import os
import shutil
import re

from IPython.lib.deepreload import original_import

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


def replace_by_re(pattern_same_parts, origin_str, origin_pattern, target_pattern, replace_full_name=False, is_file=False):
    o_str = re.search(origin_pattern, origin_str).group()
    o_str_back_up = o_str
    for same_part in pattern_same_parts:
        matched_str = re.search(same_part, o_str).group()
        target_pattern = target_pattern.replace(same_part, matched_str, 1)
        o_str = o_str.split(matched_str, 1)[-1]
    if replace_full_name:
        if is_file:
            suffix = origin_str.split('.')[-1]
            new_name = '{}.{}'.format(target_pattern, suffix)
        else:
            new_name = target_pattern
    else:
        new_name = origin_str.replace(o_str_back_up, target_pattern)
    return new_name


def file_rename(root_path, origin_pattern, replace_format, replace_dir_name=False, replace_file_name=False, replace_full_name=False):
    file_name_replace = {}
    dir_name_replace = {}
    for root, dirs, files in os.walk(root_path):
        if replace_file_name:
            for file in files:
                origin_path = os.path.join(root, file.strip('/\\'))
                if not os.path.isfile(origin_path) or not re.search(origin_pattern, file):
                    continue
                file_name_list = file_name_replace.get(root, [])
                file_name_list.append(file)
                file_name_replace[root] = file_name_list
        if replace_dir_name:
            for dir in dirs:
                origin_path = os.path.join(root, dir.strip('/\\'))
                if not os.path.isdir(origin_path) or not re.search(origin_pattern, dir):
                    continue
                dir_name_list = dir_name_replace.get(root, [])
                dir_name_list.append(dir)
                dir_name_replace[root] = dir_name_list

    pattern_same_parts = get_same_parts(origin_pattern, replace_format)

    replace_mapping = {}
    for replace_dict in [file_name_replace, dir_name_replace]:
        for item_root in replace_dict:
            is_file = False
            if replace_dict is file_name_replace:
                is_file = True
            items = replace_dict[item_root]
            for item in items:
                target_name = replace_by_re(pattern_same_parts, item, origin_pattern, replace_format, replace_full_name, is_file)
                target_path = os.path.join(item_root, target_name.strip('/\\'))
                suffix = 1
                while os.path.exists(target_path) and target_path != os.path.join(item_root, item.strip('/\\')):
                    name, ext = os.path.splitext(target_name)
                    target_name = '{}-{}{}'.format(name, suffix, ext)
                    suffix += 1
                    target_path = os.path.join(item_root, target_name.strip('/\\'))
                replace_mapping[os.path.join(item_root, item.strip('/\\'))] = target_path

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
            o_path = os.path.join(root, file.strip('/\\'))
            if not os.path.isfile(o_path) or file.split('.')[-1] != origin_pattern:
                continue
            new_name = file.replace(origin_pattern, replace_format)
            t_path = os.path.join(root, new_name.strip('/\\'))
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


def file_name_to_lower_or_upper(root_path, opt):
    is_to_upper = opt == 'main_file_name_to_upper'
    file_rename_path_dict = {}
    dir_rename_path_dict = {}
    for root, dirs, files in os.walk(root_path):
        for file in files:
            t_path = os.path.join(root, file)
            if not os.path.isfile(t_path):
                continue
            if root not in file_rename_path_dict:
                file_rename_path_dict[root] = []
            file_rename_path_dict[root].append(file)
        for dir in dirs:
            t_path = os.path.join(root, dir)
            if not os.path.isdir(t_path):
                continue
            if root not in dir_rename_path_dict:
                dir_rename_path_dict[root] = []
            dir_rename_path_dict[root].append(dir)
    rename_dict = {}
    for item_dict in [file_rename_path_dict, dir_rename_path_dict]:
        for root in item_dict:
            rename_list = item_dict[root]
            for rename_item in rename_list:
                origin_path = os.path.join(root, rename_item)
                if os.path.isfile(origin_path):
                    path_without_ext, ext = os.path.splitext(rename_item)
                    target_path = os.path.join(root, '{}{}'.format(path_without_ext.upper() if is_to_upper else path_without_ext.lower(), ext))
                else:
                    target_path = os.path.join(root, rename_item.upper() if is_to_upper else rename_item.lower())
                rename_dict[origin_path] = target_path
    print(rename_dict)
    rename_dict = dict(sorted(rename_dict.items(), key=lambda i: i[0], reverse=True))
    for origin_path in rename_dict:
        target_path = rename_dict[origin_path]
        start_idx = 1
        same_dir_ls = os.listdir(os.path.dirname(target_path))
        parent_path, target_name = os.path.split(target_path)
        while target_name in same_dir_ls and origin_path != target_path:
            path_without_ext, ext = os.path.splitext(target_name)
            target_name = '{}-{}{}'.format(path_without_ext, start_idx, ext)
            target_path = os.path.join(parent_path, target_name)
            start_idx += 1
        rename_dict[origin_path] = target_path
        shutil.move(origin_path, target_path)
    history_json = {
        root_path: {
            'lower' if is_to_upper else 'upper': rename_dict
        }
    }
    write_to_json('file_rename.json', history_json)


def rename_roll_back(root_path, opt, origin_pattern=None, replace_format=None):
    record_json = read_json('file_rename.json')
    path_dict = record_json.get(root_path, {})
    if opt in ['main_file_name_to_upper', 'main_file_name_to_lower']:
        option = 'lower' if opt == 'main_file_name_to_lower' else 'upper'
        rename_opt_dict = record_json[root_path]
        rename_dict = rename_opt_dict[option]
        for o_path in rename_dict:
            shutil.move(rename_dict[o_path], o_path)
        rename_opt_dict.pop(option)
        if not rename_opt_dict:
            record_json.pop(root_path)
        else:
            record_json[root_path] = rename_opt_dict
        write_to_json('file_rename.json', record_json)
    else:
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
