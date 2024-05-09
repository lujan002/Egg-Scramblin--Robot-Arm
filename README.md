# Robot Arm Egg Scrambler

### This project is a work-in-progress

Autonomous robotic arm for srambling eggs. The work done to create the robot base is documented in my [this repository](https://github.com/lujan002/EEZYbotARM-Mk2-Robot-Arm-PS4-Control). For this modification, I've developed an new end effector spatula and programmed an optimal motion path for the end effector to reliably scramble eggs without human intervention. 

Watch the [demo video](https://www.youtube.com/watch?v=ewMSy4-Ajvs&embeds_referring_euri=https%3A%2F%2Flukejansen.carrd.co%2F&feature=emb_logo)

<p align="center">
  <img src="RoboChef2.png" alt="Robot Arm" width="50%" height="auto">
</p>
<p align="center">
  <img src="ActionShot.png" alt="Action Shot" width="50%" height="auto">
</p>

## Mechanical Modifications 
The first prototype utilized a 1:1 gear ratio with an SG90 servo motor, enabling a 180-degree range of motion for the spatula.

<p align="center">
  <img src="gears_v1.png" alt="Gears v1" width="50%" height="auto">
</p>

Adjusting to challenges of programming movement with only 180 degress of rotation, the second iteration introduced a middle gear to acheive a 2.5:1 gear ratio, thus enabling a full 360-degree rotation. This change necessitated an upgrade to a more powerful servo due to the increased torque requirements.

<p align="center">
  <img src="gears_v2.png" alt="Gears v2" width="50%" height="auto">
</p>

However, aligning the gears incorrectly proved to be problematic. The middle gear was not aligned with the other two, which caused increased friction and an imperfect mesh between the gears. I tried to address this by adjusting the number of teeth and the thickness of each tooth, but these changes did not resolve the issue. Ultimately, I found that removing the pinion altogether led to a more robust design. Although this required slightly extending the base of the end effector to make space for a single, larger gear, the trade-off was well worth it for the improved performance and reliability.

I have programmed the spatula to move in a circle ensuring it remains tangent to the pan's circumference, incorporating a vertical swipe to capture any unturned eggs. Pan radius, pan center coordinates, operating height are all easily adjustable parameters. 

## Cooked Egg Detection Software
In order to make the robot truly autonomous, a way to detect the eggs when cooked was necessary. A novel addition to this project was the task of training a machine learning model to take images from a camera stream and use this to predict if the picture it sees is cooked or uncooked. 

<p align="center">
  <img src="CookedDataset.png" alt="CookedDataset" width="50%" height="auto">
</p>
<p align="center">
  <img src="UncookedDataset.png" alt="UncookedDataset" width="50%" height="auto">
</p>

Future objectives include:
enhancing the spatula's path for consistent egg contact
integrating a machine learning-based vision system to determine when the eggs are fully cooked
Fully autonomous capabilities, such as cracking eggs and turning off the stove. 

