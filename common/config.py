import os
import sys

CLOSE = '关闭'
ENTER = '确认'
ROLL_BACK = '回退'

VIDEO_TYPE_LIST = ['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'mpeg', 'mpg', 'webm', 'rmvb', '3gp', 'ts', 'm4v']
IMG_TYPE_LIST = ['jpg', 'jpeg', 'png', 'git', 'bmp', 'tiff', 'webp', 'raw', 'svg', 'psd', 'heif', 'tif', 'heic']

RE_PATTERN = {
    '视频': r'.*\.(?i)({})'.format('|'.join(VIDEO_TYPE_LIST)),
    '图片': r'*\.(?i)({})'.format('|'.join(IMG_TYPE_LIST))
}

HISTORY_FILE_PATH = r'history'

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


NORMAL_SIZE = 30
BIG_SIZE = 40
SMALL_SIZE = 20
if sys.platform == 'win32':
    NORMAL_SIZE = 20
    BIG_SIZE = 30
    SMALL_SIZE = 10
