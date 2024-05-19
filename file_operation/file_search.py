import os
import re
import cv2

from common.utils import is_video
search_by_key = 'search_by_key'
search_by_spent = 'search_by_spent'
search_by_same_spent = 'search_by_same_spent'
search_by_same_size = 'search_by_same_size'


def file_search(root_path, opt, text):
	result_list = []
	result_file_dict = {}
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
	for root, dirs, files in os.walk(root_path):
		for file in files:
			file_path = os.path.join(root, file)
			if not os.path.isfile(file_path):
				continue
			if opt == search_by_key and not re.match(text, file):
				continue
			if opt in [search_by_same_spent, search_by_same_size] and text and not re.match(text, file):
				continue
			if opt == search_by_key:
				result_list.append(file_path)
			if opt in [search_by_spent, search_by_same_spent]:
				if not is_video(file):
					continue
				cap = cv2.VideoCapture(file_path)
				if cap.isOpened():
					rate = cap.get(cv2.CAP_PROP_FPS)
					frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
					duration = int(frame_num / rate)
					cap.release()
				else:
					cap.release()
					continue
				if opt == search_by_spent:
					if duration > min_spent and duration < max_spent:
						result_list.append(file_path)
				else:
					spent_list = result_file_dict.get(duration, [])
					spent_list.append(file_path)
					result_file_dict[duration] = spent_list
			if opt == search_by_same_size:
				file_size = os.path.getsize(file_path)
				size_list = result_file_dict.get(file_size, [])
				size_list.append(file_path)
				result_file_dict[file_size] = size_list
	if result_list:
		return result_list
	return result_file_dict
