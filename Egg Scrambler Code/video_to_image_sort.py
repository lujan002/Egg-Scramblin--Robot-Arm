# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:30:08 2024

@author: 20Jan
"""

import cv2
import os
import shutil  # Import shutil for moving files

def capture_frames(video_path, output_folder, test_folder, interval=1, test_interval=5):
    # Load the video
    video = cv2.VideoCapture(video_path)
    
    # Get video frame rate
    fps = video.get(cv2.CAP_PROP_FPS)
    
    # Calculate the interval in frames
    frames_interval = int(fps * interval)
    
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Ensure test folder exists
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)
    
    frame_count = 0
    image_count = 0
    
    while True:
        # Read the next frame
        success, frame = video.read()
        if not success:
            break  # No more frames, exit the loop
        
        # Check if it's time to capture this frame
        if frame_count % frames_interval == 0:
            base_name = f'image2_{image_count:05d}.jpg'
            if image_count % test_interval == 0:
                # For every 5th image, save to the test dataset folder
                image_path = os.path.join(test_folder, base_name).replace("\\", "/")
            else:
                # Save other images to the output folder
                image_path = os.path.join(output_folder, base_name).replace("\\", "/")
            
            cv2.imwrite(image_path, frame)
            print(f'Image saved: {image_path}')
            image_count += 1
        
        frame_count += 1
    
    # Release the video capture object
    video.release()
    print('Done!')

# Example usage
video_path = 'data_videos/IMG_6522.MOV'
output_folder = 'eggs_dataset/uncooked'
test_folder = 'eggs_val_dataset/uncooked'
capture_frames(video_path, output_folder, test_folder, interval=1)  # Capture an image every second, moving every 5th to test dataset
