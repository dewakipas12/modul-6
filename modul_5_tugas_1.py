# -*- coding: utf-8 -*-
"""Modul_5_tugas 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Dyw4RriPalIrK2wnST-RyC-5Cp2x1KgF
"""

import zipfile
import matplotlib.pyplot as plt
import urllib.request
import shutil
from sklearn.model_selection import train_test_split
import random
from tensorflow.keras.preprocessing.image import load_img
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import matplotlib.pyplot as plt
import cv2
import matplotlib.image as mpimg
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout, Input
from tensorflow.keras.applications import ResNet101
from tensorflow.keras.optimizers import Adam

from google.colab import drive
drive.mount('/content/drive', force_remount  = True)

# Ekstrak dataset
import os
import zipfile

img_zip = '/content/drive/MyDrive/dataset/rps.zip'

if not os.path.exists(img_zip):
    print(f"File {img_zip} tidak ditemukan.")
else:
    try:
        zip_ref = zipfile.ZipFile(img_zip, 'r')  # Membaca local path
        zip_ref.extractall('/dataset')  # Extract .zip file
        zip_ref.close()
        print("Ekstraksi berhasil.")
    except zipfile.BadZipFile:
        print(f"File {img_zip} bukan file zip yang valid.")

base_dir = '/dataset/rps'

train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')
test_dir = os.path.join(base_dir, 'test')

os.makedirs(train_dir, exist_ok = True)
os.makedirs(val_dir, exist_ok = True)
os.makedirs(test_dir, exist_ok = True)

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split = 0.3
)

train_generator = train_datagen.flow_from_directory(
    r"/dataset/rps",
    target_size = (150,150),
    class_mode  = 'categorical',
    subset = 'training'
)

validation_generator = train_datagen.flow_from_directory(
    r"/dataset/rps",
    target_size = (150,150),
    class_mode  = 'categorical',
    subset = 'validation'
)

class_labels = list(train_generator.class_indices.keys())

# Tampilkan 1 gambar dari setiap kelas
for label in class_labels:
    img = plt.imread(train_generator.filepaths[np.argmax(train_generator.labels == class_labels.index(label))])
    plt.imshow(img)
    plt.title(label)
    plt.show()

#  load model ResNet101,  memotong bagian Top atau Fully Connected Layernya
baseModel = ResNet101(
                      weights="imagenet",  # Load weights pre-trained on ImageNet.
                      input_tensor=Input(shape=(150, 150, 3)), # Set Input Model dengan shape yang sesuai dengan ukuran citra
                      include_top=False,
                      )

# Model Summary
baseModel.summary()

# Freeze the baseModel karena sudah dilakukan training
baseModel.trainable = False

# Creating Fully Connected
x = baseModel.output
x = Flatten()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.2)(x)  # Regularize with dropout
outputs = Dense(1, activation = 'sigmoid')(x)
model = Model(inputs = baseModel.input, outputs = outputs)

# Model Summary
model.summary()

# Complie Model


model.compile(Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# training Transfer Learning Model ResNet101
history = model.fit(
    train_generator,
    epochs = 10,
    validation_data = validation_generator,
)

# Visualization Accuracy, Val Accuracy, Loss and Val Loss
import matplotlib.pyplot as plt
accuracy = history.history['accuracy']
val_accuracy = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs_range = range(len(accuracy))

plt.figure(figsize=(13, 5))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, accuracy, label='Training Accuracy')
plt.plot(epochs_range, val_accuracy, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Akurasi')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Loss')
plt.show()

# Printout Accuracy and Loss
loss, accuracy = model.evaluate_generator(validation_generator)
print("Validation: \nAccuracy = %f  \nLoss = %f " % (accuracy, loss))

# Showing Classification Report
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# Predictting Model
y_pred =  model.predict_generator(validation_generator)
y_pred = np.argmax(y_pred, axis=1)
target_names = ['paper', 'rock', 'scrissors']

#Classification Report
print('Classification Report')
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

random_indices = np.random.choice(len(validation_generator.filenames), size=10, replace=False)
random_images = [validation_generator.filepaths[i] for i in random_indices]
random_labels = [class_labels[y_pred[i]] for i in random_indices]

# Tampilkan gambar dan lakukan predict
for img_path, true_label in zip(random_images, random_labels):
    img = plt.imread(img_path)
    plt.imshow(img)
    plt.title(f'True Label: {true_label}')

    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(150, 150))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)
    predicted_label = class_labels[np.argmax(prediction)]
    confidence = np.max(prediction)

    plt.xlabel(f'Predicted Label: {predicted_label} (Confidence: {confidence:.2f})')
    plt.show()