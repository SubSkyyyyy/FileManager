import os
import sys
import subprocess
import cv2
import hashlib
from common.config import PROJECT_ROOT
from pywinauto import Application


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


def is_video(path):
    if os.path.splitext(path)[-1].lower().strip('.') not in ['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'mpeg', 'mpg',
                                                             'webm', 'rmvb', '3gp', 'ts', 'm4v']:
        return False
    return True


def is_img(path):
    if os.path.splitext(path)[-1].lower().strip('.') not in ['jpg', 'jpeg', 'png', 'git', 'bmp', 'tiff', 'webp', 'raw',
                                                             'svg', 'psd', 'heif', 'tif', 'heic']:
        return False
    return True


def convert_path_to_hash_str(path):
    return hashlib.sha256(path.encode()).hexdigest()


def generate_thumbnail(path):
    if is_img(path):
        return path
    if is_video(path):
        thumbnail_name = convert_path_to_hash_str(path)
        img_dir = os.path.join(PROJECT_ROOT, 'img')
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)
        thumbnail_path = os.path.join(img_dir, '{}.png'.format(thumbnail_name))
        if os.path.isfile(thumbnail_path):
            return thumbnail_path
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            cap.release()
            return None
        frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num / 2))
        success, frame = cap.read()
        if not success:
            cap.release()
            return None
        cv2.imwrite(thumbnail_path, frame)
        cap.release()
        return thumbnail_path
