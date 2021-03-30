#-*- coding:utf-8 -*-
import traceback
from bs4 import BeautifulSoup
import threading, time, requests, os, urllib3
import json
import sys
import urllib.request
requests.packages.urllib3.disable_warnings()

headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
    } 

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, url, dir, filename):
        threading.Thread.__init__(self)
        self.threadID = filename
        self.url = url
        self.dir = dir
        self.filename=filename
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        download_pic(self.url,self.dir,self.filename)
def download_pic(url,dir,filename):
    req=requests.get(url=url,headers=headers)
    file = dir+filename
    if req.status_code==200:
        with open(str(file),'wb') as f:
            f.write(req.content)
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        d = os.makedirs(path)
    return path
	
def get_urls(num):
        page_url = all_url[num-1]
        print(page_url)
        soup = creat_soup(page_url)
        article_url=[a['href'] for a in soup.find_all('a', href=True)]
        return article_url			
def creat_soup( url):
    '''
    该函数返回一个url的soup对象
    :param url:一个页面的链接
    '''
    # 获取网页，得到一个response对象
    s = requests.session()
    try:
        response = s.get(url, headers=headers,   timeout=30)
    except requests.exceptions.RequestException as e:
        print(e) 
    response.encoding = 'UTF-8' 
    return BeautifulSoup(response.text, 'html.parser')
		
try:
    all_url = ['https://cos.cossj.com/Cosplay1.html','https://cos.cossj.com/Cosplay2.html','https://cos.cossj.com/Cosplay3.html']
    num = input("选择下载:\n1.动漫游戏\n2.古风制服\n3.日本和风\n")
    urls = get_urls(int(num)) 
    for url in urls:
        url='https://cos.cossj.com/'+url
        threads=[]
        soup = creat_soup(url)
        p = soup.findAll('li')
        title = soup.find('title').text
        page = {'title':title, 'imgs':[]}
        for i in p:
            page['imgs'].append(i['data-src'].replace("https://images.weserv.nl/?url=https://pic.24cos.com", "https://pic.lovecos.net"))

        imgPath = os.path.abspath('./')+'/cos'+num+'/'+title+'/'
        imgs=page['imgs']
        if os.path.exists(imgPath) and (len(os.listdir(imgPath)) == len(imgs) ):
            print('Passed：'+title+'已经下载！')
        else:
            folder = mkdir(imgPath)
            count = 0
            print('开始下载:'+title+',共计图片:'+str(len(imgs)) +'张')
            for index, img in enumerate(imgs):
                filename = str(index+1)+'.jpg'
                thread=myThread(img,imgPath,filename)
                thread.start()
                threads.append(thread)
                count +=1
                while True:
                    if(len(threading.enumerate()) < 4):
                        break
            for t in threads:
                t.join()
            print('Finisded! '+title+'结束,共计下载'+str(count)+'张图片')
except Exception as e:
    print ('Exception: ', e)
    print('程序错误，退出')
    pass