import os
import requests

start_idx = 1855
url_format = 'https://cdn-mso8.kiseouhgf.info/hlsredirect_m3u8/2lh8dtY192DeR81-9GnMlQ/1723076396/hls/2A5oaWZZqei/normal.mp4/{}?ckskip=1&e=1722115505&st=c4HbIse1DbUqajhWFUgqWQ&ckskiptoken=2639b6c5c310c18123d41cafffe06311'
m3u8_filename = 'index.m3u8'
anti_keyword = '#'
scrapy_file_name = 'ONED-933'
base_dir = '/Users/yangtiejun/Downloads/'
file_dir = os.path.join(base_dir, scrapy_file_name)


def get_m3u8_content():
    result = requests.get(url_format.format(m3u8_filename))
    if result.status_code != 200:
        print('Get m3u8 content error!')
        return None
    m3u8_content = list(filter(lambda i: anti_keyword not in i and len(i) != 0, result.text.split('\n')))
    result_dict = {}
    for file_name in m3u8_content:
        result_dict[m3u8_content.index(file_name)] = file_name
    return result_dict


def merge_ts_files():
    files = sorted(os.listdir(file_dir))
    target_file = os.path.join(base_dir, '{}.ts'.format(scrapy_file_name))
    with open(target_file, 'wb') as target_f:
        for file in files:
            ts_file_path = os.path.join(file_dir, file)
            with open(ts_file_path, 'rb') as origin_f:
                target_f.write(origin_f.read())


def scrapy_video():
    error_file_list = []
    m3u8_dict = get_m3u8_content()

    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)

    for idx in range(start_idx):
        m3u8_dict.pop(idx)

    for idx in m3u8_dict:
        file = m3u8_dict[idx]
        if not file.startswith('http'):
            file_url = url_format.format(file)
        else:
            file_url = file
        result = requests.get(url=file_url, timeout=5)
        if not result or result.status_code != 200:
            error_file_list.append(file)
            print(file_url)
            continue
        file_name = '{:0>5}.ts'.format(idx)
        ts_file_path = os.path.join(file_dir, file_name)
        with open(ts_file_path, 'wb') as f:
            f.write(result.content)
        print('{} scrapy finished.'.format(file_name))

    if not error_file_list:
        merge_ts_files()
    else:
        print(error_file_list)


if __name__ == '__main__':
    scrapy_video()