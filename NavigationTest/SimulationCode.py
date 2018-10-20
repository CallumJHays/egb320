#!/usr/bin/python

# import the soccer bot module - this will include math, time, numpy (as np) and vrep python modules
import math
import numpy as np
import matplotlib.pyplot as plt

import sys, os

# Make the rest of the code available to this
def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)
sys.path.append(relpath(".."))

from VisionSystem import VisionSystem, VisualObject, VideoStream
from VisionSystem.DetectionModel import ThreshBlob
from DriveSystem import DriveSystem


# SET GLOBAL VARIABLES
headingRad = 0
MAX_ROBOT_ROT = 1
GOAL_P = 0.5
MAX_ROBOT_VEL = 0.05
lastHeading = 0.5

# FUNCTIONS

# Get Attraction Field
def getAttractionField(goal_rad):
    # Field Map with size of 60 degrees scaled to 360 degrees
    goal_deg = round((math.degrees(goal_rad) + 30))
    attractionField = np.zeros(61)
    # At the goal_deg is max attraction, therefore set to 1
    attractionField[goal_deg] = 1
    gradient = 1/float(60);
    for angle in range (0, 31, 1):
        attractionField[Clip_Deg_60(goal_deg + angle)] = 1 - angle*gradient
        attractionField[Clip_Deg_60(goal_deg - angle)] = 1 - angle*gradient
    return attractionField

# Get Repulsion Field
def getRepulsionField(obstacles):
    
    repulsionField = np.zeros(61)
    r_radius = 0.18/2;
    
    for obstacle in obstacles:
        obs_range = obstacle[0]
        obs_bear = obstacle[1] # Radians
        obs_bear_deg = round((math.degrees(obs_bear) + 30))
        obs_width = 2 * r_radius + 0.1
        
        obs_dist = max(obs_width, obs_range)
        
        # Convert size of obstacle to size in polar coordinates
        # Take into account how far the obstacle is away from the robot
        obs_width_rad = math.asin(obs_width/obs_dist)
        obs_width_deg = int(round(Clip_Deg_60(math.degrees(obs_width_rad))))
        
        # Generate Repulsive field with respect to obstacle
        obs_effect = max(0, 1 - min(1, (obs_range - r_radius * 2)))
        repulsionField[obs_bear_deg] = obs_effect
        
        for angle in range (1, obs_width_deg, 1):
            repulsionField[Clip_Deg_60(obs_bear_deg - angle)] = obs_effect
            repulsionField[Clip_Deg_60(obs_bear_deg + angle)] = obs_effect
            
    return repulsionField
    
# Get Residual Field
def getResidualField(attractionField, repulsionField):
    residualField = attractionField - repulsionField
    return residualField

# Potential Field Generation
def generatePotentialField(goal, obstaclesRB):
    # Generate Attraction Field
    attractionField = np.zeros(61)
    attractionField = getAttractionField(goal)
    # Generate Obstacle Field
    repulsionField = np.zeros(61)
    if obstaclesRB != None:
        repulsionField = getRepulsionField(obstaclesRB)
    # Generate Residual Field
    residualField = getResidualField(attractionField, repulsionField)
    headingDeg = np.argmax(residualField)
    headingRad = math.radians(((headingDeg) - 30))
    #print(headingDeg)
    # Plot the fields
    plt.clf()
    plt.figure(1)
    plt.subplot(311)
    plt.plot(attractionField)
    plt.xlim(0,60)
    plt.subplot(312)
    plt.plot(repulsionField)
    plt.xlim(0,60)
    plt.subplot(313)
    plt.plot(residualField)
    plt.xlim(0,60)
    plt.pause(0.05)
    plt.show()
    return headingRad

# Get Signed Angle
def getSignedDelta(angle_head, angle_robot):
    return angle_head
    
# Clip input angle to be between input range
def Clip_Deg_60(angle):
    while angle <= 0:
        angle = angle + 60
    while angle >= 60:
        angle = angle - 60
    return angle

# Obstacle Avoidance Procedure (1 Obstacle Input)
def avoidObstacleProcedure1(goalRange, goalBearing, obstaclesRB, headingRad):
    obstacle = obstaclesRB[0]
    obs_range = obstacle[0]
    obs_bear = obstacle[1] # Radians
    obs_x = obs_range * math.sin(obs_bear)
    obs_y = obs_range * math.cos(obs_bear)
    ballx = goalRange * math.sin(goalBearing)
    bally = goalRange * math.cos(goalBearing)
    distx = ballx - obs_x
    disty = bally - obs_y
    dist = math.sqrt(distx * distx + disty * disty)
    desired_rot_vel = min(MAX_ROBOT_ROT, max(-MAX_ROBOT_ROT, headingRad * GOAL_P))
    desired_vel = MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel)/MAX_ROBOT_ROT);
    desired_velx = desired_vel * math.sin(desired_rot_vel)
    desired_vely = desired_vel * math.cos(desired_rot_vel)
    if goalRange > obs_range and obs_range < 0.4:
        if goalBearing < 0 and goalBearing > obs_bear:
            drive_system.setTargetVelocities(desired_velx, desired_vely, -desired_rot_vel)
        elif goalBearing < 0 and goalBearing < obs_bear:
            drive_system.setTargetVelocities(-desired_velx, -desired_vely, desired_rot_vel)
        elif goalBearing > 0 and goalBearing > obs_bear:
            drive_system.setTargetVelocities(desired_velx, desired_vely, -desired_rot_vel)
        elif goalBearing > 0 and goalBearing < obs_bear:
            drive_system.setTargetVelocities(-desired_velx, -desired_vely, desired_rot_vel)
    else:
        drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)


