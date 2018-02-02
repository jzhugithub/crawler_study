# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs
import json
import re
import os
import pandas
import requests
import xlrd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from zhejiangzzhz_config import *
import xlwt
from xlutils.copy import copy
from  multiprocessing import Pool

# browser = webdriver.Chrome()
# browser.set_window_size(960, 640)
browser = webdriver.PhantomJS(service_args=SEVERVICE_ARGS)
wait = WebDriverWait(browser, 5)


def get_sub_page_ids(page_num):
    try:
        print('---page {} begin---'.format(page_num))
        # 打开网站
        browser.get("http://land.zzhz.zjol.com.cn/land/?&currpage={}".format(page_num))
        # 等待页面加载
        main_wait = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        '#wrapper > div.content.mt10.mb10.clear > div.maincontent.w650.fl > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > h3 > font')))

        # 获取网页源代码
        main_source = browser.page_source
        main_doc = pq(main_source)
        main_text = str(main_doc('#wrapper .content .maincontent .list_sub'))
        # print(main_text)

        # 获取地块页面id
        sub_ids = re.compile(r'/land/(\d+?)\.html').findall(main_text)
        with open(SUB_PAGE_IDS_FILE, 'a') as f:
            for sub_id in sub_ids:
                f.write(sub_id + '\n')
        print('---page {} end---'.format(page_num))
    except TimeoutException:
        print('get page {} error, try again'.format(page_num))
        get_sub_page_ids(page_num)


def get_sub_pages_ids():
    try:
        # 删除原ids.txt
        try:
            os.remove(SUB_PAGE_IDS_FILE)
        except:
            pass
        # 获取ids
        for i in range(1, 332, 1):
            get_sub_page_ids(i)
    except Exception:
        print('get_sub_page_ids error')


