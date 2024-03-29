# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 23:45:20 2024

@author: 20Jan

Note: Due to some inconsistencies with my physical system, namely the gear ratio not being a perfect 2:1, this throws the
orientation of theta4 off a bit. I added some ad-hoc adjustments that helped balance this. These adjustments may seem random 
to another user. Likely you may need to play around with these adjustments to tune your own system. 
"""


import numpy as np
import time
import serial

# Connect to Arduino
arduino = serial.Serial('COM4', 9600)  # Replace 'COM_Arduino' with the actual COM port
time.sleep(2) # wait for the serial connection to initialize

# Constants for arm lengths
a1 = 134.9  # length of arm1 in mm
a2 = 155.1  # length of arm2 in mm

# Define circular path parameters
# x-axis will be axis extenting from robot, y-axis will be left or right, z-axis will be up or down  
x_center, y_center = 120, 0  # Center of the pan measured from robot base
# operating height
z = 20  
# height above the pan which the spatula will maneuver about
z_increase = 90

larger_radius = 90
smaller_radius = 90
pan_radius = larger_radius # Initialize pan radius by setting it to the larger radius

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

# Constant for controlling speed (delete?)
sleep_time = 0
# Constant for switching between clockwise/counter-clockwise
spin_dir = 1
# spin_counter = 0

def calc_xy(theta):
    global theta4, z, spin_dir
    # Calculate x, y positions on the circle
    x = x_center + pan_radius * np.cos(np.radians(theta))
    y = y_center + pan_radius * np.sin(np.radians(theta))
    return x, y

# Function to update servo angles based on theta
def update_movement(theta, spin_spatula=True): 
    global theta4, z, spin_dir
    # Calculate x, y positions on the circle
    x = x_center + pan_radius * np.cos(np.radians(theta))
    y = y_center + pan_radius * np.sin(np.radians(theta))
    print("x: ", x)
    print("y: ", y)
    # Use inverse kinematics to calculate servo angles for x, y
    theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2)
    if spin_spatula == True:
        theta4 = calculate_spatula_orientation(theta)
    swipe_pan(x, y, z, theta, theta4)
    if theta >= 180 and spin_dir == 1:
        theta4 -= 20
    if theta <= 180 and spin_dir == -1 :
        theta4 += 20                
    send_to_arduino(theta1, theta2, theta3, theta4)
    return theta1, theta2, theta3, theta4

last_valid_theta3 = 90.0  # Adjust based on your system's default or safe position

def inverse_kinematics(x, y, z, a1, a2):
    global last_valid_theta3  # Use the global variable to track the last valid value
    # find hypotenous of line between point on pan and robot base, and treat this as the new "x"
    r = np.sqrt(x**2+y**2)
    r2 = np.sqrt((x - x_center)**2 + (y-y_center)**2)
    # find relationship between x-y and theta of servo 3
    q3 = np.arccos((r**2+x_center**2-r2**2)/(2*np.sqrt(x**2+y**2)*x_center))*np.sign(y)
    print("q3: ", q3)
    # Proceed with the calculations using r and z (which may be the last valid values)
    r1 = np.sqrt(r**2 + z**2)  # Recalculate r1 in case last valid values are used
    argument = (r1**2 - a1**2 - a2**2) / (2 * a1 * a2)
    if argument < -1 or argument > 1:
        print(f"Error: arccos argument out of range: {argument}")
        return None, None
    # Proceed with your calculation, ensuring q3 is valid
    if np.isnan(q3):
        # If q3 is NaN, use the last valid theta3
        q3 = last_valid_theta3
    else:
        # If q3 is valid, update the last valid theta3
        last_valid_theta3 = q3
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

# Alternate moving around big and little circle
def perform_circular_motion():
    global theta, z, pan_radius, spin_dir
    # start at the right of the pan
    send_to_arduino(45, -21, 90, 180)
    # start with spatual raised
    # theta1, theta2, theta3 = inverse_kinematics(x_center+pan_radius, y_center, z+z_increase, a1, a2)
    # send_to_arduino(theta1, theta2, theta3, 180)
    # time.sleep(0.5)
    while True:  # Loop to keep the motion continuous until stopped
        print("theta:", theta)
        theta1, theta2, theta3, theta4 = update_movement(theta)
        if theta > 170 and theta < 190: # Move theta slower around the left edge of the pan
            if spin_dir == 1:
                theta += 2.5 # Increment theta to move along the circle; adjust for speed
            elif spin_dir == -1:
                theta -= 2.5
        else:    
            if spin_dir == 1 and pan_radius == larger_radius:
                theta += 10 # Increment theta to move along the circle; adjust for speed
            elif spin_dir == -1 and pan_radius == larger_radius:
                theta -= 10
            elif spin_dir == 1 and pan_radius == smaller_radius:
                theta += 10        # Move twice as fast for the smaller radius
            elif spin_dir == -1 and pan_radius == smaller_radius:
                theta -= 10        # Move twice as fast for the smaller radius
        if theta == 360 or theta == 0:
            spin_dir = spin_dir * -1
            # if pan_radius == smaller_radius:
            #     lift_n_drop()            
        if theta >= 360: 
            # theta -= 360  # Reset theta to keep it within 0-360 degrees
            if pan_radius == larger_radius: # only swipe back and forth for the larger radius
                # swipe_middle_pan(theta1, theta2) # Swipe the spatula back and forth down x after every full circle
                # Toggle pan_radius between 110 and 70
                pan_radius = smaller_radius
            else:     
                pan_radius = larger_radius
        time.sleep(sleep_time)  # Adjust timing for smoother or faster rotation

# Move spatula normal to the pan
def calculate_spatula_orientation(theta):
    global spin_dir
    # Implement logic to calculate servo 4 angle based on theta
    theta4 = 180-(theta/2)
    # adjust for theta4 drift observed emperically in my setup
    theta4 += 0
    theta4 = 90+(theta4-90)/0.9
    # if spin_dir == 1:
    #     theta4 = 180-(theta/2)
    #     # if theta >= 180:
    #     #     theta4 = theta4 + 70 # reset theta4 to 135 deg, so it can continue along entire pan at a 45 deg angle 
    # elif spin_dir == -1:
    #     theta4 = 180-(theta/2) 
    #     # if theta <= 180:
        #     theta4 = theta4 - 70 # reset theta4 to 135 deg, so it can continue along entire pan at a 45 deg angle  
    return theta4

# Function to perform a swipe down the middle of the pan
# def swipe_middle_pan(theta1r, theta2r):
#     global flip, z
#     flip = 0
#     xr = x_center + pan_radius
#     xl = x_center - pan_radius - 30
#     y = 0
#     # Number of steps for the movement
#     steps = 10
#     # Calculate the increment for each step
#     increment = (xr - xl) / steps
#     # Perform the swipe motion by moving to the left most and right most points on the circle
#     for _ in range(steps): # move right to left
#         xr -= increment
#         theta1r, theta2r, theta3 = inverse_kinematics(xr, y, z, a1, a2)
#         send_to_arduino(theta1r, theta2r, 90, 45)
#         time.sleep(sleep_time)  # Adjust the sleep duration to control the speed of movement
#     for _ in range(steps): # move left to right
#         xl += increment
#         theta1l, theta2l, theta3 = inverse_kinematics(xl, y, z, a1, a2)
#         if _ < steps//2 - 1:
#             send_to_arduino(theta1l, theta2l, 90, 45)
#         if _ >= steps//2 - 1:
#             send_to_arduino(theta1l, theta2l, 90, 0)
            
# def lift_n_drop():
#     global z, theta, spin_dir, theta4
#     # Function to lift the spatula up, move a few degrees, and drop down before spinning in other direction inorder to capture eggs that pile up on right side
#     z_increase = 150
#     theta_increase = 60
#     # Number of steps for the movement
#     steps = 5
#     # Calculate the increment for each step
#     # Perform the swipe motion by moving to the left most and right most points on the circle
#     for _ in range(steps): # move right to left
#         z += z_increase/steps
#         update_movement(theta, spin_spatula=False)
#     for _ in range(steps): # move right to left
#         theta -= theta_increase/steps*spin_dir    
#         update_movement(theta, spin_spatula=False)
#     for _ in range(steps): # move right to left
#         z -= z_increase/steps
#         update_movement(theta, spin_spatula=False)
#     for _ in range(steps): # move right to left
#         theta += theta_increase/steps*spin_dir    
#         update_movement(theta, spin_spatula=False)
def raise_spatula(x, y, z, z_increase, z_steps, theta4):
    for _ in range(z_steps):
        z += z_increase/z_steps
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2)
        send_to_arduino(theta1, theta2, theta3, theta4)    
        time.sleep(sleep_time)
def drop_spatula(x, y, z, z_increase, z_steps, theta4):
    for _ in range(z_steps):
        z -= z_increase/z_steps
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2)
        send_to_arduino(theta1, theta2, theta3, theta4)
        time.sleep(sleep_time)               
        
def swipe_pan(x, y, z, theta, theta4):
    global spin_dir
    if theta in [0-20*spin_dir, 100-20*spin_dir, 180-20*spin_dir, 260-20*spin_dir, 360-20*spin_dir]:
        theta4_og = theta4
        xr = x_center + pan_radius
        xl = x_center - pan_radius 
        ytop = y_center + pan_radius 
        ybot = y_center - pan_radius
        # Number of steps to reach opposite end and move z
        steps = 6
        z_steps = 6
        # Set parameter to conrol how far swipe goes (ie. 0.5 ends in middle of pan, 0.75 is three-quarters, 1.0 swipes entire pan, not ideal for splashing)
        swipe_dist_horz = 0.5
        swipe_dist_vert = 0.6
        # Function to lift the spatula up, move a few degrees, and drop down before spinning in other direction inorder to capture eggs that pile up on right side
        raise_spatula(x, y, z, z_increase, z_steps, theta4)
        if theta == 100-20*spin_dir: # swipe top > bottom
            theta += 20*spin_dir
            x, y = calc_xy(theta)
            theta4 = calculate_spatula_orientation(theta)+45
            theta1, theta2, theta3 = inverse_kinematics(x, y, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
            send_to_arduino(theta1, theta2, theta3, theta4)
            time.sleep(0.3)
            drop_spatula(x, y+20, z_increase, z_increase, z_steps, theta4) # moving y so that it is closer to the edge of the pan (emperical observation)
            for _ in range(steps):
                ytop -= ((pan_radius*2)/steps)*swipe_dist_vert 
                theta1, theta2, theta3 = inverse_kinematics(x, ytop, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
                send_to_arduino(theta1, theta2, theta3, theta4)
                time.sleep(sleep_time)
            raise_spatula(x, ytop, z, z_increase, z_steps, theta4)
            for _ in range(steps):
                ytop += ((pan_radius*2)/steps)*swipe_dist_vert 
                theta1, theta2, theta3 = inverse_kinematics(x, ytop, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
                send_to_arduino(theta1, theta2, theta3, theta4)
                time.sleep(sleep_time)
        if theta == 180-20*spin_dir: # swipe left > right
            theta += 20*spin_dir
            x, y = calc_xy(theta)
            theta4 = calculate_spatula_orientation(theta)+45
            theta1, theta2, theta3 = inverse_kinematics(x, y, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
            send_to_arduino(theta1, theta2, theta3, theta4)
            time.sleep(0.3)
            drop_spatula(x, y, z_increase, z_increase, z_steps, theta4)
            for _ in range(steps):
                xl += ((pan_radius*2)/steps)*swipe_dist_horz  
                theta1, theta2, theta3 = inverse_kinematics(xl, y, z, a1, a2)
                send_to_arduino(theta1, theta2, 90, theta4)
                time.sleep(sleep_time)
            # raise_spatula(xl, y, z, z_increase, z_steps, theta4)
            # time.sleep(0.3)
            # drop_spatula(xl+20, y, z_increase, z_increase, z_steps, theta4)
            spin_middle(35, theta1, theta2, theta3, theta4)
            raise_spatula(x, y, z, z_increase, z_steps, theta4)
            # time.sleep(0.3)
            for _ in range(steps):
                xl -= ((pan_radius*2)/steps)*swipe_dist_horz
                theta1, theta2, theta3 = inverse_kinematics(xl, y, z+z_increase, a1, a2)
                send_to_arduino(theta1, theta2, 90, theta4)
                time.sleep(sleep_time)
        if theta == 260-20*spin_dir: # swipe bottom > top
            # using 260 due to emperical observation of my setup; 270 is a bit too far to the right
            theta += 20*spin_dir
            x, y = calc_xy(theta)
            theta4 = calculate_spatula_orientation(theta)+35 # again, I observed that 35 works better than 45 with my setup 
            theta1, theta2, theta3 = inverse_kinematics(x, y, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
            send_to_arduino(theta1, theta2, theta3, theta4)
            time.sleep(0.3)
            drop_spatula(x, y-(-10), z_increase, z_increase, z_steps, theta4)  # moving y so that it is closer to the edge of the pan (emperical observation)
            for _ in range(steps):
                ybot += ((pan_radius*2)/steps)*swipe_dist_vert
                theta1, theta2, theta3 = inverse_kinematics(x, ybot, z, a1, a2)
                send_to_arduino(theta1, theta2, theta3, theta4)
            raise_spatula(x, ybot, z, z_increase, z_steps, theta4)
            for _ in range(steps):
                ybot -= ((pan_radius*2)/steps)*swipe_dist_vert 
                theta1, theta2, theta3 = inverse_kinematics(x, ybot, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
                send_to_arduino(theta1, theta2, theta3, theta4)
                time.sleep(sleep_time)   
        if theta == 360-20*spin_dir or theta == 0-20*spin_dir: # swipe right > left
            if theta == 360-20*spin_dir:
                theta += 20*spin_dir
                theta4 = 45
            else:
                theta += 20*spin_dir
                theta4 = 135
            # if theta4 == 360:
            #     theta4 = calculate_spatula_orientation(theta)+45
            # if theta4 == 0:
            #     theta4 = 1
            x, y = calc_xy(theta)
            theta1, theta2, theta3 = inverse_kinematics(x, y, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
            send_to_arduino(theta1, theta2, theta3, theta4)
            time.sleep(0.3)
            drop_spatula(x+20, y, z_increase, z_increase, z_steps, theta4) # moving x so that it is closer to the edge of the pan (emperical observation)
            for _ in range(steps):
                xr -= ((pan_radius*2)/steps)*swipe_dist_horz  
                theta1, theta2, theta3 = inverse_kinematics(xr, y, z, a1, a2)
                send_to_arduino(theta1, theta2, theta3, theta4)
            # raise_spatula(xr, y, z, z_increase, z_steps, theta4)
            # time.sleep(0.3)
            # drop_spatula(xr-20, y, z_increase, z_increase, z_steps, theta4)
            spin_middle(35, theta1, theta2, theta3, theta4)
            raise_spatula(x, y, z, z_increase, z_steps, theta4)
            # time.sleep(0.3)
            for _ in range(steps):
                xr += ((pan_radius*2)/steps)*swipe_dist_horz 
                theta1, theta2, theta3 = inverse_kinematics(xr, y, z+z_increase, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
                send_to_arduino(theta1, theta2, theta3, theta4)
                time.sleep(sleep_time)
        # Move spatula back into original position on outside circle
        # time.sleep(0.3)
        drop_spatula(x, y, z_increase, z_increase, z_steps, theta4)
        theta4 = theta4_og
        # theta += 80*spin_dir
        # update_movement(theta)
        theta1, theta2, theta3 = inverse_kinematics(x, y, z+z_increase, a1, a2)
        send_to_arduino(theta1, theta2, theta3, theta4)
        
def spin_middle(steps, theta1, theta2, theta3, theta4):
    # Direction flag, 1 for increasing, -1 for decreasing
    direction = 1
    
    for _ in range(steps):
        # Update theta4 based on direction
        theta4 += 10 * direction
        
        # If theta4 hits the upper limit, change direction to decrease
        if theta4 >= 180:
            theta4 = 180  # Correct overshoot
            direction = -1
        # If theta4 hits the lower limit, change direction to increase
        elif theta4 <= 0:
            theta4 = 0  # Correct overshoot
            direction = 1
            
        send_to_arduino(theta1, theta2, theta3, theta4)

#%%
'''
def raise_spatula(z_increase):
    z += z_increase
    # Assuming update_position is a function that updates the arm's position based on the current z
    theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2)
    send_to_arduino(theta1, theta2, theta3, theta4)
    
def lower_spatula(z_increase):
    z -= z_increase
    theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2)
    send_to_arduino(theta1, theta2, theta3, theta4)
    
def swipe_across(swipe_direction, steps):
    xr = x_center + pan_radius
    xl = x_center - pan_radius 
    ytop = y_center + pan_radius 
    ybot = y_center - pan_radius
    # Number of steps to reach opposite end and move z
    steps = 20
    if swipe_direction == 'top>bottom':
        theta4 = 180
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
        send_to_arduino(theta1, theta2, theta3, theta4)
        
        for _ in range(steps):
            z -= z_increase/steps
            ytop -= ((pan_radius*2)/steps)*swipe_dist 
            print("ytop:", ytop)
            print("y:", y)
            print("z:", z)
            theta1, theta2, theta3 = inverse_kinematics(x, ytop, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
            send_to_arduino(theta1, theta2, theta3, theta4)
            time.sleep(0.1)
    if theta == 180: # swipe left > right
        theta4 = 90
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
        send_to_arduino(theta1, theta2, theta3, theta4)
        z -= z_increase
        for _ in range(steps):
            xl += (xr-xl)/(steps*swipe_dist) 
            theta1, theta2, theta3 = inverse_kinematics(xl, y, z, a1, a2)
            send_to_arduino(theta1, theta2, theta3, theta4)
    if theta == 270: # swipe bottom > top
        theta4 = 180
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
        send_to_arduino(theta1, theta2, theta3, theta4)
        z -= z_increase
        for _ in range(steps):
            ybot -= (ybot-ytop)/(steps*swipe_dist) 
            theta1, theta2, theta3 = inverse_kinematics(x, ybot, z, a1, a2)
            send_to_arduino(theta1, theta2, theta3, theta4)
    if theta == 360: # swipe right > left
        theta4 = 90
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, a1, a2) # is it necessary to use x_center, y_top, or just x and y???
        send_to_arduino(theta1, theta2, theta3, theta4)
        z -= z_increase
        for _ in range(steps):
            xr -= (xr-xl)/(steps*swipe_dist) 
            theta1, theta2, theta3 = inverse_kinematics(xr, y, z, a1, a2)
            send_to_arduino(theta1, theta2, theta3, theta4)

def swipe_pan2(x, y, z, theta, theta4):
    if theta in [90, 180, 270, 360]:
        # Store original values to restore later
        z_original, theta4_original = z, theta4
        
        # Raise the spatula before swiping
        raise_spatula(50)
        time.sleep(0.5)  # Wait for the raise to complete

        # Determine the swipe direction based on theta
        if theta == 90:
            swipe_direction = 'top>bottom'
        elif theta == 180:
            swipe_direction = 'left>right'
        elif theta == 270:
            swipe_direction = 'bottom>top'
        elif theta == 360:
            swipe_direction = 'right>left'
        
        # Perform the swipe
        swipe_across(swipe_direction, 20, 0.75)

        # Restore spatula to original position and orientation
        lower_spatula(50)
        theta4 = theta4_original
        update_position(x, y, theta4)

        # Pause before resuming normal operation to ensure stability
        time.sleep(0.5)
'''
#%%
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
    # When the spatula is resetting its orientation at the right of the circle, make sure it is completely flipped around before continuing movement 
    # if theta == 0 and flip == 1:
    #     time.sleep(0.5)
# Start circular motion
perform_circular_motion()
