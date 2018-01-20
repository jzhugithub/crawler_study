# -*- coding: utf-8 -*-
from __future__ import division
import requests
import re
import json
import codecs
from multiprocessing import Pool

# 获取页面文本信息
def get_one_page(url):
    response = requests.get(url)
    return response.text

def parse_one_page(html):
    # 编译匹配格式
    pattern = re.compile('board.*?(\d+?)</i>.*?"star">\n(.*?)</p>.*?"integer">(\d+?)\.</i>.*?"fraction">(\d+?)</i>', re.S)
    # 末尾不加re.S则在每行中进行匹配，加re.S则可以跨行匹配

    # 返回所有匹配结果
    items = re.findall(pattern, html)

    itemdict = {}
    for item in items:
        itemdict['index'] = item[0]
        itemdict['name'] = item[1].strip()[3:]
        itemdict['score'] = item[2] + '.' + item[3]
        yield itemdict


def write_to_file(content):
    with codecs.open('maoyan.txt', 'a', 'utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')
        f.close()

def main(offset):

    url = 'http://maoyan.com/board/4?offset={}'.format(offset)
    html = get_one_page(url)
    for dictitem in parse_one_page(html):
        print dictitem
        write_to_file(dictitem)

if __name__ == '__main__':
    # for i in range(0,100,10):
    #     main(i)
    #
    pool = Pool()
    pool.map(main, range(0,100,10))

    # map(main, range(0, 100, 10))