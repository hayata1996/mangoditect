# -*- coding: utf-8 -*-
"""
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m-13GHLYHLgy49F37Ah2F3anSAUs037R
"""

!pip install tensorflow==2.16.1

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, MaxPooling2D, Conv2D, Flatten
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.optimizers import Adam


# Data preparation
data_dir = '/content/drive/MyDrive/programm_sample/kagglemangodataset/archive'
batch_size = 16
img_size = (224, 224)

filepaths = []
labels = []
folds = os.listdir(data_dir)
for fold in folds:
    foldpath = os.path.join(data_dir, fold)
    filelist = os.listdir(foldpath)
    for file in filelist:
        filepaths.append(os.path.join(foldpath, file))
        labels.append(fold)

df = pd.DataFrame({'filepaths': filepaths, 'labels': labels})
train_df, test_df = train_test_split(df, test_size=0.2, random_state=123)
valid_df, test_df = train_test_split(test_df, test_size=0.5, random_state=123)

# ImageDataGenerator with preprocessing
tr_gen = ImageDataGenerator(preprocessing_function=preprocess_input)
ts_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_gen = tr_gen.flow_from_dataframe(train_df, x_col='filepaths', y_col='labels',
                                       target_size=img_size, class_mode='categorical',
                                       batch_size=batch_size, shuffle=True)
valid_gen = ts_gen.flow_from_dataframe(valid_df, x_col='filepaths', y_col='labels',
                                       target_size=img_size, class_mode='categorical',
                                       batch_size=batch_size)
test_gen = ts_gen.flow_from_dataframe(test_df, x_col='filepaths', y_col='labels',
                                      target_size=img_size, class_mode='categorical',
                                      batch_size=batch_size, shuffle=False)

# Model building
base_model = EfficientNetB0(include_top=False, weights="imagenet", input_shape=img_size + (3,))
base_model.trainable = False  # For fine-tuning, you can set this to True

input_shape = (224, 224, 3)  # 224x224 pixels and 3 channels (RGB)

# Define hyperparameters
learning_rate = 0.01
l1_factor = 0.006
l2_factor = 0.016

# Build the model
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())

# Add a dropout layer and a dense layer with L1/L2 regularization
model.add(Dropout(rate= 0.45, seed= 123))
model.add(Dense(512, activation='relu', kernel_regularizer=l1_l2(l1=l1_factor, l2=l2_factor)))

# Add the output layer
model.add(Dense(8, activation='softmax'))  # Assuming 8 classes for the classification

# Compile the model
model.compile(optimizer=Adam(learning_rate=learning_rate),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Display the model's architecture
model.summary()

# Training
#epochs = 10
epochs = 1
history = model.fit(train_gen, epochs=epochs, validation_data=valid_gen)

# Evaluation
test_loss, test_accuracy = model.evaluate(test_gen)
print(f"Test loss: {test_loss}")
print(f"Test accuracy: {test_accuracy}")

# Save model
model.save('mango_model.h5')

# Prediction and visualization in Streamlit app
# This part will go into your Streamlit app script
import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="Mango Leaf Disease Detection", page_icon=":mango:")

def import_and_predict(image_data, model):
    size = (224, 224)
    image = ImageOps.fit(image_data, size, Image.ANTIALIAS)
    img = np.asarray(image)
    img_reshape = img[np.newaxis,...]
    prediction = model.predict(img_reshape)
    return prediction

model = tf.keras.models.load_model('mango_model.h5')
class_names = list(train_gen.class_indices.keys())

st.write("# Mango Disease Detection with Remedy Suggestion")

file = st.file_uploader("", type=["jpg", "png"])
if file is not None:
    image = Image.open(file)
    st.image(image, use_column_width=True)
    predictions = import_and_predict(image, model)
    st.write(f"Detected Disease: {class_names[np.argmax(predictions)]}")
    st.write(f"Confidence: {np.max(predictions) * 100:.2f}%")
