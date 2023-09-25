# # TRAINING

# In[1]:


import random
import numpy as np
import pickle
import json
import nltk
from nltk.stem import WordNetLemmatizer


# In[2]:


intents_path = "./data/intents.json"
words_path = "./model/words.pkl"
classes_path = "./model/classes.pkl"
weights_path = "./model/weights.pkl"
biases_path = "./model/biases.pkl"


# In[3]:


lemmatizer = WordNetLemmatizer()
nltk.download('omw-1.4')
nltk.download("punkt")
nltk.download("wordnet")


# In[4]:


words = []
classes = []
documents = []
ignore_words = ["?", "!"]
data_file = open(intents_path).read()
intents = json.loads(data_file)


# ## run this if you have normal intents.json

# In[ ]:


#for intent in intents["intents"]:
#    for pattern in intent["patterns"]:
#       w = nltk.word_tokenize(pattern)
#        words.extend(w)
#        documents.append((w, intent["tag"]))
#        if intent["tag"] not in classes:
#            classes.append(intent["tag"])


# ## i made intents.json in libreoffice calc so i needed to modify like below

# In[14]:


for i in range(len(intents)):
    intent = intents[i]["intents"]
    for pattern in intent["patterns"]:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])


# In[15]:


words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))
pickle.dump(words, open(words_path, "wb"))
pickle.dump(classes, open(classes_path, "wb"))


# In[16]:


training = []
output_empty = [0] * len(classes)
for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training,dtype=object)
train_x = list(training[:, 0])
train_y = list(training[:, 1])


# In[17]:


weights = np.random.rand(len(train_x[0]), len(classes))
biases = np.zeros(len(classes))
epochs = 200
for i in range(epochs):
    for x, y in zip(train_x, train_y):
        x = np.array(x)
        layer = np.dot(x, weights) + biases
        layer = np.maximum(layer, 0)
        layer_error = layer - y
        layer_delta = layer_error
        weights_delta = np.dot(x[:, None], layer_delta[None, :])
        biases_delta = layer_delta
        weights -= 0.01 * weights_delta
        biases -= 0.01 * biases_delta

pickle.dump(weights, open(weights_path, "wb"))
pickle.dump(biases, open(biases_path, "wb"))
