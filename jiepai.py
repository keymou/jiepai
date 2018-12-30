'''今日头条街拍'''
import re
import json
import os
import requests
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

def  get_page(offset):
    """获取页面信息"""
    params ={
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    """获取images url链接"""
    print('*'*70)
    if json.get('data'):
        for item in json.get('data'):
            try:
                title = item.get('title')
                images = item.get('image_list')
                for image in images:
                    yield {
                        'image': 'http:'+ image.get('url').replace('list', 'large'),
                        'title': title
                    }
            except:
                continue


def save_image(item):
    """保存图片"""
    # 替换掉title字符串中的特殊字符
    title = re.sub(r'[\/\\\*\?\|\<\>\:\"]', '', item.get('title'))
    if not os.path.exists(title):
        os.mkdir(title)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(title, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as file_obj:
                    file_obj.write(response.content)
            else:
                print('已经下载过', file_path)
    except requests.ConnectionError:
        print('下载失败')

def main(offset):
    """主函数"""
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)

GROUP_START = 1
GROUP_END = 20

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END+1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
