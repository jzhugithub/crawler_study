# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs
import json
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from taobao_config import *
import time
import os

# 用Chrome
# browser = webdriver.Chrome()
browser = webdriver.PhantomJS(service_args=SEVERVICE_ARGS)
browser.set_window_size(960, 640)

# 设置等待时间
wait = WebDriverWait(browser, 10)


def search():
    try:
        print('---page 1 begin---')
        # 打开网站
        browser.get("http://www.taobao.com")
        # 指定并等待元素出现
        # EC.presence_of_element_located 等待直到元素出现
        # EC.element_to_be_clickable 等待直到元素可点击
        # '#q'Chrome检查元素，Copy selector得到的值（By.CSS_SELECTOR就是指根据selector进行选择）
        # 选择搜索框
        input = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        # 等待搜素按钮
        submit = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        # 输入搜索字符
        input.send_keys(KEY_WORDS)
        # 点击搜索按钮
        submit.click()
        time.sleep(1)
        # 读取页面信息
        get_products()
        # 总页数元素
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        print('---page 1 success---\n')
        # 返回元素文本信息
        return total.text
    except TimeoutException:
        print('search timeout')
        search()


def next_page(page_number):
    try:
        print('---page {} begin---'.format(page_number))
        # 选择搜索框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 等待搜素按钮
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        # 清空文本内容
        input.clear()
        # 输入字符
        input.send_keys(page_number)
        # 点击
        submit.click()
        # 判断翻页是否成功
        # EC.text_to_be_present_in_element 是否有指定的文本存在于元素中
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
        # 读取页面信息
        get_products()
        print('---page {} success---\n'.format(page_number))
    except TimeoutException:
        print('next page timeout')
        next_page(page_number)


def get_products():
    try:
        # 等待项目加载
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        # 获取网页源代码
        html = browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('src'),
                'price': item.find('.price').text()[2:],
                'deal': item.find('.deal-cnt').text()[:-3],
                'title': item.find('.title').text(),
                'shop': item.find('.shop').text(),
                '.location': item.find('.location').text()
            }
            # 写入文件
            with codecs.open(OUTPUT_FILE_NAME, 'a', 'utf-8') as f:
                f.write(json.dumps(product, ensure_ascii=False) + '\n')
                f.close()
        # with codecs.open('taobao.txt', 'a', 'utf-8') as f:
        #     f.write('\n\n')
        #     f.close()
    except TimeoutException:
        print('get_products timeout')


def main():
    try:
        os.remove(OUTPUT_FILE_NAME)
    except:
        pass

    try:
        # 抓取第一页
        total = search()
        # 获取总页数
        total = int(re.compile(r'.*?(\d+).*?').search(total).group(1))
        for i in range(2, total, 1):
            # 抓取下一页
            next_page(i)
    except Exception:
        print('unknown exception')
    finally:
        # 关闭浏览器
        browser.close()


if __name__ == '__main__':
    main()
