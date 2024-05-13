import numpy as np

import tensorflow as tf
from tensorflow import keras

train_images_path = 'file1.txt'
train_labels_path = 'file1.txt'
number_input = 90


train_images = np.loadtxt(train_images_path, dtype=float)
train_labels = np.loadtxt(train_labels_path, dtype=int)

class_names = ['idle', 'left', 'right', 'up', 'down']

print(np.array(class_names).shape)

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(number_input, 1)),  # input layer (1)
    keras.layers.Dense(128, activation='relu'),  # hidden layer (2)
    keras.layers.Dense(len(class_names), activation='softmax') # output layer (3)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_images, train_labels, epochs=10)

# test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=1) 
# print('Test accuracy:', test_acc)

# predictions = model.predict(test_images)

# print('Prediction: ', class_names[np.argmax(predictions[0])])

model.save_model('trained_model.keras')