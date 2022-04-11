import telebot
import requests
from bs4 import BeautifulSoup
from apiclient.discovery import build
import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams

token = "1938279438:AAFjVXCcG8TVRuh3PEaSj-orQEApIiTGg4k"

bots = telebot.TeleBot(token)
# chat_id=890093365
dblocal = mysql.connector.connect(
    host='relational.fit.cvut.cz',
    database='AdventureWorks2014',
    user='guest',
    password='relational'
)



@bots.message_handler(commands=['help'])
def bots_start(message):
    chat_id = message.chat.id
    user = message.chat.first_name
    try:
        desc = "Hii "+ user+", Berikut adalah <b>perintah</b> yang bisa km gunakan:\n"
        desc += "/s kode_emiten untuk mencari news dengan metode scraping, kode_emiten optional \n"
        desc += "/g kode_emiten untuk mencari news dengan pencarian google, kode_emiten optional \n"
        desc += "/heatmap menampilkan chart sample chart heatmap \n"
        bots.send_message(chat_id, desc,parse_mode='html')
    except:
        bots.reply_to(message, 'Ada error di modul help')

@bots.message_handler(commands=['s'])
def bots_start(message):
    try:
        scrap_emiten(message)
    except:
        bots.reply_to(message, 'Ada error di modul s')

@bots.message_handler(commands=['g'])
def bots_start(message):
    try:
        gs_emiten(message)
    except:
        bots.reply_to(message, 'Ada error di modul g')

def scrap_emiten(message):
    texts = message.text.split(" ")
    chat_id = message.chat.id
    user = message.chat.first_name
    
    if len(texts)>1:
        texts.remove("/s")
        list_positif = texts
    else:
        list_positif =["rights issue", "deviden", "buyback",
                       "akuisisi", "laba naik", "ekspansi",
                       "merger", "pengendali", "kontrak baru",
                       "targetkan","inovasi","cetak laba","anak usaha",
                       "masuknya investor","private placement"]
    hasil = []
    hasil2 = []
    portal1 = 'https://investasi.kontan.co.id'
    scraping1 = BeautifulSoup(requests.get(portal1).text, 'html.parser')
    posts = scraping1.find("div", {"class": "list-berita"}).find_all("li")
    for post in posts:
        section = post.find("div", {"class": "pic"})
        title = section.find('img')['alt']
        href = post.find('a')['href']
        for x in list_positif:
            if x in title.lower():
                hasil.append(title)
                # print(title)
                link = portal1 + href
                hasil2.append(link)
                
    portal2 = 'https://www.idxchannel.com/market-news'
    scraping2 = BeautifulSoup(requests.get(portal2).text, 'html.parser')
    posts = scraping2.find_all(class_="container-news")
    for post in posts:
        sections = post.find_all(class_="bt-con")
        for section in sections:
            title = section.find(class_='title-capt').find('a').get_text()
            href = section.find('a')['href']
            for x in list_positif:
                if x in title.lower():
                    hasil.append(title)
                    link = href
                    hasil2.append(link)

    portal4 = 'https://www.emitennews.com/category/emiten'
    scraping4 = BeautifulSoup(requests.get(portal4).text, 'html.parser')
    posts = scraping4.find_all("div", {"class": "list-category"})
    for post in posts:
        sections = post.find_all("a")
        for section in sections:
            title = section.find('img')['alt']
            href = section['href']

            for x in list_positif:
                if x in title.lower():
                    hasil.append(title)
                    link = href
                    hasil2.append(link)
                    
    if len(hasil2) > 0:
        for x in hasil2:
            
            bots.send_message(chat_id, x,parse_mode='html')
    else:
        bots.reply_to(message, "news tidak ditemukan")

def gs_emiten(message):
    texts = message.text.split(" ")
    chat_id = message.chat.id
    
    if len(texts)>1:
        texts.remove("/g")
        list_positif = texts
    else:
        list_positif =["rights issue", "deviden", "buyback",
                       "akuisisi", "laba naik", "ekspansi",
                       "merger", "pengendali baru", "kontrak baru",
                       "targetkan","inovasi","cetak laba","anak usaha"]

    api_key = "AIzaSyDnMMiOOF4PnEFgYrMI0J-jDE2YlzKMkMI"
    resource = build("customsearch", 'v1', developerKey=api_key).cse()

    link = []
    for x in list_positif:
        result = resource.list(q=x, cx='ca1eb3e1b6d154778', sort='date').execute()
        if len(result['items']) > 0:
            for item in result['items']:
                if x in item['link']:
                    link.append(item['link'])
    if len(link) > 0:
        for x in link:
            # bots.reply_to(message, x)
            bots.send_message(chat_id, x,parse_mode='html')
            
    else:
        bots.reply_to(message, "news tidak ditemukan")

@bots.message_handler(commands=['heatmap'])
def send_welcome(message):
    chat_id = message.chat.id
    user = message.chat.first_name
    text = message.text
   
    sqlData ="""select year(a.OrderDate) v_year, month(a.OrderDate) v_month, sum(a.TotalDue) revenue
                from PurchaseOrderHeader a
                where year(a.OrderDate)>2011
                group by v_year, v_month
                order by v_year, v_month"""
    dataPerformance = pd.read_sql(sqlData, dblocal)
    dataPerformance = dataPerformance.pivot("v_year", "v_month", "revenue")
    
    rcParams['figure.figsize'] = 15,8
    fig, ax = plt.subplots()
    ax = sns.heatmap(dataPerformance, linewidths=.5, cmap="YlGnBu", annot=True, fmt='.0f', cbar=False)
    # plt.show()
    # plt.savefig('report_sam.png')
    fig.savefig('heatmap.png', bbox_inches='tight')
        
    bots.send_document(chat_id,open('heatmap.png','rb'))


print("bot running")
bots.polling()


