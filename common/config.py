import os
CLOSE = '关闭'
ENTER = '确认'
ROLL_BACK = '回退'

RE_PATTERN = {
    '视频': r'.*\.(mp4|mov|avi|wmv|mkv|flv|webm|mpeg|mpg|MP4|MOV|AVI|WMV|MKV|FLV|WEBM|MPEG|MPG|TS|ts)',
    '图片': r'.*\.(jpg|jpeg|png|JPG|JPEG|PNG|GIF|gif)'
}

HISTORY_FILE_PATH = r'history'

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

NORMAL_SIZE = 30
BIG_SIZE = 40
SMALL_SIZE = 20
