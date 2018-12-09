
# coding: utf-8

# In[ ]:


import time
import requests
import nltk
import string
# from collections import Counter
from nltk.stem.porter import PorterStemmer #import porter algorithm的套件
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.corpus import wordnet
#用以定義dictionary的資料結構
from collections import defaultdict 
import math

#csv寫入
import csv
import numpy as np

import sqlite3 as lite
con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]

porter = PorterStemmer()  #定義方法
lemma = WordNetLemmatizer()
requests.packages.urllib3.disable_warnings()
headers = {'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


# In[ ]:


# c.execute("""DROP Table Variable""")
# c.execute("""CREATE TABLE Variable(vId INTEGER PRIMARY KEY AUTOINCREMENT, Name CHAR(50), actor FLOAT, numcast FLOAT, director FLOAT, storyline FLOAT, marketing FLOAT, series FLOAT, RealScore FLOAT)""")


# In[ ]:


# c.execute("""DROP Table Feature""")
# c.execute("CREATE TABLE Feature(wId INTEGER PRIMARY KEY AUTOINCREMENT, word CHAR(20))")


# In[ ]:


#詞性
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


# In[ ]:


#tokenize 的方法，lemmatization
def tokenize(word):
    res = nltk.word_tokenize(word)
    wlemma = []
    for w, pos in pos_tag(res):
        wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
        wlemma.append(lemma.lemmatize(w, wordnet_pos))

    stop = set(stopwords.words('english'))
    final = []

    for s in wlemma:
        if s not in stop:
            if s.isalpha() and len(s) > 2:
                final.append(s)
    return final


# In[ ]:


def TF(string):
    tf = defaultdict(int) #建立Dictionary的資料結構，以term作爲key，頻率做value，e.g. 'word' : 3
    res = nltk.word_tokenize(word)
    wlemma = []
    for w, pos in pos_tag(res):
        wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
        wlemma.append(lemma.lemmatize(w, wordnet_pos))
    stop = set(stopwords.words('english'))
    final = []
    for s in wlemma:
        if s not in stop:
            if s.isalpha() and len(s) > 2:
                final.append(s)
    for t in final:              #將斷出來的字統計為term的次數
        tf[t] += 1
    return tf


# Traing Part

# In[ ]:


#每部電影的資料
for i in range(1,780):
    Name = d.execute("""SELECT Name FROM Movie_info WHERE mId = ?""",(i,)).fetchone()
    Realscore = d.execute("""SELECT rating FROM Movie_info WHERE mId = ?""",(i,)).fetchone()
    c.execute("""INSERT INTO Variable(Name, Realscore) VALUES(?, ?)""",(Name, Realscore))


# In[ ]:


# 前500大明星榜各自有分
for i in range(1,501):
    score = (10 - 0.01 * i)
    c.execute("Update Actor SET score = ? WHERE actId = ? AND actId""",(score, i,))

# 不在前500大明星榜都沒分數
c.execute("Update Actor SET score = 0 WHERE actId > 500""")


# In[ ]:


#前250的導演都給 1 分
for i in range(1,251):
    c.execute("Update Director SET score = 1 WHERE dId = ?""",(i,))

#不在前250導演榜都沒分數
c.execute("Update Director SET score = 0 WHERE dId > 250""")


# In[ ]:


for i in range(1, 780):
    
    # director score
    director = d.execute("""Select dId From Movie_info WHERE mId = ?""",(i,)).fetchone()
    score = d.execute("""Select score From Director WHERE dId = ?""",(director,)).fetchone()
    if score == None:
        score = 0
    c.execute("""Update Variable SET director = ? WHERE vId = ?""",(score, i,))


    #actor score
    #number of cast score
    actor = d.execute("""Select actId From Movie_info WHERE mId = ?""",(i,)).fetchone()
    if actor != None:

        test = actor.replace(" ","").split(";")
        ascore = 0
        for item in test:
            if item == '':
                continue
            flag = d.execute("""Select score From Actor Where actId = ?""",(item,)).fetchone()
            ascore += flag
    else:
        ascore = 0

    c.execute("""Update Variable SET actor = ?, numcast = ? WHERE vId = ?""",(ascore, len(test)/10, i,))


# In[ ]:


# Marketing score
for i in range(1, 780):
    market = d.execute("""Select num_video_photo From Movie_info WHERE mId = ?""",(i,)).fetchone()
    if market == None:
        market = 0
        c.execute("""Update Movie_info SET num_video_photo = 0 WHERE mId = ?""",(i,))
    mscore = market / 10
    c.execute("""Update Variable SET marketing = ? WHERE vId = ?""",(mscore, i,))


# In[ ]:


# If the movie is part of a series,series score就是這個影集的分數，若不是，則5分
for i in range(1, 780):
    extend = d.execute("""Select extend_sId From Movie_info WHERE mId = ?""",(i,)).fetchone()
    if extend != None:
        escore = d.execute("""Select avgrating From Series_info WHERE mId = ?""",(extend,)).fetchone()
    else:
        escore = 5
    c.execute("""Update Variable SET series = ? WHERE vId = ?""",(escore, i,))


# In[ ]:


con.commit()


# Feature Selection

# In[ ]:


#將training data 的 storyline 做 tokenize
Storyline = d.execute("SELECT storyline FROM Movie_info").fetchall()
storyline_token = defaultdict()
for i in range(0,779):
    index = i + 1
    if Storyline[i] != None:
        word = Storyline[i].translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).lower() #將標點符號換成 whitespace，方便處理
        tokens = tokenize(word)
    else:
        tokens = ''
    storyline_token[index] = tokens


