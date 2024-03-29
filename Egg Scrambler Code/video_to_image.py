# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 08:42:39 2024

@author: 20Jan
"""

import cv2
import os

def capture_frames(video_path, output_folder, interval=1):
    # Load the video
    video = cv2.VideoCapture(video_path)
    
    # Get video frame rate
    fps = video.get(cv2.CAP_PROP_FPS)
    
    # Calculate the interval in frames
    frames_interval = int(fps * interval)
    
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    frame_count = 0
    image_count = 0
    
    while True:
        # Read the next frame
        success, frame = video.read()
        if not success:
            break  # No more frames, exit the loop
        
        # Check if it's time to capture this frame
        if frame_count % frames_interval == 0:
            # Save the frame as an image
            image_path = os.path.join(output_folder, f'image2_{image_count:05d}.jpg')
            cv2.imwrite(image_path, frame)
            print(f'Image saved: {image_path}')
            image_count += 1
        
        frame_count += 1
    
    # Release the video capture object
    video.release()
    print('Done!')

# Example usage
video_path = 'data_videos\IMG_6522.MOV'
output_folder = 'captured_images'
capture_frames(video_path, output_folder, interval=1)  # Capture an image every second
