import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import GRU
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Lambda
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Permute
from tensorflow.keras.layers import ReLU
from tensorflow.keras.layers import Reshape
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adadelta

def ctc_loss(args):
    return K.ctc_batch_cost(*args)

def ctc_decode(softmax):
    return K.ctc_decode(softmax,K.tle([K.shape(softmax)[1]],[K.shape(softmax)[0]]))[0][0]

def char_decode(label_encode):
    return [''.join([idx_map[column] for column in row]) for row in label_encode]

labels_input = Input([None], dtype='int32')


def ocr_model(input_class):
    sequential = Sequential([
        Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same', input_shape=[60, None, 3]),
        Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same'),
        Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same'),
        Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same'),
        Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same'),
        MaxPooling2D(pool_size=(2, 1)),
        Permute((2, 1, 3)),
        TimeDistributed(Flatten()),
        Bidirectional(GRU(128, return_sequences=True)),
        Bidirectional(GRU(128, return_sequences=True)),
        TimeDistributed(Dense(len(input_class) + 1, activation='softmax'))
    ])
    return sequential
    # input_length = Lambda(lambda x: K.tile([[K.shape(x)[1]]], [K.shape(x)[0], 1]))(sequential.output)
    # label_length = Lambda(lambda x: K.tile([[K.shape(x)[1]]], [K.shape(x)[0], 1]))(labels_input)
    # output = Lambda(ctc_loss)([labels_input, sequential.output, input_length, label_length])
    # fit_model = Model(inputs=[sequential.input, labels_input], outputs=output)
    # ctc_decode_output = Lambda(ctc_decode)(sequential.output)
    # model = Model(inputs=sequential.input, outputs=ctc_decode_output)
    # adadelta = Adadelta(lr=0.05)
    # fit_model.compile(
    #     loss=lambda y_true, y_pred: y_pred,
    #     optimizer=adadelta)
    # fit_model.summary()

import os
import numpy as np
import cv2
def generator(train_txt,BATCH_SIZE):
    train_txt = '/home/abner/dnn/project/mxnet/OCR/dataset/jzx_train.txt'
    train_reader = open(train_txt,'r')
    train_dataset = train_reader.readlines()
    print(train_dataset)
    while True:
        # images = os.listdir(img_path)
        X = []
        Y = []
        a = (np.arange(1, len(train_dataset)))
        for i in range(BATCH_SIZE):

            index = np.random.choice(a)
            img_path, label = train_dataset[index].strip().split(" ")
            print(img_path, label)
            img = cv2.imread(img_path)
            img = cv2.resize(img,(32,128))
            img = np.array(img).reshape(32, 128, 3)
            X.append(img)
            Y.append(label)
        # break
        yield X,Y
generator("",3)

def ctc_lambda_func(args):
    y_pred, labels, input_length, label_length = args
    return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

#
# loss = Lambda(ctc_lambda_func, output_shape=(1, ), name='ctc')\
#     ([dense, label_true, input_length, label_length])

def main():
    model = ocr_model(26)

    model.compile(loss={'ctc':lambda y_true,y_pred:y_pred_},optimizer='adadelta')

    model.fit(generator("",5),steps_per_epoch=600, batch_size=1, epochs=100,
                            verbose=2)
    model.save("my_ocr.h5")
