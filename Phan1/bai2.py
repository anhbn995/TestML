import tensorflow as tf

size_model = 128
size_model = 128
num_chanel = 3

inputs = tf.keras.layers.Input((size_model, size_model, num_chanel))

layer1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu',strides =(1,1), kernel_initializer='he_normal')(inputs)
layer1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal',padding = 'same')(layer1)
layer1 = tf.keras.layers.BatchNormalization()(layer1)
maxpool1 = tf.keras.layers.MaxPooling2D((2, 2))(layer1)
layer1 = tf.keras.layers.Dropout(0.1)(maxpool1)
layer2 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu',strides = (1,1), kernel_initializer='he_normal')(layer1)
layer2 = tf.keras.layers.BatchNormalization()(layer2)
maxpool2 = tf.keras.layers.MaxPooling2D((2, 2))(layer2)
layer2 = tf.keras.layers.Dropout(0.1)(maxpool2)

layer3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu',strides = (1,1), kernel_initializer='he_normal')(layer2)
layer3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal')(layer2)
layer3 = tf.keras.layers.BatchNormalization()(layer3)
maxpool3 = tf.keras.layers.MaxPooling2D((2, 2))(layer3)
layer3 = tf.keras.layers.Dropout(0.1)(maxpool3)


flaten = tf.keras.layers.Flatten()(layer3)
layer_out = tf.keras.layers.Dense(512,activation='relu')(flaten)
layer_out = tf.keras.layers.BatchNormalization()(layer_out)
layer_out = tf.keras.layers.Dropout(0.1)(layer_out)

outputs = tf.keras.layers.Dense(2,activation='softmax')(layer_out)

 
model = tf.keras.Model(inputs=[inputs], outputs=[outputs])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()