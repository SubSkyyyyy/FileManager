import os
import sys
import subprocess
import hashlib


class CombineDict(dict):
    def update_each_level(self, data: dict):
        value_stack = [data]
        dict_stack = [self]
        while value_stack:
            d = value_stack.pop(-1)
            keys = d.keys()
            curr_dict = dict_stack.pop(-1)
            for key in keys:
                if key not in curr_dict or not curr_dict[key] or not isinstance(d[key], dict):
                    curr_dict[key] = d[key]
                else:
                    value_stack.append(d[key])
                    dict_stack.append(curr_dict[key])


def open_file_in_dir(path):
    if sys.platform == 'win32':
        subprocess.run(f'explorer /select, "{path}"')
    elif sys.platform == 'darwin':
        subprocess.run(["open", "-R", path])
        # subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])


def open_file_by_default_app(path):
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])

