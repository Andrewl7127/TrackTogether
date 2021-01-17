#!/usr/bin/env python
# coding: utf-8

# In[4]:


import speech_recognition as sr
import pyttsx3
import zipcodes
import pandas as pd
from twilio.rest import Client
from datetime import datetime, timedelta, date
import nltk
from nltk.stem import WordNetLemmatizer
import json
import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import requests

new = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
new['date'] = pd.to_datetime(new['date'])
last_day = new['date'].max().date()
day_before = last_day - timedelta(days=1)
date2 = last_day.strftime("%Y-%m-%d")
pd.options.mode.chained_assignment = None
data = new[new['date'] == date2]
data.drop(columns = ['fips', 'date'], inplace = True)
data.set_index(['county', 'state'], inplace=True)
data2 = new[new['date'] == day_before.strftime("%Y-%m-%d")]
data2.drop(columns = ['fips', 'date'], inplace = True)
data2.set_index(['county', 'state'], inplace=True)
new_cases = data - data2
new_cases.reset_index(level=0, inplace=True)
new_cases.reset_index(level=0, inplace=True)
new_cases.reset_index(level=0, inplace=True, drop = True)
new_cases['county'] = new_cases['county'] + " County"

counties = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv')
counties['county'] = counties['county'] + " County"

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wiscbonsin': 'WI',
    'Wyoming': 'WY'
}

counties['state'] = counties['state'].map(us_state_abbrev)
new_cases['state'] = new_cases['state'].map(us_state_abbrev)

engine = pyttsx3.init()
engine.setProperty('rate', 125)

def say(message):
    engine.say(message)
    engine.runAndWait()

def talk(message):
    
    r = sr.Recognizer()

    with sr.Microphone() as source:
        say(message)
        audio_text = r.listen(source)

        try:
            print (r.recognize_google(audio_text))
            return r.recognize_google(audio_text)
            
        except:
            say("Sorry, I did not get that")
            talk(message)

def update():
    
    code = talk("What is your zip code?")
    
    try:
        x = zipcodes.matching(code)
        c = x[0]['county']
        s = x[0]['state']
        cases = int(new_cases[(new_cases['county'] == c) & (new_cases['state'] == s)].cases)
        deaths = int(new_cases[(new_cases['county'] == c) & (new_cases['state'] == s)].deaths)
        cases2 = int(counties[(counties['county'] == c) & (counties['state'] == s)].cases)
        deaths2 = int(counties[(counties['county'] == c) & (counties['state'] == s)].deaths)
        msg = "There have been " + str(cases) + " new cases and " + str(deaths) + " new deaths in " + c + " as of " + date
        msg += ". There have been " + str(cases2) + " total cases and " + str(deaths2) + " total deaths in " + c
        say(msg)

    except:
        say("Sorry, I did not get that")
        update()

def mobile():
    print ("hi")

def news():
    r = requests.get('https://www.reddit.com/r/Coronavirus/top/.json', headers = {'user-agent': 'Mozilla/5.0'})
    top_headers = []
    for i in range(10):
        post = r.json()['data']['children'][i]['data']['title']
        top_headers.append(post)
    say("Here are the top 5 COVID-19 headlines for" + str(date.today()))
    for i in top_headers:
        say(i + ".")

def question(): 

    lemmatizer = WordNetLemmatizer()

    import json
    import numpy as np
    import tflearn
    import tensorflow as tf
    import random
    import pickle
    import pandas as pd

    with open("intents.json") as file:
        data = json.load(file)

    try:
        with open("data1.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)
    except:
        words = []
        labels = []
        docs_x = []
        docs_y = []

        for intents in data['intents']:
            for pattern in intents['patterns']:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intents['tag'])

                if intents['tag'] not in labels:
                    labels.append(intents['tag'])

        words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in "?"]
        words = sorted(list(set(words)))
        labels = sorted(labels)

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x,doc in enumerate(docs_x):
            bags = []
            wrds = [lemmatizer.lemmatize(w) for w in doc]

            for w in words:
                if w in wrds:
                    bags.append(1)
                else:
                    bags.append(0)
            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1

            training.append(bags)
            output.append(output_row)

        training = np.array(training)
        output = np.array(output)
        with open("data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)


    tf.compat.v1.reset_default_graph() 

    nn = tflearn.input_data(shape = [None, len(training[0])])
    nn = tflearn.embedding(nn, input_dim=20000, output_dim=128, trainable=False, name="EmbeddingLayer")
    nn = tflearn.fully_connected(nn, 8)
    nn = tflearn.fully_connected(nn, 16)
    nn = tflearn.fully_connected(nn, len(output[0]), activation = "softmax")
    nn = tflearn.regression(nn)

    model = tflearn.DNN(nn)

    try:
        model.load("model.tflearn")
    except:
        model.fit(training, output, n_epoch = 1000, batch_size = 4, show_metric = True)
        model.save("model.tflearn")

    def bag_of_words(s, words):
        bag = [0 for _ in range(len(words))]

        s_words = nltk.word_tokenize(s)
        s_words = [lemmatizer.lemmatize(word.lower()) for word in s_words]

        for se in s_words:
            for i,w in enumerate(words):
                if w == se:
                    bag[i] = 1
        nparray = np.array(bag)
        return(nparray.reshape(-1,len(training[0])))

    def chat():

        say("Hi! My name is Avocado. Feel free to ask me any questions, and if you ever want to stop talking to me, say exit.")
        count = 0
        try:
            while True:
                if (count == 0):
                    inp = talk("What can I help you with today?")
                    count += 1
                else:
                    inp = talk("What else can I help you with today?")
                if "exit".find(inp.lower()) > -1:
                    say("It was nice talking to you! Goodbye!")
                    break
                results = model.predict(list(bag_of_words(inp, words)))[0]
                results_index = np.argmax(results)
                tag = labels[results_index]
                if results[results_index] > 0.5:
                    for tg in data["intents"]:
                        if tg['tag'] == tag:
                            responses = tg['responses']
                    say(random.choice(responses))
                else:
                    say("I didn't quite get that, please try again or ask a different question.")
        except:
            say("I'm sorry. I couldn't hear you. Please try again.")

    chat()

def main():

    say("Welcome to our app! Say update for an update on COVID-19 cases near you! " + 
        "Say news for the top 5 COVID-19 headlines Say mobile to get updates to your mobile phone! " 
        + "Say question to ask questions to our chat bot! If at any point you would like to stop talking say exit!" 
        + " For a repeat of the options say options.")
    flag = False
    try:
        response = talk("How can I help you?").lower()
        while flag == False:
            if "exit".find(response) > -1:
                say("It was nice talking to you. Goodbye!")
                break
            else:
                if "options".find(response) > -1:
                    say("Here are your options.")
                else:
                    if "update".find(response) > -1:
                        update()
                    else:
                        if "news".find(response) > -1:
                            news()
                        else:
                            if "mobile".find(response) > -1:
                                mobile()
                            else:
                                if "question".find(response) > -1:
                                    question()          
            response = talk("What else can I help you with?").lower()
    except:
        say("I'm sorry. Please try again.")

main()


# In[ ]:


date.today()

