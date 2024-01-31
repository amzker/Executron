#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

mapping_filename = os.path.join(data_dir, "mappings.csv")
classes_file = os.path.join(config_dir, "classes.txt")
word_index_file = os.path.join(config_dir, "word_to_index.json")
max_tokens_file = os.path.join(config_dir, "max_input")
model_path = os.path.join(model_dir, "model_dict.json")

def load_word_to_index(filename):
    with open(filename, 'r') as json_file:
        word_to_index = json.load(json_file)
    return word_to_index

def load_max_input_size(filename):
    with open(filename, 'r') as file:
        max_input_size = int(file.read())
    return max_input_size

def preprocess_data(raw_text, word_to_index, max_input_size):
    input_tokens = [word_to_index.get(word, 0) for word in word_tokenize(raw_text.lower())]

    # Pad or truncate input tokens to match the model's input size
    input_tokens = input_tokens[:max_input_size] + [0] * (max_input_size - len(input_tokens))

    return np.array([input_tokens])

def make_predictions(input_tokens, model):
    predicted_output = model.predict(input_tokens)
    return np.round(predicted_output)

def nmpredict(raw_text, word_to_index, model, max_input_size):
    input_tokens = preprocess_data(raw_text, word_to_index, max_input_size)
    predictions = make_predictions(input_tokens, model)
    mappings = pd.read_csv(mapping_filename)
    mapping_dict = mappings.set_index("mapping")["commands"].to_dict()
    predicted_commands = [",".join([mapping_dict[pred] for pred in prediction if pred in mapping_dict]) for prediction in predictions]
    return predicted_commands

word_to_index = load_word_to_index(word_index_file)
max_input_size = load_max_input_size(max_tokens_file)


# In[ ]:


class POLY2:

    def __init__(self):
        self.beta = None
        self.c = None
        self.degree = None
        self.mean = None
        self.std = None
        self.mse = []
        self.betas = []
        self.itr = []

    def polyrise(self, X, degree, interactions=False):
        newx = np.asarray(X)

        if newx.ndim == 1:
            newx = newx.reshape(-1, 1)
        X_poly = newx.copy()

        for i in range(2, degree + 1):
            X_poly = np.append(X_poly, newx ** i, axis=1)

        return X_poly

    def normalize(self, X):
        smallvalue = 1e-10

        X = (X - self.mean) / (self.std + smallvalue)
        return X

    def fit(self, X, y, lr=0.01, epochs=100, degree=1, interactions=False, alpha=0.01):
        self.degree = degree

        X_poly = self.polyrise(X, degree, interactions)
        y = np.asarray(y)
        if y.ndim == 1:
            y = y.reshape(-1, 1)

        n_samples, n_features = X_poly.shape
        n_outputs = y.shape[1]
        self.beta = np.zeros((n_features, n_outputs))
        self.c = np.zeros(n_outputs)
        self.mean = np.mean(X_poly, axis=0)
        self.std = np.std(X_poly, axis=0)
        X_norm = self.normalize(X_poly)

        for i in range(epochs):
            self.itr.append(i)
            pred = X_norm.dot(self.beta) + self.c
            error = y - pred
            self.betas.append(self.beta)

            self.mse.append(np.mean(np.absolute(error)))

            # ∂β = −2/n Σ X.T(y−βX) +  α∗sign(β)

            db = -2 / len(X_norm) * X_norm.T.dot(error)
            lasso = alpha * np.sign(self.beta)
            db = db + lasso

            dc = (-2) * np.mean(error, axis=0)
            self.beta = self.beta - (lr * db)
            self.c = self.c - (lr * dc)
        print("LAST MSE: ", np.mean(np.absolute(self.mse[-1])))
        return self

    def predict(self, X):
        if self.beta is None or self.c is None:
            raise RuntimeError("Model has not been trained. Please call model.fit() before model.predict().")
        X_poly = self.polyrise(X, self.degree, interactions=False)  # Ensure interactions are disabled
        X_norm = self.normalize(X_poly)
        return X_norm.dot(self.beta) + self.c

    def evaluate(self, X, y_actual):
        if self.beta is None or self.c is None:
            raise RuntimeError("Model has not been trained. Please call model.fit() before model.evaluate().")

        X = X.to_numpy()

        X_poly = self.polyrise(X, self.degree, interactions=False)
        X_norm = self.normalize(X_poly)

        y_pred = X_norm.dot(self.beta) + self.c

        y_actual = np.squeeze(y_actual)
        y_pred = np.squeeze(y_pred)

        correct_predictions = np.sum(np.round(y_pred) == y_actual)
        incorrect_predictions = len(y_actual) - correct_predictions

        accuracy = correct_predictions / len(y_actual)

        # i can use pandas to make beautiful tablke but i dont have energy anymore
        print("Total Samples:", len(y_actual))
        print("Correct Predictions:") 
        print(correct_predictions)
        print("Incorrect Predictions:") 
        print(incorrect_predictions)
        print("Accuracy:")
        print(accuracy)
    
    def to_dict(self):
        return {
            'beta': self.beta.tolist() if self.beta is not None else None,
            'c': self.c.tolist() if self.c is not None else None,
            'degree': self.degree,
            'mean': self.mean.tolist() if self.mean is not None else None,
            'std': self.std.tolist() if self.std is not None else None,
            'mse': self.mse,
            'betas': [beta.tolist() for beta in self.betas] if self.betas else None,
            'itr': self.itr
        }

    def from_dict(self, model_dict):
        self.beta = np.array(model_dict['beta']) if model_dict['beta'] is not None else None
        self.c = np.array(model_dict['c']) if model_dict['c'] is not None else None
        self.degree = model_dict['degree']
        self.mean = np.array(model_dict['mean']) if model_dict['mean'] is not None else None
        self.std = np.array(model_dict['std']) if model_dict['std'] is not None else None
        self.mse = model_dict['mse']
        self.betas = [np.array(beta) for beta in model_dict['betas']] if model_dict['betas'] else None
        self.itr = model_dict['itr']


# In[ ]:


with open(model_path, 'r') as file:
    loaded_model_dict = json.load(file)

model = POLY2()
model.from_dict(loaded_model_dict)
print("MODEL CONFIGURAION LOADED")


# In[ ]:


def classify(input_sentence):
    predictions = nmpredict(input_sentence,word_to_index, model, max_input_size)
    return predictions

