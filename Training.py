
# coding: utf-8

# In[17]:


import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import f_regression
import sqlite3 as lite
con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]
from sklearn.metrics import acc


# In[18]:


var = ['actor', 'numcast', 'director', 'storyline', 'marketing', 'series']


# Training Part

# In[19]:


numpx = []
numpy = []
for i in range(1,780):
    row = []
    actor = d.execute("Select actor FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(actor)
    numcast = d.execute("Select numcast FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(numcast)
    director = d.execute("Select director FROM Variable WHERE vId = ?",(i,)).fetchone()
    if director == None:
        director = 0
    row.append(director)
    storyline = d.execute("Select storyline FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(storyline)
    marketing = d.execute("Select marketing FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(marketing)
    series = d.execute("Select series FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(series)
    numpx.append(row)
    realscore = d.execute("Select RealScore FROM Variable WHERE vId = ?",(i,)).fetchone()
    numpy.append(realscore)


# In[20]:


X = np.array(numpx)
# print(X)
y = np.array(numpy)
# print(y)

lm = LinearRegression()
lm.fit(X, y)

# 印出係數
print("各項係數")
for l in lm.coef_:
    print(l)
# print(lm.coef_)

# 印出截距
print('截距:  ', lm.intercept_ )


# In[21]:


con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]


# In[22]:


numpxt = []
numpyt = []
for i in range(780,930):
    
    row = []
    actor = d.execute("Select actor FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(actor)
    numcast = d.execute("Select numcast FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(numcast)
    director = d.execute("Select director FROM Variable WHERE vId = ?",(i,)).fetchone()
    if director == None:
        director = 0
    row.append(director)
    storyline = d.execute("Select storyline FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(storyline)
    marketing = d.execute("Select marketing FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(marketing)
    series = d.execute("Select series FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(series)
    numpxt.append(row)
    realscore = d.execute("Select RealScore FROM Variable WHERE vId = ?",(i,)).fetchone()
    numpyt.append(realscore)
#     print(row)


# In[23]:


to_be_predicted = np.array(numpxt)
predicted_rate = lm.predict(to_be_predicted)

# print(predicted_rate)
# print(predicted_rate)
true = 0
false = 0
for i in range(0, 150):
    delta = abs(predicted_rate[i] - numpyt[i])
#     print(delta)
    if delta > 0.5:
        false += 1
    else:
        true += 1

accuracy = true / 150
print('Accuracy :  ', accuracy)


# Evaluation

# In[24]:


# 模型績效
mse = np.mean((lm.predict(X) - y) ** 2)
r_squared = lm.score(X, y)
adj_r_squared = r_squared - (1 - r_squared) * (X.shape[1] / (X.shape[0] - X.shape[1] - 1))

# 印出模型績效
print('MSE:    ', mse)
print('R Square:    ', r_squared)
print('adjusted R square:    ', adj_r_squared)
# 印出 p-value
print('p-value:    ',f_regression(X, y)[1])
count = 0
for item in f_regression(X, y)[1]:
    if item < 0.05:
        print(var[count], ':  ', 'true')
    else:
        print(var[count], ':  ', 'false')
    count += 1


# Training Part B

# In[25]:


con = lite.connect('../IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]


# In[26]:


numpx = []
numpy = []
for i in range(1,4662):
    if i <= 780 or i >= 930:
        row = []
        actor = d.execute("Select actor FROM Variable WHERE vId = ?",(i,)).fetchone()
        row.append(actor)
        numcast = d.execute("Select numcast FROM Variable WHERE vId = ?",(i,)).fetchone()
        row.append(numcast)
        director = d.execute("Select director FROM Variable WHERE vId = ?",(i,)).fetchone()
        if director == None:
            director = 0
        row.append(director)
        storyline = d.execute("Select storyline FROM Variable WHERE vId = ?",(i,)).fetchone()
        row.append(storyline)
        marketing = d.execute("Select marketing FROM Variable WHERE vId = ?",(i,)).fetchone()
        row.append(marketing)
        series = d.execute("Select series FROM Variable WHERE vId = ?",(i,)).fetchone()
        row.append(series)
        numpx.append(row)
        realscore = d.execute("Select RealScore FROM Variable WHERE vId = ?",(i,)).fetchone()
        numpy.append(realscore)


# In[27]:


X = np.array(numpx)
# print(X)
y = np.array(numpy)
# print(y)

lm = LinearRegression()
lm.fit(X, y)

# 印出係數
print("各項係數")
for l in lm.coef_:
    print(l)
# print(lm.coef_)

# 印出截距
print('截距:  ', lm.intercept_ )


# Testing Evaluation

# In[28]:


con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]


# In[29]:


numpxt = []
numpyt = []
for i in range(780,930):
    
    row = []
    actor = d.execute("Select actor FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(actor)
    numcast = d.execute("Select numcast FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(numcast)
    director = d.execute("Select director FROM Variable WHERE vId = ?",(i,)).fetchone()
    if director == None:
        director = 0
    row.append(director)
    storyline = d.execute("Select storyline FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(storyline)
    marketing = d.execute("Select marketing FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(marketing)
    series = d.execute("Select series FROM Variable WHERE vId = ?",(i,)).fetchone()
    row.append(series)
    numpxt.append(row)
    realscore = d.execute("Select RealScore FROM Variable WHERE vId = ?",(i,)).fetchone()
    numpyt.append(realscore)
#     print(row)


# In[30]:


to_be_predicted = np.array(numpxt)
predicted_rate = lm.predict(to_be_predicted)

# print(predicted_rate)
# print(predicted_rate)
true = 0
false = 0
for i in range(0, 150):
    delta = abs(predicted_rate[i] - numpyt[i])
#     print(delta)
    if delta > 0.5:
        false += 1
    else:
        true += 1
print(true)
print(false)

accuracy = true / 150
print('Accuracy :  ', accuracy)


# Evaluation

# In[31]:


# 模型績效
mse = np.mean((lm.predict(X) - y) ** 2)
r_squared = lm.score(X, y)
adj_r_squared = r_squared - (1 - r_squared) * (X.shape[1] / (X.shape[0] - X.shape[1] - 1))

# 印出模型績效
print('MSE:    ', mse)
print('R Square:    ', r_squared)
print('adjusted R square:    ', adj_r_squared)
# 印出 p-value
print('p-value:    ',f_regression(X, y)[1])
count = 0
for item in f_regression(X, y)[1]:
    if item < 0.05:
        print(var[count], ':  ', 'true')
    else:
        print(var[count], ':  ', 'false')
    count += 1


# In[32]:


import pickle #pickle模块

#保存Model(注:save文件夹要预先建立，否则会报错)
with open('LM_0.8.pickle', 'wb') as f:
    pickle.dump(lm, f)
    f.close()
#读取Model
with open('LM_0.8.pickle', 'rb') as f:
    clf2 = pickle.load(f)
    #测试读取后的Model
    print(clf2.predict(X[0:1]))