def setup_vision_system():

    objects_to_size_and_result_limit = [
        ("ball", (0.043, 0.043, 0.043), 1)
        ("obstacle", (0.18, 0.18, 0.2), None),
        ("blue_goal", (0.3, 0.3, 0.1), 1) # 30 centimetres long, 10 cm high? i guess
        ("yellow_goal", (0.3, 0.3, 0.1), 1)
    ]

    return VisionSystem(objects_to_track={
        name: VisualObject(
            real_size=size,
            detection_model=ThreshBlob.load(relpath("..", "detection_models", name)),
            result_limit=result_limit
        ) for name, size, result_limit in objects_to_size_and_result_limit
    })


# get the range and bearings from a vision system, assuming it has been updated recently
def get_detected_objects(video_stream, vision_system):
    # this might take a while - planned some performance tweaks to boost this speed by 3.5-ish
    vision_system.update_with_frame(next(video_stream))
    objs = vision_system.objects_to_track # for shorthand

    def maybenone(bearings_distances, multi):
        if any(bearings_distances):
            if multi:
                return bearings_distances
            else:
                return bearings_distances[0]
        else:
            return None

    return (
        maybenone(objs["ball"].bearings_distances),
        maybenone(objs["blue_goal"].bearings_distances),
        maybenone(objs["yellow_goal"].bearings_distances),
        maybenone(objs["obstacle"].bearings_distances),
    )

def setTargetVelocities(xvel, yvel, rot):


# MAIN SCRIPT
if __name__ == '__main__':

  #Wrap everything in a try except case that catches KeyboardInterrupts.
  #In the exception catch code attempt to Stop the VREP Simulator so don 't have to Stop it manually when pressing CTRL+C
  try:
    # downsample scale is quadratically related to performance, inversely quadratically to fidelity
    video_stream = VideoStream(downsample_scale=4)
    vision_system = setup_vision_system()
    drive_system = DriveSystem()


    # Edit While loop to integrate drive and visiion system
    ballRB, blueRB, yellowRB, obstaclesRB = get_detected_objects(video_stream, vision_system)
    count = 0
    goal_found = False
    lastObstacle = 0
    lastHeading = 0.4
    check = False
    
    while True:
        
        #check to see if ball is in dribbler
        if check == True: # soccerBotSim.BallInDribbler() == True:
            print("Ball Obtained")
            ballRB, blueRB, yellowRB, obstaclesRB = get_detected_objects(video_stream, vision_system)
            if goal_found == False:
                drive_system.setTargetVelocities(0, 0, 0.5)
                if blueRB != None:
                    bGoalRange = blueRB[0]
                    bGoalBearing = blueRB[1]
                    goal_found = True
                    print("Goal Found")
            if goal_found == True:
                print("Heading towards Goal")
                if blueRB != None:
                    bGoalRange = blueRB[0]
                    bGoalBearing = blueRB[1]
                else:
                    goal_found = False
                headingRad = generatePotentialField(bGoalBearing, obstaclesRB)
                if obstaclesRB != None:
                    if len(obstaclesRB) == 1:
                        print("1 Obstacle")
                        avoidObstacleProcedure1(bGoalRange, bGoalBearing, obstaclesRB, headingRad)
                else:
                    desired_rot_vel = min(MAX_ROBOT_ROT, max(-MAX_ROBOT_ROT, headingRad * GOAL_P))
                    desired_vel = MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel)/MAX_ROBOT_ROT);
                    drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)
                if bGoalRange < 0.65:
                    print("Shoot")
                    #
                    # DRIBBLER
                    #
                    #soccerBotSim.KickBall(0.5)
                    goal_found = False
                    lastHeading = 0.4
        else:
            print("Looking for Ball")
            ballRB, blueRB, yellowRB, obstaclesRB = get_detected_objects(video_stream, vision_system)
            if ballRB == None:
                drive_system.setTargetVelocities(0, 0, lastHeading + 0.1)
                lastHeading = 0.4
            else:
                # Get Range and Bearing of Ball
                ballRange = ballRB[0]
                ballBearing = ballRB[1]
                lastHeading = ballBearing
                # Generate Potential Field
                headingRad = generatePotentialField(ballBearing, obstaclesRB)
                if obstaclesRB != None:
                    if len(obstaclesRB) == 1:
                        print("1 Obstacle")
                        avoidObstacleProcedure1(ballRange, ballBearing, obstaclesRB, headingRad)
                else:
                    desired_rot_vel = min(MAX_ROBOT_ROT, max(-MAX_ROBOT_ROT, headingRad * GOAL_P))
                    desired_vel = MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel)/MAX_ROBOT_ROT)
                    drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)

  except KeyboardInterrupt as e: #attempt to stop simulator so it restarts and don 't have to manually press the Stop button in VREP 
    soccerBotSim.StopSimulator()