
# coding: utf-8

# In[1]:


import requests 
from lxml import html
from bs4 import BeautifulSoup
from datetime import datetime 
from datetime import timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

import nltk
import string
# from collections import Counter
from nltk.stem.porter import PorterStemmer #import porter algorithm的套件
from nltk.corpus import stopwords



import sqlite3 as lite
con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]

requests.packages.urllib3.disable_warnings()
headers = {'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


# 建立資料表 Company
# c.execute("""CREATE TABLE Company(cId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), num_publish INTEGER, score FLOAT)""")
# 
# 建立資料表 Director
# c.execute("""CREATE TABLE Director(dId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")
# 
# 建立資料表 Actor
# c.execute("""CREATE TABLE Actor(actId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")

# # 刪除資料表
# c.execute("""DROP TABLE Movie_info""")
# 
# c.execute("""DROP TABLE Series_info""")
# 
# # 建立資料表
# # c.execute("""CREATE TABLE Movie_info(mId INTEGER PRIMARY KEY AUTOINCREMENT, Date TIMESTAMP, Name CHAR(50), extend_sId INTEGER, rating FLOAT, storyline_len INTEGER, storyline char(255), num_video_photo INTEGER, num_cast INTEGER, actId char(100), dId INTEGER, cId INTEGER)""")
# c.execute("""CREATE TABLE Movie_info(mId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), extend_sId INTEGER, rating FLOAT, storyline_len INTEGER, storyline char(255), num_video_photo INTEGER, num_cast INTEGER, actId char(100), dId INTEGER)""")
# 
# 
# c.execute("""CREATE TABLE Series_info(mId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), avgrating FLOAT)""")
# 
# 
# # 輸入資料
# # c.execute("""INSERT INTO Movie_info(Name) VALUES("test")""")
# 
# 
# 
# # 印出資料
# f = c.execute("""SELECT * FROM Movie_info""").fetchall()
# 
# 
# # insert加變數的用法
# # today = datetime.now()
# # f = c.execute("""INSERT INTO Movie_info(date) VALUES(?)""",(today,))
# # c.execute("""DROP TABLE Company_test""")
# # c.execute("""DROP TABLE Director_test""")
# # c.execute("""DROP TABLE Actor_test""")
# # c.execute("""CREATE TABLE Company_test(cId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), num_publish INTEGER, score FLOAT)""")
# # c.execute("""CREATE TABLE Director_test(dId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")
# # c.execute("""CREATE TABLE Actor_test(actId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")
# 
# print(f)

# c.execute("""DROP TABLE Company_test""")
# c.execute("""DROP TABLE Director_test""")
# c.execute("""DROP TABLE Actor_test""")
# c.execute("""CREATE TABLE Company_test(cId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), num_publish INTEGER, score FLOAT)""")
# c.execute("""CREATE TABLE Director_test(dId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")
# c.execute("""CREATE TABLE Actor_test(actId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), Rank INTEGER, score FLOAT)""")

# In[20]:


#tokenize 的方法
def tokenize(word):
    res = nltk.word_tokenize(word)
    porter = PorterStemmer()  #定義方法
    stemmer = [ porter.stem(element) for element in res]  #stemming
    stop = set(stopwords.words('english'))
    final = []
    for s in stemmer:
        if s not in stop:
            if s.isalpha() and len(s) > 2:
                final.append(s)
    return final


# In[21]:


# url = 'https://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm'
# urllist = ['https://www.imdb.com/search/title?genres=horror&sort=user_rating,desc&start=1&explore=title_type,genres&ref_=adv_nxt']
urllist = []
for i in range(1, 452, 50):
    url = 'https://www.imdb.com/search/title?genres=horror&sort=user_rating,desc&start=' + str(i) + '&explore=title_type,genres&ref_=adv_nxt'
    urllist.append(url)
# print(urllist)


# In[22]:


# movie_link_list = []
# count = 1
for url in urllist:
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text, 'lxml')
    crawler = soup.select("div.lister-item-content")
    for s in crawler:
        try:
            # Movie Name
            a1 = s.select("h3.lister-item-header a")[0]
            a = a1
            
            # Get movie series
            a2 = s.select("h3.lister-item-header a")[1]
            a = a2
            relative = a1.text
            relid = d.execute("SELECT mId FROM Series_info WHERE Name = ? ",(relative,)).fetchone()
            if relid  == None:
                c.execute("""INSERT INTO Series_info(Name) VALUES(?)""",(relative,))
                relid = d.execute("SELECT mId FROM Series_info WHERE Name = ? ",(relative,)).fetchone()
            
            # Link info
            movielink = 'https://www.imdb.com' + a['href']
