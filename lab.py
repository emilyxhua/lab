# Import statements

import plotly 
import csv
import re
import numpy as np

import plotly.plotly as py
import plotly.graph_objs as go

# Importing the tweet_text2.csv file into the colab notebook

from google.colab import files
uploaded = files.upload()

csvfile = open('all_tweets_encoded_with_bots.csv', encoding="utf8", errors='ignore')

readCSV = csv.reader(csvfile, delimiter=",")

# Declaring variables
encodings = []           # list of (userInd, tweetStr, ideology, harassment, hate_speech, divisive, rights, tweetInd)
users = {}               # key: username string, value: index
hashtag_dict = {}        # key: hashtag string, value: index
rev_hashtag_dict = {}    # key: index, value: hashtag string (reverse of hashtag_dict)
allVals = []             # initial input from readCSV

def handle_hashtags(tweet):
  """
  Input: str tweet to be parsed for hashtags
  Output: list of integers corresponding to indices of hashtags
  """
  lst = re.findall('\#[A-Za-z][A-Za-z0-9]+', tweet)

  retlst = []

  for tag in lst:
      if tag in hashtag_dict.keys():
          retlst.append(hashtag_dict[tag])
      else:
          rev_hashtag_dict[len(hashtag_dict.keys())] = tag
          hashtag_dict[tag] = len(hashtag_dict.keys())
          retlst.append(hashtag_dict[tag])

  return retlst

# Reading the information from the CSV
for row in readCSV:
    allVals.append(row)
    encodings.append(row)

# Refining encodings so that values are in indices
for i in range(1, len(allVals)):
    row = allVals[i]
    user = row[0]
    tweet = row[1]
    pro = row[2]
    harassment = 0 if row[3] == '0' else 1
    hate_speech = 0 if row[4] == '0' else 1
    divisive = 0 if row[5] == '0' else 1
    rights = 0 if row[6] == '0' else 1
    
    # Encodes ideological leaning, with pro-life as -1 and pro-choice as 1
    if pro == 'Pro-Life':
        encodings[i][2] = -1
    elif pro == 'Pro-Choice':
        encodings[i][2] = 1
    else:
        encodings[i][2] = 0
    
    encodings[i][3] = harassment
    encodings[i][4] = hate_speech
    encodings[i][5] = divisive
    encodings[i][6] = rights

    # Encodes users
    if user in users.keys():
        encodings[i][0] = users[user]
    else:
        users[user] = len(users.keys())
        encodings[i][0] = users[user]
    
    # Converts tweets to indices
    encodings[i].append(handle_hashtags(tweet))

# Functions to calculate relevant statistics

def calculate_hashtag_harassment():
    """
    Output: List of [harassment/total] for all hashtags
    """
    harassment = [(0, 0)] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            x, y = harassment[tag]
            if row[3]:
                harassment[tag] = (x + 1, y + 1)
            else:
                harassment[tag] = (x, y + 1)
    toRet = [float(x) / float(y) for x, y in harassment]
    return toRet

def calculate_hashtag_hate():
    """
    Output: List of [hate/total] for all hashtags
    """
    hate = [(0, 0)] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            x, y = hate[tag]
            if row[4]:
                hate[tag] = (x + 1, y + 1)
            else:
                hate[tag] = (x, y + 1)
    toRet = [float(x) / float(y) for x, y in hate]
    return toRet

def calculate_hashtag_divisive():
    """
    Output: List of [divisive/total] for all hashtags
    """
    harassment = [(0, 0)] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            x, y = harassment[tag]
            if row[5]:
                harassment[tag] = (x + 1, y + 1)
            else:
                harassment[tag] = (x, y + 1)
    toRet = [float(x) / float(y) for x, y in harassment]
    return toRet

def calculate_hashtag_rights():
    """
    Output: List of [women's rights/total] for all hashtags
    """
    harassment = [(0, 0)] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            x, y = harassment[tag]
            if row[6]:
                harassment[tag] = (x + 1, y + 1)
            else:
                harassment[tag] = (x, y + 1)
    toRet = [float(x) / float(y) for x, y in harassment]
    return toRet

def calculate_hashtag_ideology():
    """
    Output: List of [ideology/total] for all hashtags
    """
    harassment = [(0, 0)] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            x, y = harassment[tag]
            harassment[tag] = (x + row[2], y + 1)
            
    toRet = [float(x) / float(y) for x, y in harassment]
    return toRet

def hashtag_counts():
    """
    Output: Lists of the number of times each hashtag is used
    """
    toRet = [0] * len(hashtag_dict.keys())
    for i in range(1, len(allVals)):
        row = encodings[i]
        hashtags = row[7]
        for tag in hashtags:
            toRet[tag]+= 1
    return toRet

# Creating lists to use in visualization containing the calculated percentages
harassment = calculate_hashtag_harassment()
hate = calculate_hashtag_hate()
divisive = calculate_hashtag_divisive()
counts = hashtag_counts()
ideology = calculate_hashtag_ideology()
rights = calculate_hashtag_rights()
names = [rev_hashtag_dict[i] for i in range(0,len(hashtag_dict.keys()))]