# In[ ]:


# 先定義 3 個 class
class_doc_id = {}
high = d.execute("""Select mId From Movie_info Where rating >= 8""").fetchall()

class_doc_id['high'] = high
medium = d.execute("""Select mId From Movie_info Where rating >= 6 and rating < 8""").fetchall()

class_doc_id['medium'] = medium
low = d.execute("""Select mId From Movie_info Where rating < 6""").fetchall()

class_doc_id['low'] = low

total_doc_id = high + medium + low


# In[ ]:


#建立字典，算每個 term在每個文件的 tf，還有該 term 的 collection frequecy

Class_CF = {}
doc_tf = {}
dictionary = []

#掃過每個class
for classid in class_doc_id:
    CF = defaultdict(int) #儲存每個 term出現在 collection 的次數的 dictionary
    #每個文件的 TF 和每個 class 的 CF dictionary，每個 Term 的所有 TF 加起來就是他的 CF
    for fileid in class_doc_id[classid]: #分別讀取每個文件
        word = d.execute("""Select storyline From Movie_info Where mId = ?""",(fileid,)).fetchone()
        if word != '' and word != None:
            tf = TF(word)
            for w in tf:
                CF[w] += tf[w]
                if w not in dictionary:
                    dictionary.append(w)
        else:
            tf = {}
        doc_tf[fileid] = tf
    Class_CF[classid] = CF


# In[ ]:


#Likelihood Ratio

matrix = np.zeros((3, len(dictionary)))  #把每個term在每個class裏的特徵值算出來
termid = 1


for term in dictionary:
    for classid in Class_CF:
        n11 = 0
        n10 = 0
        n01 = 0
        n00 = 0
        for fileid in class_doc_id[classid]:
            if term in doc_tf[fileid]:
                n11 += 1                   #true present
            else:
                n10 += 1                   #true absent
        for fileid in total_doc_id:
            if fileid not in class_doc_id[classid]:
                if term in doc_tf[fileid]:
                    n01 += 1               #false present
                else:
                    n00 += 1               #false absent

        N = n11 + n10 + n01 + n00
        numerator = ((((n11+n01)/N)**n11) * ((1-((n11+n01)/N))**n10)) * ((((n11+n01)/N)**n01) * ((1-((n11+n01)/N))**n00))
        denominator = (((n11/(n11+n10))**n11) * ((1-n11/(n11+n10))**n10)) * (((n01/(n01+n00))**n01) * ((1-n01/(n01+n00))**n00))
        
        value = (-2) * math.log(numerator/denominator)   #算兩個假設的 likelihood ratio
        if classid == 'high':
            index = 0
        elif classid == 'medium':
            index = 1
        else:
            index = 2
        matrix[index - 1][termid - 1] = value
    termid += 1#換下一個 term


# In[ ]:


#挑出各個 class最高分的 5個 term 做 feature

def getfeature(matrix):
    feature_list = []
    incase = []
    for i in range(0,3):
        classid_list = matrix[i][0:]
        position = sorted(range(len(classid_list)), key=lambda i: classid_list[i], reverse = True)

        pos = []
        for p in range(0,5):
            pos.append(position[p])

        for ft in pos:
            if dictionary[ft] not in feature_list:
                feature_list.append(dictionary[ft])

    return feature_list

