# -*- coding: UTF-8 -*-
#!/usr/bin/python

# create by zhonghanwen 2019/06/16

import requests
import json
import urllib
import sys
import os
import time

# 打印当前本地时间
def printCurrentTime():
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[Log]: %s"%(localtime))


def _progress(block_num, block_size, total_size):
    '''回调函数
       @block_num: 已经下载的数据块
       @block_size: 数据块的大小
       @total_size: 远程文件的大小
    '''
    percent = 100.0 * block_num * block_size / total_size
    _name = 'Downloading'
    if percent > 100:
        percent = 100
        _name = 'Download complete '
    
    sys.stdout.write('\r>> %s %.1f%% ' % (_name, percent))
    sys.stdout.flush()

def downloadSound(download_url, type, book_name):
    DATA_URL = download_url
    savePaht = os.getcwd() + "/" + type + "/" + book_name + "/"
    #print("save path %s" % (savePaht))
    mkdir(savePaht)
    filename = savePaht + DATA_URL.split('/')[-1]
    print(filename)
    if isSoundExist(filename) :
        print("[Log]: sound is exist skip.")
        return
    try :
        filepath, _ = urllib.urlretrieve( DATA_URL.encode('utf-8'), filename, _progress)
    except urllib.ContentTooShortError :
        print('[Log]: Network conditions is not good.Reloading.')
        time.sleep(5)
        filepath, _ = urllib.urlretrieve( DATA_URL.encode('utf-8'), filename, _progress)
    except :
        print('[Log]: Other exception.Reloading.')
        time.sleep(10)
        filepath, _ = urllib.urlretrieve( DATA_URL.encode('utf-8'), filename, _progress)
    finally :
        pass

def isSoundExist(path):
    path = path.strip()
    isExists = os.path.exists(path)
    return isExists

def mkdir(path):

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        #print ('创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print (' 目录已存在')
        return False

def searchBookInfo(book_id, keyword):
    try:
        s = requests.get("http://app.tingchina.com/search.asp?oauth_token=&keyword=%s" % (keyword))
        jm1 = json.loads(s.text)
        msg = jm1['msg']
        if msg == 'OK':
            data = jm1['data']
            count = len(data)
            if count > 0:
                for num in range(0, count):
                    _bookId = data[num]['bookID']
                    if book_id == _bookId:
                        bookType = data[num]['bookType']
                        return bookType
            else:
                print("[Log]: search count less than zero~")
                return -1
        else:
            print("[Log]: search info failure~")
            return -1
    except urllib.ContentTooShortError :
        print('[Log]: [SearchBook] Network conditions is not good.Reloading.')
        time.sleep(5)
        searchBookInfo(book_id, keyword)
    except :
        print('[Log]: [SearchBook] other except.Reloading.')
        time.sleep(10)
        searchBookInfo(book_id, keyword)
    finally:
        pass

def requestDownloadUrl(episodes, book_id, book_type, type_id, book_name) :
    try:
        #print(episodes)
        _r = requests.get('http://app.tingchina.com/play_cdn.asp?episodes=%s&bookID=%s&bookType=%s'%(episodes,book_id, book_type))
        #print(_r.text)
        jmReal = json.loads(_r.text)

        msg = jmReal['msg']
        if msg == 'OK':
            realUrl = jmReal['data']['url']
            #print("--> realUrl: %s"%(realUrl))
            downloadSound(realUrl, type_id, book_name)            
        else:
            print("[Log]: request downlaod url failure!")
    except urllib.ContentTooShortError:
        print('[Log]: [requestDownloadUrl] Network conditions is not good.Reloading.')
        time.sleep(5)
        requestDownloadUrl(episodes, book_id, book_type, type_id, book_name)
    except :
        print('[Log]: [requestDownloadUrl] other except.Reloading.')
        time.sleep(10)
        requestDownloadUrl(episodes, book_id, book_type, type_id, book_name)
    finally:
        pass

def getBookDownloadList(book_type, book_id, pend, type_id, book_name) :
    try:
        _dr = 'http://app.tingchina.com/book_downlist.asp?pstr=1&type=%s&bookID=%s&pend=%s'%(book_type, book_id, pend)
        _responseDownload = requests.get(_dr)
        _jsonDownload = json.loads(_responseDownload.text)
        _msg = _jsonDownload['msg']
        if _msg == 'OK' :
            downloadLists = _jsonDownload['data']
            if downloadLists == None :
                return
            _dsize = len(downloadLists)
            for num in range(0, _dsize) :
                _epis = downloadLists[num]['epis']
                requestDownloadUrl(_epis, book_id, book_type, type_id, book_name)
        else :
            print("[Log]:  get download lists failure.")    
    except urllib.ContentTooShortError:
        print("[Log]: getBookDownloadList Network conditions is not good. Reloading.")
        time.sleep(5)
        getBookDownloadList(book_type, book_id, pend, type_id, book_name)
    except :
        print("[Log]: getBookDownloadList other except. Reloading.")
        time.sleep(10)
        getBookDownloadList(book_type, book_id, pend, type_id, book_name)
    finally:
        pass


def requestGetBook(type, bookId): 
    try:
        s = requests.get('http://app.tingchina.com/book_disp.asp?oauth_token=&type=%s&bookID=%s' %(str(type),bookId))
        jsonStr = json.dumps(s.text)
        #print(jsonStr)

        jm1 = json.loads(s.text)
        msg = jm1['msg']
        if msg == 'OK':
            data = jm1['data']
            book_id = jm1['data']['bookID']
            book_name = jm1['data']['bookName']
            pend = jm1['data']['bookCount']
            type_id = jm1['data']['typeId']

            _bookType = searchBookInfo(book_id, book_name)
            if _bookType == -1:
                #print("### no book info skip.")
                return -1000
            if  _bookType == None:
                #print("### no book info skip.")
                return -1000

            book_type = str(_bookType)
            getBookDownloadList(book_type, book_id, pend, type_id, book_name)

        else:
            print("[Log]: request get book failure")
            return -1000
    except urllib.ContentTooShortError:
        print('[Log]: [requestGetBook] Network conditions is not good.Reloading.')
        time.sleep(5)
        requestGetBook(type, bookId)
    except :
        print('[Log]: [requestGetBook] other excpet.Reloading.')
        time.sleep(10)
        requestGetBook(type, bookId)
    finally:
        pass

startBookId = input('please enter start bookid: ')
endBookId = input('please enter end bookid:')

def startRequest(num):
    result = requestGetBook(1, num)
    if result == -1000 :
        result = requestGetBook(2, num)
    return result 

for num in range(startBookId, endBookId + 1):
    print("[Log]: book id %d"%(num))
    result = 0
    try : 
        result = startRequest(num)
    except urllib.ContentTooShortError:
        print("[Log]: Network conditions is not good.Reloading.")
        time.sleep(5)
        result = startRequest(num)
    except :
        print("[Log]: other except.")
        time.sleep(10)
        result = startRequest(num)
    finally :
        if result == -1000 :
            pass
        else :
            printCurrentTime()
            print("[Log]: search area [%s-%s], current book id : %d"%(startBookId, endBookId, num))
        
 