def get_sub_page(param):
    count = param[0]
    page_id = param[1]

    print('sub page count {} pageid {} start'.format(count, page_id))
    try:
        browser.get("http://land.zzhz.zjol.com.cn/land/{}.html".format(page_id))
        sub_wait = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div.bt3')))
        table = browser.find_element_by_css_selector('body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3)')
        land = []
        # count
        land.append((u'count', count))
        # page id
        land.append((u'page_id', page_id))
        # 名称
        land.append((u'地块', table.find_element_by_class_name('bt3').text))
        # 时间
        times = table.find_element_by_class_name('btn8').text
        time1 = re.compile(u'出让时间：(\d{4}-\d{2}-\d{2})', re.S).findall(times)
        time2 = re.compile(u'公告时间：(\d{4}-\d{2}-\d{2})', re.S).findall(times)

        try:
            a = time1[0]
            land.append((u'出让时间', time1[0]))
        except:
            land.append((u'出让时间', u''))
        try:
            a = time2[0]
            land.append((u'公告时间', time2[0]))
        except:
            land.append((u'公告时间', u''))

        # 出让面积（㎡）
        land.append((u'出让面积（㎡）', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(1) > td:nth-child(2)').text))
        # 容积率
        land.append((u'容积率', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(1) > td:nth-child(4)').text))
        # 成交价（万元）
        land.append((u'成交价（万元）', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(1) > td:nth-child(6)').text))
        # 用地性质
        land.append((u'用地性质', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(2)').text))
        # 商业占比
        land.append((u'商业占比', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(4)').text))
        # 成交楼面价（元/㎡）
        land.append((u'成交楼面价（元/㎡）', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(6)').text))
        # 起价（万元）
        land.append((u'起价（万元）', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(3) > td:nth-child(2)').text))
        # 配保（㎡）
        land.append((u'配保（㎡）', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(3) > td:nth-child(4)').text))
        # 溢价率
        land.append((u'溢价率', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(3) > td:nth-child(6)').text))
        # ≤90㎡户型占比
        land.append((u'≤90㎡户型占比', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(4) > td:nth-child(2)').text))
        # 竞得单位
        land.append((u'竞得单位', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(4) > td:nth-child(4)').text))
        # 地块四至
        land.append((u'地块四至', table.find_element_by_css_selector(
            'body > div:nth-child(5) > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > table > tbody > tr:nth-child(5) > td:nth-child(2)').text))

        # 坐标
        doc = pq(browser.page_source)
        loc_text = doc('body > div:nth-child(5) > div:nth-child(2) > script').text()
        pos_xy = re.compile("var px = '(.*?)'; var py = '(.*?)'; var bSize").search(loc_text)
        land.append((u'坐标px', pos_xy.group(1)))
        land.append((u'坐标py', pos_xy.group(2)))

        # 写数据
        with codecs.open(TXT_NAME, 'a', 'utf-8') as f:
            f.write(json.dumps(land, ensure_ascii=False) + '\n')
            f.close()

        # if count == 1:
        #     workbook = xlwt.Workbook(encoding='utf-8')
        #     worksheet = workbook.add_sheet('Sheet1')
        #     for i, key_valve in enumerate(land):
        #         worksheet.write(0, i, key_valve[0])
        #         worksheet.write(1, i, key_valve[1])
        #     workbook.save(EXCLE_NAME)
        # else:
        #     workbook = xlrd.open_workbook(EXCLE_NAME)
        #     workbook_new = copy(workbook)
        #     worksheet_new = workbook_new.get_sheet(0)
        #     for i, key_valve in enumerate(land):
        #         worksheet_new.write(count, i, key_valve[1])
        #     workbook_new.save(EXCLE_NAME)

        # 周边
        perimeter_html = doc('body > div:nth-child(5) > div:nth-child(5) > div.bt4.weiruan').html()
        has_table = True
        try:
            pandas.read_html(perimeter_html)
        except:
            has_table = False
        if has_table:
            with codecs.open(
                    os.path.join(RESULT_DIR, 'count_{}_pageid_{}html.txt'.format(count, page_id)),
                    'w', 'utf-8') as f:
                f.write(json.dumps(perimeter_html, ensure_ascii=False))

        print('sub page count {} pageid {} end'.format(count, page_id))
    except TimeoutException:
        print('sub page count {} pageid {} timeout'.format(count, page_id))
        # get_sub_page(count, page_id)

def get_sub_page_zhoubian(count, page_id):
    print('sub page zhoubian count {} pageid {} start'.format(count, page_id))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    response = requests.get("http://land.zzhz.zjol.com.cn/land/{}.html".format(page_id), headers=headers)
    response.encoding = 'gbk'
    pagetext = response.text
    pattern = re.compile(u'周边项目价格参考.*?src=\"(.*?)\"',re.S)
    if re.search(pattern, pagetext):
        image_url = u'http://land.zzhz.zjol.com.cn' + re.findall(pattern, pagetext)[0]
        print('get image: {}'.format(image_url))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        }
        img_response = requests.get(image_url,headers=headers)
        with open(os.path.join(RESULT_DIR,'count_{}_pageid_{}.jpg'.format(count,page_id)), 'wb') as f:
            f.write(img_response.content)


def txt2excel():
    for root, dirs, files in os.walk(RESULT_DIR):
        for file in files:
            if file[-4:]=='.txt':
                print(file)
                with open(os.path.join(RESULT_DIR, file), 'r') as f:
                    df = pandas.read_html(f.read())
                    bb = pandas.ExcelWriter(os.path.join(RESULT_DIR, file)[:-8] + '.xlsx')
                    df[0].to_excel(bb)
                    bb.close()


def main(process_num):
    try:
        # get_sub_pages_ids()

        # get_sub_page(1, 10925)
        # get_sub_page(2, 14251)
        # get_sub_page(3, 14419)
        # get_sub_page(4, 14033)

        idlist = []
        with open(SUB_PAGE_IDS_FILE, 'r') as f:
            for id in f.readlines():
                idlist.append(int(id))
        pool = Pool()
        for i in range(BEGIN_COUNT, len(idlist) + 1, process_num):
            pool.map(get_sub_page, [(t, idlist[t-1]) for t in range(i, i + process_num, 1)])
            # pool.map(get_sub_page_zhoubian, [(t, idlist[t - 1]) for t in range(i, i + process_num, 1)])
    finally:
        browser.close()
    txt2excel()


if __name__ == '__main__':
    main(PROCESS_NUM)
