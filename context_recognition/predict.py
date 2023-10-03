#!/usr/bin/env python
# coding: utf-8

# # PREDICTING

# In[18]:


import random
import numpy as np
import pickle
import json
import nltk
from nltk.stem import WordNetLemmatizer
import os 
# In[19]:


lemmatizer = WordNetLemmatizer()
nltk.download('omw-1.4')
nltk.download("punkt")
nltk.download("wordnet")


# In[21]:

model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
words_path = os.path.join(model_dir, "words.pkl")
classes_path = os.path.join(model_dir, "classes.pkl")
weights_path = os.path.join(model_dir, "weights.pkl")
biases_path = os.path.join(model_dir, "biases.pkl")



# In[22]:


words = pickle.load(open(words_path, "rb"))
classes = pickle.load(open(classes_path, "rb"))
weights = pickle.load(open(weights_path, "rb"))
biases = pickle.load(open(biases_path, "rb"))


# In[23]:


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict(inputs, weights, biases):
    layer = np.dot(inputs, weights) + biases
    layer = np.maximum(layer, 0)
    return layer

def classify(input_sentence):
    inputs = bow(input_sentence, words)
    predicted_output = predict(inputs, weights, biases)
    predicted_class_index = np.argmax(predicted_output)
    predicted_class = classes[predicted_class_index]
    return predicted_class


# In[31]:
def main():
    while True:
        useri = input("user: ")
        if useri == "bye":
            break
        print(classify(useri))

if __name__ == "__main__":
    main()
