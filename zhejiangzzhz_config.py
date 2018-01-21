#-*- coding=utf-8 -*-
import os

SEVERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
SUB_PAGE_IDS_FILE = 'sub_ids.txt'
RESULT_DIR = 'zhejiang_zzhz'
EXCLE_NAME = os.path.join(RESULT_DIR, 'zhejiang_zzhz.xls')
BEGIN_COUNT = 1

# multiprocess
TXT_NAME = os.path.join(RESULT_DIR, 'zhejiang_zzhz.txt')
PROCESS_NUM = 3