feature_term_list = getfeature(matrix)


# In[ ]:


#建立 term 之於 class的 matrix
condprob = np.zeros((len(feature_term_list), 3))  #建立 condition probability 的 matrix

#掃過每個class
for classid in class_doc_id:
    CF = defaultdict(int) #儲存每個term出現在 collection 的次數的 dictionary

    denominator = 0
    for fileid in class_doc_id[classid]: #分別讀取每個文件
        word = d.execute("""Select storyline From Movie_info Where mId = ?""",(fileid,)).fetchone()
        if word != '' and word != None:
            tf = TF(word)
            for w in tf:
                CF[w] += tf[w]
                denominator += tf[w]

    denominator = denominator + len(feature_term_list)

    if classid == 'high':
        index = 0
    elif classid == 'medium':
        index = 1
    else:
        index = 2
    for i in range(0, len(feature_term_list)):
        term = feature_term_list[i]
        prob = (CF[term] + 1) / denominator
        condprob[i][index] = prob


# In[ ]:


con.commit()


# Testing part

# In[ ]:


#每部電影的資料
for i in range(1,151):
    Name = d.execute("""SELECT Name FROM test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    Realscore = d.execute("""SELECT rating FROM test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    c.execute("""INSERT INTO Variable(Name, Realscore) VALUES(?, ?)""",(Name, Realscore))


# In[ ]:


for i in range(1, 151):
    index = i + 779
    # director score
    director = d.execute("""Select dId From test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    score = d.execute("""Select score From Director WHERE dId = ?""",(director,)).fetchone()
    if score == None:
        score = 0
        
    c.execute("""Update Variable SET director = ? WHERE vId = ?""",(score, index,))


    #actor score
    #number of cast score
    actor = d.execute("""Select actId From test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    if actor != None:

        test = actor.replace(" ","").split(";")
        ascore = 0
        for item in test:
            if item == '':
                continue
            flag = d.execute("""Select score From Actor Where actId = ?""",(item,)).fetchone()
            ascore += flag
    else:
        ascore = 0

    c.execute("""Update Variable SET actor = ?, numcast = ? WHERE vId = ?""",(ascore, len(test)/10, index,))


# In[ ]:


#Marketing Score
for i in range(1, 151):
    index = i + 779
    market = d.execute("""Select num_video_photo From test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    if market == None:
        market = 0
        c.execute("""Update test_Movie_info SET num_video_photo = 0 WHERE mId = ?""",(i,))
    mscore = market / 10
    c.execute("""Update Variable SET marketing = ? WHERE vId = ?""",(mscore, index,))


# In[ ]:


# Series Score
for i in range(1, 151):
    index = i + 779
    extend = d.execute("""Select extend_sId From test_Movie_info WHERE mId = ?""",(i,)).fetchone()
    if extend != None:
        escore = d.execute("""Select avgrating From Series_info WHERE mId = ?""",(extend,)).fetchone()
    else:
        escore = 5
    c.execute("""Update Variable SET series = ? WHERE vId = ?""",(escore, index,))


# In[ ]:


#testing data 的編號
test_doc_id = d.execute("""Select vId FROM Variable Where vId > 779""").fetchall()


# In[ ]:


#Storyline score

for fileid in test_doc_id: #分別讀取每個文件
    score = []
    row = []
    row.append(fileid)
    index = fileid - 779
    #prior probability
    for i in range(0,3):
        score.append(math.log(1/3))

    #取 testing data 中每個 document 的 term
    
    words = d.execute("""Select storyline From test_Movie_info Where mId = ?""",(index,)).fetchone()
    if words != None:
        word = words.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))) #將標點符號換成 whitespace，方便處理
        token = tokenize(word)

        #計算對於這個 document，每個class的score
        for classid in range(0, 3):
            for t in token:
                if t in feature_term_list:
                    tid = feature_term_list.index(t)
                    score[classid] += math.log(condprob[tid][classid])

    else:
        score = [1, 2, 1]
    #取 argmax

    classscore = 10 - 2 * (score.index(max(score)) + 1)
    c.execute("""Update Variable SET storyline = ? WHERE vId = ?""",(classscore, fileid,))


# In[ ]:


con.commit()

