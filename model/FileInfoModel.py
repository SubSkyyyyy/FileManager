import os
import cv2
import hashlib
import shutil
from common.redis_cache import redis_client
from common.config import VIDEO_TYPE_LIST, IMG_TYPE_LIST, PROJECT_ROOT

class FileInfo:
	def __init__(self, file_path):
		self.path = file_path
		self.duration = None
		self.file_size = None
		self.thumbnail_path = None
		self.image_path = None
		if self.is_img():
			self.image_path = self.path

	def load_from_redis(self):
		try:
			info = redis_client.hgetall(self.path)
			if not info:
				return None
			info = {key.decode(): value.decode() for key, value in info.items()}
			self.file_size = int(info.get('file_size'))
			self.duration = int(info.get('duration')) if info.get('duration', '') != '' else None
			if not self.duration and self.is_video():
				self.get_file_duration()
				self.save_to_redis()
			return True
		except Exception as e:
			print(e)

	def save_to_redis(self):
		redis_client.hset(self.path, 'file_size', self.file_size or '')
		if self.is_video():
			redis_client.hset(self.path, 'duration', self.duration or '')

	def is_video(self):
		if os.path.splitext(self.path)[-1].lower().strip('.') not in VIDEO_TYPE_LIST:
			return False
		return True

	def is_img(self):
		if os.path.splitext(self.path)[-1].lower().strip('.') not in IMG_TYPE_LIST:
			return False
		return True

	def get_file_duration(self):
		if self.is_video() and self.duration is None:
			if not self.duration:
				cap = cv2.VideoCapture(self.path)
				if cap.isOpened():
					rate = cap.get(cv2.CAP_PROP_FPS)
					frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
					self.duration = int(frame_num / rate)
					cap.release()
				else:
					cap.release()
					self.duration = 0

	def get_file_size(self):
		if not self.file_size:
			self.file_size = os.path.getsize(self.path)

	def get_file_info(self):
		get_info_success = self.load_from_redis()
		if not get_info_success:
			self.get_file_duration()
			self.get_file_size()
			self.save_to_redis()

	@property
	def thumbnail(self):
		if self.thumbnail_path:
			return self.thumbnail_path
		screenshot_name = self.convert_path_to_hash_str()
		thumbnail_name = '{}-thumbnail'.format(screenshot_name)
		img_dir = os.path.join(PROJECT_ROOT, 'img')
		if not os.path.isdir(img_dir):
			os.makedirs(img_dir)
		screenshot_path = os.path.join(img_dir, '{}.bmp'.format(screenshot_name))
		thumbnail_path = os.path.join(img_dir, '{}.bmp'.format(thumbnail_name))
		if self.is_img():
			img_content = cv2.imread(self.path)
			thumbnail_content = cv2.resize(img_content,(img_content.shape[1] // 2, img_content.shape[0] // 2))
			cv2.imwrite(thumbnail_path, thumbnail_content)
			return self.image_path
		elif self.is_video():
			if os.path.isfile(screenshot_path) and os.path.isfile(thumbnail_path):
				self.image_path = screenshot_path
				self.thumbnail_path = thumbnail_path
				return self.thumbnail_path
			cap = cv2.VideoCapture(self.path)
			if not cap.isOpened():
				cap.release()
				return None
			frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
			cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num / 2))
			success, screenshot_content = cap.read()
			if not success:
				cap.release()
				return None
			thumbnail_content = cv2.resize(screenshot_content, (screenshot_content.shape[1] // 2, screenshot_content.shape[0] // 2))
			cv2.imwrite(screenshot_path, screenshot_content)
			cv2.imwrite(thumbnail_path, thumbnail_content)
			cap.release()
			self.image_path = screenshot_path
			self.thumbnail_path = thumbnail_path
			return self.thumbnail_path
		else:
			return None

	def convert_path_to_hash_str(self):
		return hashlib.sha256(self.path.encode()).hexdigest()

	def refactor(self, target_path):
		shutil.move(self.path, target_path)
		self.path = target_path

		screenshot_name = self.convert_path_to_hash_str()
		thumbnail_name = '{}-thumbnail'.format(screenshot_name)
		img_dir = os.path.join(PROJECT_ROOT, 'img')
		screenshot_path = os.path.join(img_dir, '{}.bmp'.format(screenshot_name))
		thumbnail_path = os.path.join(img_dir, '{}.bmp'.format(thumbnail_name))
		if not self.is_img() and self.image_path:
			shutil.move(self.image_path, screenshot_path)
			self.image_path = screenshot_path
		if self.thumbnail_path:
			shutil.move(self.thumbnail_path, thumbnail_path)
			self.thumbnail_path = thumbnail_path
