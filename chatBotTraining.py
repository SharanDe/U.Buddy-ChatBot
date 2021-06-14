#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


with open('intents.json', encoding="utf8") as json_data:
    intents = json.load(json_data)


# In[3]:


def preprocessCreateAndTrain(intentsJson, modelName):
    words = []
    classes = []
    documents = []
    specialCharacters = ['?','/','-']
    for intent in intentsJson:
        for pattern in intent['patterns']:
            listOfWords = nltk.word_tokenize(pattern)
            words.extend(listOfWords)
            documents.append((listOfWords, intent['tag'].replace(' ', '_')))
            if intent['tag'].replace(' ', '_') not in classes:
                classes.append(intent['tag'].replace(' ', '_'))
                    
    words = [stemmer.stem(w.lower()) for w in words if w not in specialCharacters]
    words = sorted(list(set(words)))

    classes = sorted(list(set(classes)))
    
    training = []
    output = []

    emptyArray = [0] * len(classes)

    for doc in documents:
        bagOfWords = []
        pattern = doc[0]
        pattern = [stemmer.stem(word.lower()) for word in pattern]
    
        for word in words:
            bagOfWords.append(1) if word in pattern else bagOfWords.append(0)

        output_row = list(emptyArray)
        output_row[classes.index(doc[1])] = 1

        training.append([bagOfWords, output_row])

    random.shuffle(training)
    training = np.array(training)
    
    train_x = list(training[:,0])
    train_y = list(training[:,1])
    
    ops.reset_default_graph()
    
    with open('trainedModelsMetaData.json', 'r') as metaData:
        modelMetaData = json.load(metaData)
        
    modelMetaData[modelName] = {
        'inputNodeSize': len(train_x[0]),
        'outputNodeSize' : len(train_y[0])
    }
    
    with open('trainedModelsMetaData.json', 'w') as metaData:
        metaData.write(json.dumps(modelMetaData, indent=4))

    neuralNetwork = tflearn.input_data(shape=[None, len(train_x[0])])
    neuralNetwork = tflearn.fully_connected(neuralNetwork, 10)
    neuralNetwork = tflearn.fully_connected(neuralNetwork, 10)
    neuralNetwork = tflearn.fully_connected(neuralNetwork, len(train_y[0]), activation='softmax')
    neuralNetwork = tflearn.regression(neuralNetwork)

    model = tflearn.DNN(neuralNetwork, tensorboard_dir='tflearn_logs')

    model.fit(train_x, train_y, n_epoch=750, batch_size=8, show_metric=True)
    model.save('trainedModels/' + modelName + '.tflearn')
    pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "pickleFiles/training_data" + '_' + modelName, "wb" ) )


# In[4]:


def trainWithEachIteration(intentArray, modelName="mainModel"):
    print('Training ==> for model', modelName)
    preprocessCreateAndTrain(intentArray, modelName)
    for intent in intentArray:
        if type(intent['responses'][0]) != str:
            trainWithEachIteration(intent['responses'], modelName + '_' + intent['tag'].replace(' ','_'))


# In[6]:


if __name__ == '__main__':
    trainWithEachIteration(intents['intents'], "mainModel")






