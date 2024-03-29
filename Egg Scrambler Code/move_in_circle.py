# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 11:34:42 2024

@author: 20Jan
"""

import numpy as np
import time
import serial

# Connect to Arduino
arduino = serial.Serial('COM4', 9600)  # Replace 'COM_Arduino' with the actual COM port
time.sleep(2) # wait for the serial connection to initialize

# Constants for arm lengths
a1 = 134.9  # length of arm1 in mm
a2 = 147.1  # length of arm2 in mm

# Define circular path parameters
# x-axis will be axis extenting from robot, y-axis will be left or right, z-axis will be up or down  
x_center, y_center = 160, 0  # Center of the pan measured from robot base
z = 50 # operating height
pan_radius = 100
theta = 0  # Starting angle
theta4 = 0

# Constants for arm range of motion (global)
s1_min = 35
s1_max = 133 #133
    # define s2_min, s2_max in functions bc it depends on theta1
    
# Constants for arm range of motion (Ardunio Servo)
s1_mod_min = 0
s1_mod_max = 70
s2_mod_min = 45
s2_mod_max = 145

# Function to update servo angles based on theta
def update_movement(theta):
    # Calculate x, y positions on the circle
    x = x_center + pan_radius * np.cos(np.radians(theta))
    y = y_center + pan_radius * np.sin(np.radians(theta))
    print("x: ", x)
    print("y: ", y)
    
    # Use inverse kinematics to calculate servo angles for x, y
    theta1, theta2, theta3 = inverse_kinematics(x, y, a1, a2)
    # Assume a function to calculate theta4 based on theta to keep the spatula oriented correctly
    theta4 = calculate_spatula_orientation(theta)
    # theta4 = 90
    # Send calculated angles to Arduino
    send_to_arduino(theta1, theta2, theta3, theta4)

def inverse_kinematics(x, y, a1, a2):
    # find hypotenous of line between point on pan and robot base, and treat this as the new "x"
    r = np.sqrt(x**2+y**2)
    # find relationship between x-y and theta of servo 3
    q3 = np.arccos((r**2+x_center**2-pan_radius**2)/(2*np.sqrt(x**2+y**2)*x_center))*np.sign(y)
    print("q3: ", q3)
    # Proceed with the calculations using r and z (which may be the last valid values)
    r1 = np.sqrt(r**2 + z**2)  # Recalculate r1 in case last valid values are used
    argument = (r1**2 - a1**2 - a2**2) / (2 * a1 * a2)
    if argument < -1 or argument > 1:
        print(f"Error: arccos argument out of range: {argument}")
        return None, None

    q2 = -np.arccos(argument)
    q1 = np.arctan2(z, r) - np.arctan2((a2 * np.sin(q2)), (a1 + a2 * np.cos(q2)))
    q2 = q2 + q1  # Set theta2 to global coordinates
    q1 = np.rad2deg(q1)
    q2 = np.rad2deg(q2)  
    q3 = 90 - np.rad2deg(q3)
    print("theta1: ", q1)
    print("theta2: ", q2)
    print("theta3: ", q3)
    return q1, q2, q3


# def perform_circular_motion():
#     global theta
#     while True:  # Loop to keep the motion continuous until stopped
#         update_movement(theta)
#         theta += 5  # Increment theta to move along the circle; adjust for speed
#         if theta >= 360:
#             theta -= 360  # Reset theta to keep it within 0-360 degrees
#         #time.sleep(0.01)  # Adjust timing for smoother or faster rotation

# Alternate moving around big and little circle
def perform_circular_motion():
    global theta, pan_radius
    while True:  # Loop to keep the motion continuous until stopped
        update_movement(theta)
        theta += 5  # Increment theta to move along the circle; adjust for speed
        if theta >= 360:
            theta -= 360  # Reset theta to keep it within 0-360 degrees
            
            # Toggle pan_radius between 110 and 70
            if pan_radius == 100:
                pan_radius = 70
            else:
                
                
                pan_radius = 100
        
        time.sleep(0.01)  # Adjust timing for smoother or faster rotation


# Move spatula normal to the pan
def calculate_spatula_orientation(theta):
    # Implement logic to calculate servo 4 angle based on theta
    if theta <= 170: # The numbers are a bit odd, I know. It's just what worked best with my setup because my servo wasn't moving a true 180 deg rotation.  
        theta4 = (180-theta)
    else: 
        theta4 = (330-theta)
    return theta4

# # Moving the spatula back and forth rapidly
# def calculate_spatula_orientation():
#     global theta4
#     # Introduce a static variable within the function for direction tracking.
#     # This variable will persist across function calls.
#     if 'direction' not in calculate_spatula_orientation.__dict__:
#         calculate_spatula_orientation.direction = 1  # Start with direction set to 1 (incrementing)

#     # Adjust theta4 based on the current direction.
#     theta4 += 13 * calculate_spatula_orientation.direction

#     # Check if theta4 has reached its bounds and toggle direction if so.
#     if theta4 >= 180 or theta4 <= 0:
#         calculate_spatula_orientation.direction *= -1  # Toggle direction
#         # Adjust theta4 to ensure it stays within 0-180 range.
#         theta4 = max(0, min(theta4, 180))

#     return theta4

# Function to send all values to Arduino
def send_to_arduino(theta1, theta2, theta3, theta4):
    #calculate s2 range in global coordinate frame 
    s2_max = 19 #19
    s2_min = -69 #-69
    # Convert the "global" angles into Arunino Servo angles by interpolation
    theta1_mod = ((theta1-s1_min)/(s1_max-s1_min))*(-s1_mod_max+s1_mod_min)+s1_mod_max
    theta2_mod = ((theta2-s2_max)/(s2_min-s2_max))*(-s2_mod_max+s2_mod_min)+s2_mod_max
    print('theta1_mod:',theta1_mod)
    print('theta2_mod:',theta2_mod)
    print('theta3:',theta3)
    print('theta4:',theta4)
    data_string = f"{theta1_mod},{theta2_mod},{theta3},{theta4}\n"  # Format to be parsed by Arduino
    #print(f"Sending to Arduino: {data_string}") # Debugging 
    arduino.write(data_string.encode())

# Start circular motion
perform_circular_motion()
