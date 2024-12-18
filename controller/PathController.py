import os
from pathlib import Path
from common.config import VIDEO_TYPE_LIST, IMG_TYPE_LIST, PROJECT_ROOT

class PathController:
    def __init__(self, path):
        self.path = path
        self.path_obj = Path(path)


    def is_video(self):
        if os.path.splitext(self.path)[-1].lower().strip('.') not in VIDEO_TYPE_LIST:
            return False
        return True

    def is_img(self):
        if os.path.splitext(self.path)[-1].lower().strip('.') not in IMG_TYPE_LIST:
            return False
        return True

    def is_dir(self):
        return self.path_obj.is_dir()

    def is_file(self):
        return self.path_obj.is_file()

    def move(self, target_path):
        target_path_main, ext = os.path.splitext(target_path)
        rename_count = 1
        while True:
            try:
                target_obj_path = Path(target_path)
                self.path_obj.rename(target_obj_path)
                self.path_obj = target_obj_path
                return True
            except FileExistsError:
                target_path = '{}-{}{}'.format(target_path_main, rename_count, ext)
                rename_count += 1
                continue

    def rename(self, new_name):
        new_name_main, ext = os.path.splitext(new_name)
        rename_count = 1
        while True:
            try:
                new_file_name_obj = self.path_obj.with_name(new_name)
                self.path_obj.rename(new_file_name_obj)
                self.path_obj = new_file_name_obj
                return True
            except FileExistsError:
                new_name = '{}-{}{}'.format(new_name_main, rename_count, ext)
                rename_count += 1
                continue


    def search(self, search_pattern):
        self.path_obj.rglob(search_pattern)