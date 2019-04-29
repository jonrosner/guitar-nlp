from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import Adam
from keras.callbacks import LambdaCallback, ModelCheckpoint
from keras.layers import Dropout
from keras.regularizers import l2

import random
import numpy as np
import logging

from . import marshaller


class Model:
    def __init__(self, input_size, num_features, units, lr):
        self.input_size = input_size
        self.num_features = num_features
        self.units = units
        self.lr = lr

        self.model = Sequential()
        self.model.add(LSTM(self.units, input_shape=(
            self.input_size, self.num_features), return_sequences=True))
        self.model.add(Dropout(0.3))
        self.model.add(LSTM(self.units, return_sequences=True))
        self.model.add(Dropout(0.3))
        self.model.add(LSTM(self.units))
        self.model.add(Dropout(0.3))
        self.model.add(Dense(256))
        self.model.add(Dropout(0.3))
        self.model.add(Dense(self.num_features))
        self.model.add(Activation('softmax'))
        self.optimizer = Adam(lr=self.lr)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer=self.optimizer, metrics=['categorical_accuracy'])
        print(self.model.summary())

    def load(self, filepath):
        self.model.load_weights(filepath, by_name=True)

    def train(self, dataset, batch_size, epochs, filepath):
        self.dataset = dataset
        print("Starting training with dataset... x: {0}, y: {1}".format(
            dataset["X"].shape, dataset["Y"].shape)
        )
        checkpoint = ModelCheckpoint(filepath,
                                     monitor='loss',
                                     verbose=1,
                                     save_best_only=True,
                                     mode='min')
        self.model.fit(dataset["X"], dataset["Y"],
                       batch_size=batch_size, epochs=epochs,
                       verbose=2, callbacks=[checkpoint],
                       validation_split=0.0)

    def predict(self, x):
        preds = self.model.predict(x, verbose=0)[0]
        z = map(lambda y: (marshaller.int_to_note(
            y[0]), y[1]), enumerate(preds))
        print(sorted(z, key=lambda z1: z1[1])[-3:])
        return np.argmax(preds)

    def test(self, test_songs, length, num_features):
        correct = 0
        false = 0
        print(len(test_songs))
        for test_song in test_songs:
            one_hot_song = np.array(
                list(map(lambda x: marshaller.int_to_one_hot(x, num_features), test_song)))
            x = np.expand_dims(one_hot_song[:length], axis=0)
            generated = test_song[:length]
            l = min(10, len(test_song)-length)
            for _ in range(l):
                preds = self.model.predict(x, verbose=0)[0]
                next_note = np.argmax(preds)
                generated.append(next_note)
                next_note_one_hot = marshaller.int_to_one_hot(
                    next_note, num_features).reshape(1, -1)
                x = np.append(x[0][1:], next_note_one_hot, axis=0).reshape(
                    (1, length, num_features))
            current_correct = sum(
                [i == j for i, j in zip(test_song, generated)])
            correct += current_correct
            false += l + length - current_correct
            print("Generated:\n" + marshaller.unmarshall(generated))
            print("Actual:\n" + marshaller.unmarshall(test_song[0:20]))
        print("Accuracy: \t", (correct / (correct+false)))

    def generate_from_nothing(self, length, num_features, input_size):
        generated = []
        current_X = np.random.randint(1, num_features, input_size)
        for _ in range(length):
            X = np.expand_dims(marshaller.ints_to_onehots(
                current_X, num_features), axis=0)
            next_note = self.predict(X)
            generated.append(next_note)
            current_X = np.append(current_X[1:], next_note)
        print(marshaller.unmarshall(generated))
