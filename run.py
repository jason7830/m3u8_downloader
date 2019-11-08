import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import m3u8
import queue
from MultiRequests import Requester, request
from Downloader import Downloader
import re
session = requests.session()
headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}

if __name__ == '__main__':
    url = input("Input: ")
    r = session.get(url,headers=headers)
    soup = bs(r.text,'html.parser')
    m3u8_link = soup.find(id='video').find('source').get('src')
    title = soup.find('h1','article-watch__title').text
    title = re.sub('[/\\:?\*"<>|]','',title)[:200]
    a = m3u8_link
    d = Downloader(a,title+'.mp4',threads=10)
    d.download()
    d.concatSegs(True)