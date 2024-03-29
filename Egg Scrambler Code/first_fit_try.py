# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 13:36:16 2024

@author: 20Jan
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import os

#%%
# dimensions of our images.
img_width, img_height = 150, 150

train_data_dir = 'eggs_dataset'
validation_data_dir = 'eggs_val_dataset'
# Function to count the number of files in a directory, including files in subdirectories
def count_files(directory):
    return sum([len(files) for r, d, files in os.walk(directory)])
# Count the number of training and validation samples
nb_train_samples = count_files(train_data_dir)
nb_validation_samples = count_files(validation_data_dir)
print("Number of training samples:", nb_train_samples)
print("Number of validation samples:", nb_validation_samples)
epochs = 50
batch_size = 16

if tf.keras.backend.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

model = Sequential([
    Conv2D(32, (3, 3), input_shape=input_shape, activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])


# this is the augmentation configuration we will use for training
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    brightness_range=[0.5, 1.5])

# this is the augmentation configuration we will use for testing: only rescaling
test_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary',
    shuffle=True, #
    seed=42)

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

# Display the first image and its transformation
x_batch, y_batch = next(train_generator) # Fetch a batch of images
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].imshow(x_batch[0])
ax[0].set_title('Transformed Image')
ax[1].imshow(plt.imread(train_generator.filepaths[0]))  # Assuming this is the path to the original image
ax[1].set_title('Original Image')
plt.show()

#%%
model.fit(
    train_generator,
    steps_per_epoch=nb_train_samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples // batch_size,
    class_weight={0: 1, 1: 2}) # Double the weight of the uncooked eggs (class 1)
    
model.save_weights('first_try.weights.h5')

#%% Plot Validation Predictions 
# Assuming 'model' is your model's variable name
model.load_weights('first_try.weights.h5')  # Load the saved weights

validation_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = validation_datagen.flow_from_directory(
    'eggs_val_dataset',  # This should be the path to your validation dataset
    target_size=(150, 150),
    batch_size=nb_validation_samples,  # Process one image at a time
    class_mode='binary')

# Fetch a batch of validation images
validation_images, labels = next(validation_generator)

# Make a prediction
predictions = model.predict(validation_images)

# Calculate the number of batches needed to go through the validation set
num_validation_samples = validation_generator.samples
batch_size = validation_generator.batch_size
steps = num_validation_samples // batch_size

for i, image in enumerate(validation_images):
    # Calculate the prediction probability of being "cooked"
    prob_cooked = 1 - predictions[i][0]
    
    # Determine predicted and actual class names
    predicted_class = 'uncooked' if predictions[i][0] > 0.5 else 'cooked'
    actual_class = 'uncooked' if labels[i] > 0.5 else 'cooked'
    
    # Plot the image
    plt.figure(figsize=(5, 5))
    plt.imshow(image)
    plt.title(f'Prediction (probability of being cooked): {prob_cooked:.2f}\n' +
              f'Predicted class: {predicted_class}\n' +
              f'Correct class: {actual_class}')
    plt.show()
