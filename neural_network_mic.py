import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from collections import Counter

# Load data
train_images_path = 'X_train.txt'
train_labels_path = 'y_train_gesture.txt'
gesture_list = ['idle', 'left', 'right', 'up', 'down']

train_images = np.loadtxt(train_images_path, dtype=float)
train_labels = np.loadtxt(train_labels_path, dtype=int)

train_images = np.reshape(train_images, (-1, 15, train_images.shape[1]))

# Normalize data
train_images = (train_images + 32768) / (32768 * 2)

# Split data
# Count instances of each class type
class_counts = Counter(train_labels)

# Find the minority class
min_class_count = min(class_counts.values())
min_class_label = min(class_counts, key=class_counts.get)

# Undersample the majority classes
undersampled_images = []
undersampled_labels = []
for label, image in zip(train_labels, train_images):
    if class_counts[label] == min_class_count:
        undersampled_images.append(image)
        undersampled_labels.append(label)
    elif class_counts[label] > min_class_count:
        class_counts[label] -= 1

# Convert lists to arrays
undersampled_images = np.array(undersampled_images)
undersampled_labels = np.array(undersampled_labels)

# Split undersampled data
X_train, X_val, y_train, y_val = train_test_split(undersampled_images, undersampled_labels, test_size=0.3, random_state=42, stratify=undersampled_labels)

# Count instances of each class type in training data after stratified split
train_class_counts = {gesture_list[i]: np.sum(y_train == i) for i in range(len(gesture_list))}
print("Training Data Class Counts (Stratified Split):")
for gesture, count in train_class_counts.items():
    print(f"{gesture}: {count} instances")

# Count instances of each class type in validation data after stratified split
val_class_counts = {gesture_list[i]: np.sum(y_val == i) for i in range(len(gesture_list))}
print("\nValidation Data Class Counts (Stratified Split):")
for gesture, count in val_class_counts.items():
    print(f"{gesture}: {count} instances")

# Calculate total instances in the training set
total_train_instances = len(y_train)

# Calculate percentages for each class within the training set
train_class_percentages = {gesture: (count / total_train_instances) * 100 for gesture, count in train_class_counts.items()}
print("\nTraining Data Class Percentages:")
for gesture, percentage in train_class_percentages.items():
    print(f"{gesture}: {percentage:.2f}%")

# Calculate total instances in the validation set
total_val_instances = len(y_val)

# Calculate percentages for each class within the validation set
val_class_percentages = {gesture: (count / total_val_instances) * 100 for gesture, count in val_class_counts.items()}
print("\nValidation Data Class Percentages:")
for gesture, percentage in val_class_percentages.items():
    print(f"{gesture}: {percentage:.2f}%")

# Define the model
model = keras.Sequential([
    keras.layers.Conv1D(64, 3, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
    # keras.layers.MaxPooling1D(2),
    # keras.layers.Dropout(0.3),
    keras.layers.Conv1D(256, 3, activation='relu'),
    keras.layers.Flatten(),
    keras.layers.Dense(2058, activation='relu'),
    keras.layers.Dense(1024, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(512, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dropout(0.1),
    keras.layers.Dense(len(gesture_list), activation='softmax')
])


model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.000001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=1000, validation_data=(X_val, y_val), callbacks=[EarlyStopping(patience=500)])

# Plotting loss
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Training and Validation Loss')
plt.show()

# Plotting accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Training and Validation Accuracy')
plt.show()

# Evaluate on validation set
test_loss, test_acc = model.evaluate(X_val, y_val, verbose=1)
print('Validation accuracy:', test_acc)

# Save the model
model.save('trained_model.keras')
