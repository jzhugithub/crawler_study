# -*- coding:utf-8 -*-
import json
from hashlib import md5
import re
from urllib import urlencode
import os
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from multiprocessing import Pool


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3,
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    response = requests.get(url)
    try:
        return response.text
    except RequestException:
        print('请求索引页出错')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            url = item.get('article_url')
            if url:
                yield url


def get_page_detail(url):
    response = requests.get(url)
    try:
        return response.text
    except RequestException:
        print('请求详情页出错', url)
        return None


def parse_page_detial(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    image_pattern = re.compile(r'gallery\: JSON\.parse\(\"(.*?)\"\),', re.S)
    result = image_pattern.search(html).groups(1)[0]
    result = result.replace('\\\\', '\\').replace('\\', '')
    if result:
        data = json.loads(result)
        if data and u'sub_images' in data.keys():
            sub_images = data.get(u'sub_images')
            images = [item.get(u'url') for item in sub_images]
            for image in images:
                download_image(image)
            return {
                'title': title,
                'images': images,
                'url': url
            }


def download_image(url):
    print('正在下载：{}'.format(url))
    response = requests.get(url)
    try:
        save_image(response.content)
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content):
    dir_path = os.path.join(os.getcwd(), 'images')
    file_path = os.path.join(dir_path, '{0}.jpg'.format(md5(content).hexdigest()))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(param):
    offset = param[0]
    keyword = param[1]
    print(offset)
    print(keyword)
    html = get_page_index(offset, keyword)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            print parse_page_detial(html, url)


if __name__ == '__main__':
    page_num = 4
    keyword = '街拍'
    processes = 3


    offsets = range(0, 20 * page_num, 20)
    pool = Pool(processes=processes)
    pool.map(main, [[i, keyword] for i in offsets])