#             movie_link_list.append(link)
            
            # Rating info
            rating = s.select("div.ratings-bar strong")[0].text
            
            # Store into db
            c.execute("""INSERT INTO Movie_info(Name, rating, extend_sId) VALUES(?, ?, ?)""",(a.text, rating, relid,))
        except:
            # Movie Name
            a1 = s.select("a")[0]
            a = a1
            #Link info
            movielink = 'https://www.imdb.com' + a['href']
#             movie_link_list.append(link)
            
            # Rating info
            rating = s.select("div.ratings-bar strong")[0].text
            
            # Store into db
            c.execute("""INSERT INTO Movie_info(Name, rating) VALUES(?, ?)""",(a.text, rating,))
            
        mId = d.execute("""SELECT mId FROM Movie_info WHERE Name = ?""",(a.text,)).fetchone()
#         print(mId)
        
        #crawler part 2
        res = requests.get(movielink, headers = headers)
        soup = BeautifulSoup(res.text, 'lxml')
        
        
        num_photo_video = soup.select("div.combined-see-more")
        num_photo = soup.select("div.combined-see-more a")
        try:
            if len(num_photo) != 0:
                if len(num_photo_video) == 1:
                    text = num_photo[1].text
                    num = text.replace('See all', '').replace('photos', '').replace('photo', '').replace('\n', '')
                    num = int(num)
                else:
                    textv = num_photo[0].text
                    numv = int(textv.replace('See all', '').replace('videos', '').replace('video', '')).replace('\n')
                    textp = num_photo[2].text
                    nump = int(textp.replace('See all', '').replace('photos', '').replace('photo', '')).replace('\n')
                    num = numv + nump  
            else:
                text = '0'
                num = int(text)
            
        except:
            text = '0'
            num = int(text)
        c.execute("""UPDATE Movie_info SET num_video_photo = ? WHERE mId = ?""",(num, mId,))
        
        
        
        try:
            #storyline info
            storyline = soup.select("div.inline p span")[0].text
            sterm = tokenize(storyline)
            story_len = len(sterm)

        except:      
            #storyline info
            storyline = ''
            story_len = 0
        c.execute("""UPDATE Movie_info SET storyline_len = ?, storyline = ? WHERE mId = ?""", (story_len, storyline, mId,))
        
        #
        nextcrawl = soup.select("div#titleCast div.see-more a")
        try:
            nextcrawl = nextcrawl[0]['href']
            nextcrawl = movielink.replace("?ref_=adv_li_tt", "") + nextcrawl

            # Crawler page of cast info of this movie
            res = requests.get(nextcrawl, headers = headers)
            soup = BeautifulSoup(res.text, 'lxml')

            #Directors info
            director = soup.select("div.header table.simpleTable tbody tr td.name a")[0].text.strip().replace("\n","")
            dId = d.execute("""SELECT dId FROM Director WHERE Name = ?""", (director,)).fetchone()
            if dId == None:
                c.execute("""INSERT INTO Director(Name) VALUES(?)""", (director,))
            dId = d.execute("""SELECT dId FROM Director WHERE Name = ?""", (director,)).fetchone()
        
            #Actors info
            actor = soup.select("table.cast_list tr td a")
            actorlist = []
            for a in actor:
                act = a.text
                if act == '':
                    continue
                if act[0] == ' ':
                    act = act[1:]
                actorlist.append(act.replace('\n', ''))
                
            actId_list = ''
            for actor in actorlist:
                actId = d.execute("""SELECT actId FROM Actor WHERE Name = ?""", (actor,)).fetchone()
                if actId == None:
                    c.execute("""INSERT INTO Actor(Name) VALUES(?)""", (actor,))
                actId = d.execute("""SELECT actId FROM Actor WHERE Name = ?""", (actor,)).fetchone()
                actId_list = actId_list + str(actId) + '; '
                
            num_cast = len(actorlist)
        except:
            #Directors info
            if len(soup.select("div.credit_summary_item a")) != 0:
                director = soup.select("div.credit_summary_item a")[0].text.strip().replace("\n","")
                dId = d.execute("""SELECT dId FROM Director WHERE Name = ?""", (director,)).fetchone()
                if dId == None:
                    c.execute("""INSERT INTO Director(Name) VALUES(?)""", (director,))
                dId = d.execute("""SELECT dId FROM Director WHERE Name = ?""", (director,)).fetchone()
            else:
                dId = 0

            #Actors info
            actor = ''
            actId_list = ''
            num_cast = 0
            
        #store into db
        c.execute("""UPDATE Movie_info SET num_cast = ?, actId = ?, dId = ? WHERE mId = ?""", (num_cast, actId_list, dId, mId,))


# In[2]:


# testm = c.execute("SELECT * FROM Movie_info").fetchall()
# # print(testm)
# for t in testm:
#     print(t)


# In[24]:


con.commit()

