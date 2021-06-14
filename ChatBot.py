#!/usr/bin/env python
# coding: utf-8

# In[174]:


# Libraries needed for NLP
import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# Libraries needed for Tensorflow processing
import tensorflow as tf
from tensorflow.python.framework import ops
import numpy as np
import tflearn
import random
import json
import pickle


# In[175]:


with open('intents.json', encoding='utf8') as json_data:
    intents = json.load(json_data)
    


# In[176]:


ERROR_THRESHOLD = 0.30


# In[177]:


def tokenizeAndStem(sentence):
    words = nltk.word_tokenize(sentence)
    words = [stemmer.stem(word.lower()) for word in words]
    return words


# In[178]:


def generateBagOfWords(sentence, words, show_details=False):
    tokenizedWords = tokenizeAndStem(sentence)
    bagOfWords = [0]*len(words)  
    for word in tokenizedWords:
        for index,wordAfterEnumeration in enumerate(words):
            if wordAfterEnumeration == word: 
                bagOfWords[index] = 1
                if show_details:
                    print ("found in bag: ", bagOfWords)
    return(np.array(bagOfWords))


# In[179]:


def predictForSingleModel(modelName, sentence, intentsJson):
    with open('trainedModelsMetaData.json', 'r') as metaData:
        modelsMetaData = json.load(metaData)
    
    inputNodeSize = modelsMetaData[modelName]['inputNodeSize']
    outputNodeSize = modelsMetaData[modelName]['outputNodeSize']
    
    ops.reset_default_graph()
    
    neuralNetwork = tflearn.input_data(shape=[None, inputNodeSize])
    neuralNetwork = tflearn.fully_connected(neuralNetwork, 10)
    neuralNetwork = tflearn.fully_connected(neuralNetwork, 10)
    neuralNetwork = tflearn.fully_connected(neuralNetwork, outputNodeSize, activation='softmax')
    neuralNetwork = tflearn.regression(neuralNetwork)
    
    model = tflearn.DNN(neuralNetwork, tensorboard_dir='tflearn_logs')
    model.load('./trainedModels/' + modelName + '.tflearn')
    data = pickle.load( open( "./pickleFiles/training_data" + "_" + modelName, "rb" ) )
    words = data['words']
    classes = data['classes']
    train_x = data['train_x']
    train_y = data['train_y']
    
    predictionResults = model.predict([generateBagOfWords(sentence, words)])[0]
    # filter out predictions below a threshold
    predictionResults = [[index,result] for index,result in enumerate(predictionResults) if result>ERROR_THRESHOLD]
    # sort by strength of probability
    predictionResults.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for result in predictionResults:
        return_list.append((classes[result[0]], result[1]))
    return return_list


# In[180]:


def responseFromPredictionUsingSingleModel(modelName, sentence, intentArray):
    results = predictForSingleModel(modelName, sentence, intentArray)
    if results:
        while results:
            for intent in intentArray:
                if intent['tag'].replace(' ', '_') == results[0][0]:
                    response = {}
                    response['tag'] = intent['tag'].replace(' ', '_')
                    response['responses'] = intent['responses']
                    if 'links' in intent:
                        response['links'] = intent['links']
                    return response
            results.pop(0)


# In[181]:


def predictWithIterations(modelName, sentence, intentArray):
    response = responseFromPredictionUsingSingleModel(modelName, sentence, intentArray)
    if type(response['responses'][0]) != str:
        return predictWithIterations(modelName + "_" + response['tag'], sentence, response['responses'])
    else:
        finalResponse = {}
        finalResponse['response'] = random.choice(response['responses'])
        if 'links' in response:
            finalResponse['links'] = response['links']
        return finalResponse

