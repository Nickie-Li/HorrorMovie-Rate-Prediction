
# coding: utf-8

# In[ ]:


import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import f_regression
import sqlite3 as lite
con = lite.connect('IMDB.sqlite')
c = con.cursor()
d = con.cursor()
d.row_factory = lambda cursor, row: row[0]


# In[ ]:


var = ['actor', 'numcast', 'director', 'storyline', 'marketing', 'series']


# In[ ]:


# variable = c.execute("Select actor, numcast, director, storyline, marketing, series FROM Variable").fetchall()
# variable


# Training Part

# In[ ]:


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
    print(row)


# In[ ]:


X = np.array(numpx)
# print(X)
y = np.array(numpy)
# print(y)

lm = LinearRegression()
lm.fit(X, y)

# 印出係數
print(lm.coef_)

# 印出截距
print(lm.intercept_ )


# Testing Evaluation

# In[ ]:


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


# In[ ]:


to_be_predicted = np.array(numpxt)
predicted_rate = lm.predict(to_be_predicted)

# print(predicted_rate)
true = 0
false = 0
for i in range(0, 150):
    delta = abs(predicted_rate[i] - numpyt[i])
    if delta > 0.5:
        false += 1
    else:
        true += 1
# print(true)
# print(false)

accuracy = true / 150
print(accuracy)


# Evaluation

# In[ ]:


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

