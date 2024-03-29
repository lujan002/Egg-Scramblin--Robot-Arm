# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 21:52:35 2024

@author: 20Jan

adopted from: https://www.tensorflow.org/tutorials/images/classification
"""


import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np 

# Import the data
data_dir = r"C:\Users\20Jan\Robot Arm Copy\Egg Scrambler Code\eggs_dataset"
img_height = 256
img_width = 256
num_classes = 2

train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    batch_size=32,
    image_size=(img_height, img_width))
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    batch_size=32,
    image_size=(img_height, img_width))

# model = tf.keras.applications.Xception(
#     weights=None, input_shape=(256, 256, 3), classes=10)
# model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
# model.fit(train_ds, epochs=10, validation_data=validation_ds)

# Get the class names from the foler directory names
class_names = train_ds.class_names
print(class_names)

# View the first 9 images
plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

# Configure the dataset for performance
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# Create the model
model = models.Sequential([
  layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

# Compile the model
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.summary()

# Fit the model
epochs=10
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

# Evaluate the model
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

#%%
test_dir = r"C:\Users\20Jan\Robot Arm Copy\Egg Scrambler Code\eggs_val_dataset"
# Make Predictions
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    shuffle=False,
    batch_size=1,
    image_size=(256, 256))  # Adjust `image_size` to match the input size your model expects

probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
predictions = probability_model.predict(test_ds)
predicted_classes = np.argmax(predictions, axis=-1)
np.argmax(predictions[0])
test_ds[0]

# Adjust the plot_image function to not require true labels
def plot_image(i, predictions_array, img):
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])

  plt.imshow(img.numpy().astype("uint8"))
  predicted_label = np.argmax(predictions_array)

  plt.xlabel("{} {:2.0f}%".format(class_names[predicted_label],
                                  100*np.max(predictions_array)),
                                  color='blue')

# Create a batch of images and labels from the test dataset
for test_images, _ in test_ds.take(1):  # Take 1 batch from the test dataset
    break  # We break the loop to not go over more batches

# Plot the first X test images and their predicted labels
num_rows = 2
num_cols = 3
num_images = num_rows * num_cols
plt.figure(figsize=(2*2*num_cols, 2*num_rows))
for i in range(num_images):
    plt.subplot(num_rows, 2*num_cols, 2*i+1)
    plot_image(i, predictions[i], test_images[i])
plt.tight_layout()
plt.show()


# Future Work
'''
Implement precision, recall metrics
recall especially important to gauge how well the model avoids false positives (important in this case; bad if undercooked eggs are labeled as cooked')
'''