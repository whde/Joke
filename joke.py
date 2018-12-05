#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import importlib
from bs4 import BeautifulSoup
from urllib.parse import quote
from flask import json
import urllib3
import string

root_folder = 'JOKE/'
root_url = 'http://www.jokeji.cn/hot.asp?action=brow'

# 获取排行榜URL页下面的笑话list数据
def getmeichannel(url):
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    http = urllib3.PoolManager()
    web_data = http.request('GET', url, headers=headers).data
    soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    channel = []
    tables = soup.findAll(height='30')
    for table in tables:
        try:
            for tr in table.findAll('tr'):
                channel.append(tr)
                pass
        except Exception as e:
            print('Error:', e)
            pass
    return channel


# 获取排行榜的页数
def getpages(url):
    print(url)
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    http = urllib3.PoolManager()
    web_data = http.request('GET', url, headers=headers).data
    # web_data = requests.get(url, headers=headers)
    # web_data.encoding = 'gb2312'
    soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    print(web_data)
    # 找总页数
    span = soup.find(class_='main_title')
    tds = span.findAll('td')
    td = tds[len(tds)-2]
    pages = td.select('a')[0].get('href').replace('hot.asp?action=brow&me_page=', '')
    print(pages)
    return pages


# 爬取详情页数据
def detail(url):
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    http = urllib3.PoolManager()
    r = http.request('GET', url, headers=headers)
    web_data = r.data
    soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    # 查找详情页数据
    font = soup.find(attrs={'id': 'text110'})
    try:
        return font.get_text()
        pass
    except Exception as e:
        print(str(e))
        return ''
        pass


# 爬取每页下面的内容
def page(url):
    # 获取每页下面的笑话list
    channel_list = getmeichannel(url)
    list1 = []
    for tr in channel_list:
        dict1 = {}
        a = tr.find(class_='main_14')
        herf = 'http://www.jokeji.cn'+a.get('href')
        title = a.get_text()
        print(str(herf)+' --- '+str(title))
        dict1['herf'] = herf
        dict1['title'] = title
        dict1['date'] = tr.find(class_='date').get_text().replace('\r\n          ', '')
        # 获取当前笑话的详情，去详情页爬取数据
        dict1['detail'] = detail(herf)
        list1.append(dict1)
    return list1


# 开始爬取数据
def spider(url):
    list1 = []
    i = 1
    # 去获取排行榜的页数
    pages = getpages(url)
    while i <= int(pages):
        # 拼接每一页的URL地址
        pageurl = 'http://www.jokeji.cn/hot.asp?action=brow&me_page='+str(i)
        print(pageurl)
        # 获取每页下面的内容
        list1 = list1+page(pageurl)
        i = i+1
        pass
    else:
        print('大于页数')

    # 将list存储到data.json中
    try:
        filename = root_folder + 'data.json'
        with open(filename, "wb") as f:
            stri = json.dumps(list1, encoding='UTF-8', ensure_ascii=False)
            print(stri)
            f.write(stri)
        pass
    except Exception as e:
        print('Error:', e)
        pass
    pass


# 程序入口
if __name__ == "__main__":
    # 创建文件夹，最后存数据到这个文件夹下面
    importlib.reload(sys)
    if os.path.isdir(root_folder):
        pass
    else:
        os.mkdir(root_folder)
    # 开始爬取数据
    spider(root_url)
    print('**** spider ****')
