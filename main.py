import time
import sys
import os
import pyperclip
import pyautogui
import requests
import json
import win32api,win32con
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
league = config.get("DEFAULT","league")


def getNameAndType(clipboard):
    if clipboard.startswith('稀 有 度:') == False:
        return None, None
    try:
        if clipboard.splitlines()[2].startswith('--------'):
            return None, clipboard.splitlines()[1]
        else:
            return clipboard.splitlines()[1], clipboard.splitlines()[2]
    except:
        return None
def process_dict(s):
    if s['price']:
        single_price = s['price']['amount']
        unit = s['price']['currency']
        price_info = str(single_price) + " "+ unit
        return price_info
    else:
        return '无定价'

def findTradeInfo(clipboard):
    name, itemtype = getNameAndType(clipboard)
    if itemtype == None:
        return None
    # print('finding ' + itemtype)
    headers = {'Content-Type': 'application/json'}
    if name != None:
        payload = {"query":{"status":{"option":"any"},"name": name,"type":itemtype ,"stats":[{"type":"and","filters":[]}]},"filters":{"trade_filters":{"filters":{"indexed":{"option":"1day"}},"disabled":False}},"sort":{"price":"asc"}}
    else:
        payload = {"query":{"status":{"option":"any"},"type":itemtype ,"stats":[{"type":"and","filters":[]}]},"filters":{"trade_filters":{"filters":{"indexed":{"option":"1day"}},"disabled":False}},"sort":{"price":"asc"}}
    url = "https://poe.game.qq.com/api/trade/search/"+league    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print( 'post error ' + str(response.status_code))
        return
    
    itemid = response.json()['id']
    list = response.json()['result']
    # print( "total:" + str(response.json()['total'] ))
    url='https://poe.game.qq.com/api/trade/fetch/'
    maxCount = 10
    step = int(len(list)/maxCount) + 1
    for i in range(0,len(list),step):
        url = url + list[i] + ','
    url = url[:-1]
    url = url + '?query=' + itemid
    
    result = requests.get(url)
    if result.status_code != 200:
        print( 'get error ' + str(response.status_code))
        return

    if name !=None:
        tmpString = name + " "+itemtype
    else:
        tmpString = itemtype
        
    tmpString = tmpString + '\n' + "市场库存:" + str(response.json()['total'] )
    print( "市场库存:" + str(response.json()['total'] ))
    print("+++++++++++++++++++++++++")    
    infolist = result.json()['result']
    page = int(response.json()['total']/10)
    itemid = ''
    for info in infolist:
        print(info['id'])
        itemid = itemid + info['id'] + ","
        tooltip = "ID: %s 价格 %s" % (info['listing']['account']['lastCharacterName'], process_dict(info['listing']))
        print(tooltip)
        tmpString = tmpString + '\n' + tooltip
    win32api.MessageBox(0, tmpString, "查询结果",win32con.MB_OK)
def mainLoop():
    print('Press Ctrl+C in POE client')
    pyperclip.copy('')
    recent_value = ''
    while True:
        clipboard = pyperclip.paste()
        if clipboard != recent_value:
            print( 'clipboard changed' )
            recent_value = clipboard
            print(clipboard)
            findTradeInfo(clipboard)
            
        time.sleep(0.1)


if __name__ == "__main__":
    mainLoop()