trace0 = go.Scatter(
    x=harassment,
    y=hate,
    text=names,
    mode='markers',
    marker=dict(
        color=['rgb(93, 164, 214)']*len(hashtag_dict.keys()),
        size=counts,
    )
)

layout = go.Layout(
    title='Harassment vs Hate',
    xaxis=dict(
        title='Harassment (Fraction of Tweets using Hashtag)',
    ),
    yaxis=dict(
        title='Hate (Fraction of Tweets using Hashtag)',
    )
)

data = [trace0]
fig = go.Figure(data=data, layout=layout)

py.iplot(fig, filename='bubblechart-text')

def summarize():
    lst = []
    for i in range(0, len(hashtag_dict.keys())):
        if (harassment[i] or divisive[i]) and rev_hashtag_dict[i] != "#StopKavanaugh":
            lst.append((harassment[i], divisive[i], counts[i], rev_hashtag_dict[i]))
    return lst

summ = summarize()
har1 = [x[0] for x in summ]
div1 = [x[1] for x in summ]
cts1 = [x[2] for x in summ]
nms1 = [x[3] for x in summ]

trace1 = go.Scatter(
    x=har1,
    y=div1,
    text=nms1,
    mode='markers',
    marker=dict(
        color=['rgb(93, 164, 214)']*len(har1),
        size=cts1,
    )
)
layout = go.Layout(
    title='Harassment vs Divisiveness',
    xaxis=dict(
        title='Harassment (Fraction of Tweets using Hashtag)',
    ),
    yaxis=dict(
        title='Divisiveness (Fraction of Tweets using Hashtag)',
    )
)

data = [trace1]
fig = go.Figure(data=data, layout=layout)

py.iplot(fig, filename='bubblechart-text1')

def summarize_two():
    lst = []
    for i in range(0, len(hashtag_dict.keys())):
        if rev_hashtag_dict[i] != "#StopKavanaugh":
            lst.append((rights[i], divisive[i], counts[i], rev_hashtag_dict[i], ideology[i]))
    return lst

summ_two = summarize_two()
rights1 = [x[0] for x in summ_two]
divisive1 = [x[1] for x in summ_two]
counts1 = [x[2] for x in summ_two]
names1 = [x[3] for x in summ_two]
ideology1 = [x[4] for x in summ_two]

def ideology_to_color(ideology):
    lst = []
    for i in ideology:
        if i > 0:
            lst.append((255*(1-i), 0, 255))
        else:
            lst.append((255, 0, 255*(1+i)))
    retLst = ['rgb' + str(x) for x in lst]
    return retLst

trace2 = go.Scatter(
    x=rights1,
    y=divisive1,
    text=names1,
    mode='markers',
    marker=dict(
        #color = ideology_to_color(ideology1),
        color = ideology1,
        size=counts1,
        colorscale='Bluered',
        reversescale=True,
        colorbar=dict(
            thickness=5,
            title='Polarity (Pro-Life to Pro-Choice)',
            xanchor='left',
            titleside='right'
        ),
    )
)

layout = go.Layout(
    title='Women\'s Rights vs Divisiveness',
    xaxis=dict(
        title='Women\'s Rights (Fraction of Tweets using Hashtag)',
    ),
    yaxis=dict(
        title='Divisiveness (Fraction of Tweets using Hashtag)',
    ),
)

data = [trace2]
fig = go.Figure(data=data, layout=layout)

py.iplot(fig, filename='bubblechart-text2')

def summarize_two():
    lst = []
    for i in range(0, len(hashtag_dict.keys())):
        if rev_hashtag_dict[i] != "#StopKavanaugh":
            lst.append((rights[i], divisive[i], counts[i], rev_hashtag_dict[i], ideology[i]))
    return lst

summ_two = summarize_two()
rights1 = [x[0] for x in summ_two]
divisive1 = [x[1] for x in summ_two]
counts1 = [x[2] for x in summ_two]
names1 = [x[3] for x in summ_two]
ideology1 = [x[4] for x in summ_two]

def rights_to_color():
    lst = []
    for i in rights1:
        if i < 0.2:
            lst.append((255,204,255))
        elif i < 0.4:
            lst.append((255, 153, 255))
        elif i < 0.6:
            lst.append((255, 51, 200))
        elif i < 0.8:
            lst.append((255, 40, 175))
        else:
            lst.append((255,20,147))
    retLst = ['rgb' + str(x) for x in lst]
    return retLst

trace3 = go.Scatter(
    x=ideology1,
    y=divisive1,
    text=names1,
    mode='markers',
    marker=dict(
#         color = rights_to_color(),
        color = rights1,
        size=counts1,
        colorscale='YlGnBu',
        reversescale=True,
        colorbar=dict(
            thickness=5,
            title='Intensity (Women\'s Rights)',
            xanchor='left',
            titleside='right'
        ),
    )
)

layout3 = go.Layout(
    title='Women\'s Rights vs Ideology vs Divisiveness',
    xaxis=dict(
        title='Ideology',
    ),
    yaxis=dict(
        title='Divisiveness (Fraction of Tweets using Hashtag)',
    ),
)

data = [trace3]
fig = go.Figure(data=data, layout=layout3)
py.iplot(fig, filename='bubblechart-text3')
