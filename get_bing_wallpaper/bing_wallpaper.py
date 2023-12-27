
import os
import re
import time
import yaml
import easygui
import requests
import json
import wget
from bs4 import BeautifulSoup
from lxml import etree


BING_WEBSITE="https://cn.bing.com/?form=HPEDGE"
HEAD_WEBSITE="https://cn.bing.com"

class Spider():
    def __init__(self, url):
        self.url = url

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 Edg/84.0.522.63'
        }

    def get_data(self):
        # r = requests.get(self.url, headers=self.headers, cookies=self.cookies)
        r = requests.get(self.url, headers=self.headers)
        if r.status_code != 200:
            return False
        r.encoding = r.apparent_encoding
        self.html = r.text
        return True

    def get_lcd(self):
        bb_test = requests.get(self.url, headers=self.headers, cookies=self.cookies)
        dict_temp = bb_test.json()
        ret = dict_temp['lcdBottomTable']
        return ret

    def BeautifulSoup_find(self):
        '''用BeautifulSoup解析'''
        start = time.time()
        soup = BeautifulSoup(self.html, 'lxml')  # 转换为BeautifulSoup的解析对象()里第二个参数为解析方式

        div_str = soup.find_all('td', class_='hp_hd')
        print(type(div_str))
        temp_str = str(div_str)
        temp_len = len('data-ultra-definition-src=\"')
        begin = int(temp_str.find('data-ultra-definition-src=\"'))
        end = int(temp_str.find('\" id=\"bgImgProgLoad\"'))
        print(temp_str[begin+temp_len:end])
        bg_url = temp_str[begin+temp_len:end];

        # div_str = soup.find_all('a', class_='sc_light')
        # print(type(div_str))
        # print(div_str)
        # bg_url = "sss"
        return bg_url

    def message_box(self, title1, msg1):
        # 桌面弹出消息框
        easygui.msgbox(title=title1, msg=msg1)

if __name__ == '__main__':
    print("*** start at %s ***" % (time.ctime(time.time())))
    os.chdir('C:\\Users\\670252481\\Documents\\Python\\download_bing_wallpaper')
    count = 1

    url = BING_WEBSITE
    spider = Spider(url)
    ret = spider.get_data()
    tmp_url=spider.BeautifulSoup_find()
    print("tmp_url:",HEAD_WEBSITE+tmp_url)
    os.chdir('C:\\Users\\670252481\\Pictures\\wallpicture')
    filename = time.strftime("%Y%m%d", time.localtime())+'.jpg'
    wget.download(HEAD_WEBSITE+tmp_url, out=filename)

    print("*** end at %s ***" % (time.ctime(time.time())))
