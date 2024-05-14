import numpy as np

import tensorflow as tf
from tensorflow import keras

train_images_path = 'X_train.txt'
train_labels_path = 'y_train_gesture.txt'
number_input = 150
class_names = ['none', 'left', 'right', 'up', 'down']

# train_images = np.loadtxt(train_images_path, dtype=float)
file = open(train_images_path, "r")
train_images = file.read()
train_images = train_images.split("\n")
for i in range(len(train_images)):
    train_images[i] = train_images[i].split(' ')

train_labels = np.loadtxt(train_labels_path, dtype=str)
for i in range(len(train_labels)):
    train_labels[i] = class_names.index(train_labels[i])
train_labels = train_labels.astype(int)

while True:
    remove = False
    for i in range(len(train_images)):
        if len(train_images[i]) > 150:
            train_images.pop(i)
            train_labels = np.delete(train_labels, i)
            remove = True
            break
    if remove == False:
        break
    else: 
        remove == False

train_images = np.array(train_images, dtype=float)
train_images = np.reshape(train_images, (len(train_images), 1, number_input))
train_labels = np.reshape(train_labels, (len(train_labels), 1))
train_labels = train_labels / 4.0

print("Train Image Shape: ", train_images.shape)
print("Train Label Shape: ", train_labels.shape)

model = keras.Sequential([
    keras.layers.Input(shape=(1, number_input), batch_size=len(train_labels)),  # input layer (1)
    keras.layers.Dense(128, activation='relu'),  # hidden layer (2)
    keras.layers.Dense(len(class_names), activation='softmax') # output layer (3)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(train_images, train_labels, epochs=10)

model.save('trained_model.keras')