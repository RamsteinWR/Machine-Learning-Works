# -*- coding: utf-8 -*-
"""DCNN for recognising digits .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zWbqAMlYQKindZdL5q1vq8O3rIO4_8av
"""

!pip install pydrive
!pip install googledrivedownloader

import datetime
from __future__ import division, print_function
from keras import backend as K
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.datasets import mnist, cifar100
from keras.utils import np_utils
from keras.optimizers import SGD, RMSprop, Adam
from keras import regularizers
from keras.regularizers import l1, l2, l1_l2
import os
import numpy as np
import matplotlib.pyplot as plt

'''for saving the model'''
from keras.models import load_model
from keras.models import model_from_json

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from google.colab import auth
from oauth2client.client import GoogleCredentials
'''for checkpointing'''
from keras.callbacks import ModelCheckpoint
# network and training
'''cifar 100 is a dataset of '''
NB_EPOCH = 50
BATCH_SIZE = 128
VERBOSE = 1
OPTIMIZER = Adam(lr=10**-3, decay=1e-7, epsilon=1e-6)
VALIDATION_SPLIT = 0.2
DROPOUT = 0.3
# IMG_ROWS, IMG_COLS = 32, 32  # input image dimensions
# IMG_CHANNELS = 3
INPUT_SHAPE = (32, 32, 3)

'''loading of the data and defining the no of classes'''
NB_CLASSES = 100 # number of outputs = number of digits
(X_train, y_train), (X_test, y_test) = cifar100.load_data()
print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
print('train samples: '+ str(X_train.shape[0]))
print('test samples: '+ str(X_test.shape[0]))

# K.set_image_dim_ordering("tf")  # consider them as float and normalize
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255
# we need a 60K x [1 x 28 x 28] shape as input to the CONVNET
# we need a 60K x [1 x 28 x 28] shape as input to the CONVNET
# X_train = X_train[:, np.newaxis, :, :]
# X_test = X_test[:, np.newaxis, :, :]
X_train = X_train.reshape(-1, 32, 32, 3)
X_test = X_test.reshape(-1, 32, 32, 3)

# convert class vectors to binary class matrices
y_train = np_utils.to_categorical(y_train, NB_CLASSES)
y_test = np_utils.to_categorical(y_test, NB_CLASSES)
# initialize the optimizer and model




'''network'''
model = Sequential()
model.add(Conv2D(32, (3,3), padding='same', input_shape=INPUT_SHAPE, kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.add(Activation('relu'))
model.add(Conv2D(32, (3,3), padding='same', activation='relu', kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(DROPOUT))

model.add(Conv2D(64, (3,3), padding='same', activation='relu', kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.add(Conv2D(64, (3,3), activation='relu', kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(DROPOUT))

model.add(Flatten())
model.add(Dense(512, activation='relu', kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.add(Dropout(DROPOUT))

model.add(Dense(NB_CLASSES, activation='softmax', kernel_regularizer=regularizers.l1_l2(0.01, 0.02)))
model.summary()


model.compile(loss="categorical_crossentropy", optimizer=OPTIMIZER, metrics=["accuracy"])

MODEL_DIR = "sample_data/"
'''save the best model'''
checkpoint = ModelCheckpoint(filepath=os.path.join(MODEL_DIR, f"model:{datetime.datetime.now():%Y-%m-%d-%Hh%Mm%Ss}"))



history = model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,
                    validation_split=VALIDATION_SPLIT, callbacks=[checkpoint])




# while((history.history.get('acc')[-1] <99.0 and history.history.get('val_acc')[-1] <99.0) and (history.history.get('loss')[-1] >0.02 and history.history.get('val_loss')[-1] >0.02)):
#     history = model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,
#                         validation_split=VALIDATION_SPLIT, callbacks=[checkpoint])

print("acc: "+ str(history.history.get('acc')[-1]))
print("loss: "+ str(history.history.get('loss')[-1]))
print("val_acc: "+ str(history.history.get('val_acc')[-1]))
print("val_loss: "+ str(history.history.get('val_loss')[-1]))

score = model.evaluate(X_test, y_test, verbose=VERBOSE)
print("Test score:", score[0])
print('Test accuracy:', score[1])

'''1 . authenticate and create a pydrive client'''
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

'''2. save keras model and weights on the google drive'''

# create on colab directory
date = datetime.datetime.now()
model.save(f"M:{date:%Y-%m-%d-%Hh%Mm%Ss}")
model_file = drive.CreateFile({"title": f"M:{date:%Y-%m-%d-%Hh%Mm%Ss}"})
model_file.SetContentFile(f"M:{date:%Y-%m-%d-%Hh%Mm%Ss}")
model_file.Upload()

print(model_file.get('id'))


'''4.  reload weights from google drive into the model'''
# use get shareable link to get file id or get() method
last_weight_file = drive.CreateFile({'id': model_file.get('id')})
last_weight_file.GetContentFile(f'weights_reloaded:{date:%Y-%m-%d-%Hh%Mm%Ss}.mat')
model.load_weights(f'weights_reloaded:{date:%Y-%m-%d-%Hh%Mm%Ss}.mat')


score = model.evaluate(X_test, y_test, verbose=VERBOSE)
print("Test score:", score[0])
print('Test accuracy:', score[1])
# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()