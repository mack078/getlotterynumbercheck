#!/usr/bin/python
#coding:utf-8
import requests
import HTMLParser
from bs4 import BeautifulSoup
import datetime
import re
import json
import threading
import time
import Queue
import json
import sys
from Queue import Queue

IssueMax = 3 #檢測期數;奇數(單數)
Issue = (IssueMax - 1) / 2 #檢測中心點


def getNumber_str(numbers, name):
    data = [0] * len(numbers)
    for index , number in enumerate(numbers):
        if cmp("1分快三", name.encode('utf-8')) == 0 or cmp("5分快三", name.encode('utf-8')) == 0 or cmp("江?快三", name.encode('utf-8')) == 0 or cmp("安徽快三", name.encode('utf-8')) == 0:
            number = number.text.strip().split('-')
            data[index] = number[1]
        else:
            data[index] = number.text.strip()

    return data

def TgAlarm(title, siteURL, number):
    dic_num={0:u"零", 1:u"一", 2:u"二", 3:u"三", 4:u"四", 5:u"五", 6:u"六", 7:u"七", 8:u"八", 9:u"九"}
    headers = {'Content-Type': 'application/json'}
    tg_url = "TG告警连结"
    msg = '請檢查最近' + dic_num[IssueMax].encode('utf-8') + '筆，異常訊息' 
    txt = title
    text =  msg + txt.encode('utf-8') + '\n'
    for num in range(0, IssueMax):
        text = text + number[num].encode('utf-8') + '\n'

    text = text + siteURL.encode('utf-8')
    data = {"chat_id": "-448822280", "text": text , "disable_notification": "true"}
    response = requests.post(url=tg_url, headers=headers, data=json.dumps(data))
    print text

def checkNum(start, end, number, title, url):
    for num in range(start, end - 1):
        print str(num) + " " + number[num] + " - " + number[num + 1] + " = " + str( int(number[num]) - int(number[num + 1]) )
        if ( int(number[num]) - int(number[num + 1]) ) != 1 :
            TgAlarm(title, url, number)

def job(url, name, max, q):
    global Issue, IssueMax
    
    if cmp("北京PK10", name.encode('utf-8')) == 0 or cmp("北京幸运", name.encode('utf-8')) == 0 or cmp("湖北快三", name.encode('utf-8')) == 0 :
        q.put(name)
        return

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.find('h3', class_="select-title").text.strip()
    td = soup.find('td', class_="issue-numbers").text.strip()
    get_number = soup.find_all('td', class_="issue-numbers")

    if len(get_number) > 1:
        #alarm = False
        CrossDay = False
        Maxlen = len(str(max)) #最大值長度(位數)

        #處理class_="issue-numbers" 重複
        if cmp("幸运飞艇", name.encode('utf-8')) == 0 :
            index = 0
            numberADD = [0] * (len(get_number) / 2)
            for num in range(len(get_number)):
                if num % 2 == 0:
                    numberADD[index] = get_number[num]
                    index = index + 1
            get_number = numberADD

        get_number = getNumber_str(get_number, name)

        print " "
        print get_number

        if max != -1:
            print title.encode('utf-8') + " 檢測中心點:" + get_number[Issue].encode('utf-8') + " 最大值:" + str(max).encode('utf-8') + " 最大值長度:" + str(Maxlen).encode('utf-8')
            for num in range(0, IssueMax):
                print get_number[num] + " " + get_number[num][int(Maxlen) * -1 : -1] + get_number[num][-1]
                if int(get_number[num][int(Maxlen) * -1 : -1] + get_number[num][-1]) == int(max):
                    print "原檢測中心點= get_number[" + str(Issue).encode('utf-8') + "] " + get_number[Issue].encode('utf-8') 
                    Issue = num
                    CrossDay = True
                    print "位移檢測中心點= get_number[" + str(Issue).encode('utf-8') + "] " + get_number[num].encode('utf-8') 
                    break

        if CrossDay == True: #檢測跨日
            print title.encode('utf-8') + " " + "跨日"
            if int(get_number[Issue - 1][-1] ) != 1 and Issue != 0:
                TgAlarm(title, url, get_number)
            else:
                #checkNum(Issue - 1, 0, -1, get_number, title, url) #中心點向上檢查
                checkNum(0, Issue, get_number, title, url) #向下檢查至中心點
                checkNum(Issue, IssueMax, get_number, title, url) #中心點向下檢查

        else :
            print title.encode('utf-8') + " " + "未跨日"
            #checkNum(Issue, 0, -1, get_number, title, url) #中心點向上檢查
            #checkNum(Issue, IssueMax - 1, 1, get_number, title, url) #中心點向下檢查
            checkNum(0, IssueMax, get_number, title, url) #向下檢查


        #print(name + " Unexpected error: " + str(sys.exc_info()[0]))

    q.put(name)

def multithreading():
    q =Queue()
    threads = []
    input_file = open ('/usr/local/checkpy/url.json')
    json_array = json.load(input_file)

    for item in json_array:
        t = threading.Thread(target=job,args=(item['url'], item['name'], item['max'], q))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()


multithreading()
