import os
import re

from model.FileInfoModel import FileInfo

search_by_key = 'search_by_key'
search_by_spent = 'search_by_spent'
search_by_same_spent = 'search_by_same_spent'
search_by_same_size = 'search_by_same_size'


def file_search(root_path, opt, text):
    result_list = []
    if opt == search_by_spent:
        min_t, max_t = text.split('-')
        min_t = min_t.strip()
        max_t = max_t.strip()
        min_spent_list = min_t.split(':')
        min_spent_list = [int(i) for i in min_spent_list]
        max_spent_list = max_t.split(':')
        max_spent_list = [int(i) for i in max_spent_list]
        min_spent = 0
        while min_spent_list:
            min_spent += min_spent_list.pop(0)
            if min_spent_list:
                min_spent *= 60
        max_spent = 0
        while max_spent_list:
            max_spent += max_spent_list.pop(0)
            if max_spent_list:
                max_spent *= 60
        text = None

    for root, dirs, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(root, file.strip('/\\'))
            file_obj = FileInfo(file_path)
            if not os.path.isfile(file_path):
                continue
            elif text and not re.match(text, file):
                continue
            elif opt in [search_by_spent, search_by_same_spent] and not file_obj.is_video():
                continue

            file_obj.get_file_info()
            if opt == search_by_spent and (file_obj.duration < min_spent or file_obj.duration > max_spent):
                continue
            result_list.append(file_obj)

    return result_list
