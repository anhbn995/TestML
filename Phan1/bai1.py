from keras.models import Model
from keras.layers import Input, Dense
import tensorflow as tf

input_ = Input(shape = (16,))
dense_1 = Dense(8)(input_)
dense_2 = Dense(8,activation=tf.nn.relu)(dense_1)
dense_3 = Dense(8,activation=tf.nn.relu)(dense_2)
dense_4 = Dense(4,activation=tf.nn.relu)(dense_3)
output = Dense(1,activation=tf.nn.sigmoid)(dense_4)

model = Model(inputs = input_, outputs= output)
model.summary()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-2), loss=tf.keras.losses.BinaryCrossentropy(),
              metrics=[tf.keras.metrics.BinaryAccuracy()])