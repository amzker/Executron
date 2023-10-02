import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np
import random
import os
import pickle

data = pd.read_csv("data/text_class.csv")

model_dir =  "model"
words_path = os.path.join(model_dir,"words.pkl")
classes_path = os.path.join(model_dir, "classes.pkl")
weights_path = os.path.join(model_dir, "weights.pkl")
biases_path = os.path.join(model_dir, "biases.pkl")


lemmatizer = WordNetLemmatizer()
nltk.download("punkt")

words = []
classes = []
documents = []
ignore_words = ["?", "!"]


for col_name, values in data.iloc[:, :].iteritems():
    for value in values:
        if isinstance(value, str):
            words.extend(word_tokenize(value))
            documents.append((word_tokenize(value), col_name))
            if col_name not in classes:
                classes.append(col_name)

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))


pickle.dump(words, open(words_path, "wb"))
pickle.dump(classes, open(classes_path, "wb"))

# Prepare training data
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
training = np.array(training, dtype=object)
train_x = list(training[:, 0])
train_y = list(training[:, 1])

# Define weights and biases
weights = np.random.rand(len(train_x[0]), len(classes))
biases = np.zeros(len(classes))
epochs = 200

# Training loop
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

# Save the weights and biases
pickle.dump(weights, open(weights_path, "wb"))
pickle.dump(biases, open(biases_path, "wb"))
