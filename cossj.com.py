#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import threading, time, requests, os, urllib3
import json
import sys
import urllib.request
requests.packages.urllib3.disable_warnings()

all_url = ['https://cos.cossj.com/Cosplay1.html','https://cos.cossj.com/Cosplay2.html','https://cos.cossj.com/Cosplay3.html']

headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
    } 

class StoppableThread(threading.Thread):
    """封装stop和stoped的thread """

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        d = os.makedirs(path)
    return path

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

def get_urls(num):
    #for page_url in all_url:
        page_url = all_url[num-1]
        print(page_url)
        soup = creat_soup(page_url)
        #get=requests.get(url=page_url,headers=headers)
        #article_url=soup.find_all('a').get('href')
        article_url=[a['href'] for a in soup.find_all('a', href=True)]
        return article_url


def get_single_imgs(url):
    soup = creat_soup(url)
    p = soup.findAll('li')
    title = soup.find('title').text
    page = {'title':title, 'imgs':[]}
    for i in p:
        page['imgs'].append(i['data-src'].replace("https://images.weserv.nl/?url=https://pic.24cos.com", "https://pic.lovecos.net"))
    return page


semaphore = threading.Semaphore(3)
def saveImages(num, title, imgs):
    imgPath = os.path.abspath('./')+'/cos'+num+'/'+title+'/'
#    t = os.listdir(imgPath)
    if os.path.exists(imgPath) and (len(os.listdir(imgPath)) == len(imgs) ):
        print('Passed：'+title+'已经下载！')
        return False
    folder = mkdir(imgPath)
    count = 0
    print('开始下载:'+title+',共计图片:'+str(len(imgs)) +'张')
    num = 5
    with semaphore:
        while num:
            for index, img in enumerate(imgs):
                try:
                    html = requests.get(img, headers=headers, timeout=30)
                    filename = folder+'/'+str(index+1)+'.jpg'
                    with open(filename, 'wb') as handle:
                        handle.write(html.content)
                    count +=1
                except Exception as e:
                    print(e)
                    continue
            print('Finisded! '+title+'结束,共计下载'+str(count)+'张图片')

def downTask():
    num = input("选择下载:\n1.动漫游戏\n2.古风制服\n3.日本和风\n")
    urls = get_urls(int(num)) 
    for url in urls:
        thread_list = []
        url='https://cos.cossj.com/'+url
        signle = get_single_imgs(url)
        try:
            th = StoppableThread(target=saveImages, args=(num,signle['title'],signle['imgs'])) 
            th.start() 
            thread_list.append(th)
        except (KeyboardInterrupt, SystemExit):
            th.stop()
            sys.exit() 
    for x in thread_list:
        x.join()
       


if __name__=="__main__":
    downTask()