import numpy as np

import tensorflow as tf
from tensorflow import keras

train_images_path = 'X_train.txt'
train_labels_path = 'y_train_gesture.txt'
gesture_list = ['idle', 'left', 'right', 'up', 'down']
frame_per_action = 15

train_images = np.loadtxt(train_images_path, dtype=float)
train_labels = np.loadtxt(train_labels_path, dtype=int)

train_images = np.reshape(train_images, (-1, frame_per_action, train_images.shape[1]))

# train_images = train_images / 30000

print("Train Image Shape: ", train_images.shape)
print("Train Label Shape: ", train_labels.shape)

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(train_images.shape[1], train_images.shape[2])),  # input layer (1)
    keras.layers.Dense(1500, activation='linear'),  # hidden layer (2)
    keras.layers.Dense(1500, activation='tanh'),  # hidden layer (2)
    keras.layers.Dense(1500, activation='relu'),  # hidden layer (2)
    keras.layers.Dense(len(gesture_list), activation='softmax') # output layer (3)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(train_images, train_labels, epochs=10)

test_loss, test_acc = model.evaluate(train_images,  train_labels, verbose=1) 

print('Test accuracy:', test_acc)

model.save('trained_model.keras')