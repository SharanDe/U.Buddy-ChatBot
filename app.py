#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ChatBot
from flask import *


# In[2]:


app = Flask(__name__)

@app.route('/')
def main():
    return render_template('ChatBot.html')

@app.route('/getResponse')
def getResponse():
    message = request.args.get('msg')
    response = ChatBot.predictWithIterations("mainModel", message, ChatBot.intents['intents'])
    return response

if __name__ == '__main__':
    app.run()


# In[ ]:




