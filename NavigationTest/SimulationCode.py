#!/usr/bin/python

# import the soccer bot module - this will include math, time, numpy (as np) and vrep python modules
from soccerbot_lib import *
import math
import numpy as np
import matplotlib.pyplot as plt

#SET SCENE PARAMETERS
sceneParameters = SceneParameters()

# Set the ball 's starting position [x, y] (in metres)
sceneParameters.ballStartingPosition = [0, -0.8]

# Set the position of the obstacles[x, y]( in metres), or specify None if not wanted in the scene
sceneParameters.obstacle0_StartingPosition = [0.2, -0.5]
sceneParameters.obstacle1_StartingPosition = None
sceneParameters.obstacle2_StartingPosition = None

# SET ROBOT PARAMETERS
robotParameters = RobotParameters()

# Drive Parameters
robotParameters.driveType = 'omni'# specify if using differential or omni drive system
robotParameters.minimumLinearSpeed = 0.04# minimum speed at which your robot can move forward in m / s
robotParameters.maximumLinearSpeed = 0.25# maximum speed at which your robot can move forward in m / s
robotParameters.driveSystemQuality = 1# specifies how good your drive system is from 0 to 1#(with 1 being able to drive in a perfectly straight line)

# Camera Parameters
robotParameters.cameraOrientation = 'landscape'# specifies the orientation of the camera
robotParameters.cameraDistanceFromRobotCenter = 0.1# distance between the camera and the center of the robot
robotParameters.cameraHeightFromFloor = 0.03# height of the camera relative to the floor in metres
robotParameters.cameraTilt = 0.1 # tilt of the camera in radians

# Vision Processing Parameters
robotParameters.maxBallDetectionDistance = 5# the maximum distance you can detect the ball in metres
robotParameters.maxGoalDetectionDistance = 2.5# the maximum distance you can detect the goals in metres
robotParameters.maxObstacleDetectionDistance = 1.5# the maximum distance you can detect the obstacles in metres

# Dribbler Parameters
robotParameters.dribblerQuality = 1# specifies how good your dribbler is from 0 to 1.0#(with 1.0 being awesome and 0 being non - existent)

# SET GLOBAL VARIABLES
headingRad = 0

# FUNCTIONS

# Get Attraction Field
def getAttractionField(goal_rad):
    # Field Map with size of 60 degrees scaled to 360 degrees
    goal_deg = round((math.degrees(goal_rad) + 30) * 6)
    attractionField = np.zeros(361)
    # At the goal_deg is max attraction, therefore set to 1
    attractionField[goal_deg] = 1
    gradient = 1/float(180);
    for angle in range (0, 181, 1):
        attractionField[Clip_Deg_360(goal_deg + angle)] = 1 - angle*gradient
        attractionField[Clip_Deg_360(goal_deg - angle)] = 1 - angle*gradient
    return attractionField

# Get Repulsion Field
def getRepulsionField(obstacles):
    
    repulsionField = np.zeros(361)
    r_radius = 0.18/2;
    
    for obstacle in obstacles:
        obs_range = obstacle[0]
        obs_bear = obstacle[1] # Radians
        obs_bear_deg = round((math.degrees(obs_bear) + 30) * 6)
        obs_width = 2 * r_radius + 0.5
        
        obs_dist = max(obs_width, obs_range)
        
        # Convert size of obstacle to size in polar coordinates
        # Take into account how far the obstacle is away from the robot
        obs_width_rad = math.asin(obs_width/obs_dist)
        obs_width_deg = int(round(Clip_Deg_360(math.degrees(obs_width_rad))))
        
        # Generate Repulsive field with respect to obstacle
        obs_effect = max(0, 1 - min(1, (obs_range - r_radius * 2)))
        repulsionField[obs_bear_deg] = obs_effect
        
        for angle in range (1, obs_width_deg, 1):
            repulsionField[Clip_Deg_360(obs_bear_deg - angle)] = max(repulsionField[Clip_Deg_360(obs_bear_deg + angle)], obs_effect)
            repulsionField[Clip_Deg_360(obs_bear_deg + angle)] = max(repulsionField[Clip_Deg_360(obs_bear_deg - angle)], obs_effect)
            
    return repulsionField
    
# Get Residual Field
def getResidualField(attractionField, repulsionField):
    residualField = attractionField - repulsionField
    return residualField

# Potential Field Generation
def generatePotentialField(goal, obstaclesRB):
    # Generate Attraction Field
    attractionField = np.zeros(361)
    attractionField = getAttractionField(goal)
    # Generate Obstacle Field
    repulsionField = np.zeros(361)
    if obstaclesRB != None:
        repulsionField = getRepulsionField(obstaclesRB)
    # Generate Residual Field
    residualField = getResidualField(attractionField, repulsionField)
    headingDeg = np.argmax(residualField)
    headingRad = math.radians(((headingDeg/6) - 30))
    print(headingDeg)
    # Plot the fields
    plt.clf()
    plt.figure(1)
    plt.subplot(311)
    plt.plot(attractionField)
    plt.xlim(0,360)
    plt.subplot(312)
    plt.plot(repulsionField)
    plt.xlim(0,360)
    plt.subplot(313)
    plt.plot(residualField)
    plt.xlim(0,360)
    plt.pause(0.05)
    plt.show()
    return headingRad

# Get Signed Angle
def getSignedDelta(angle_head, angle_robot):
    return angle_head
    
# Clip input angle to be between input range
def Clip_Deg_360(angle):
    while angle <= 0:
        angle = angle + 360
    while angle >= 360:
        angle = angle - 360
    return angle



# MAIN SCRIPT
if __name__ == '__main__':

  #Wrap everything in a try except case that catches KeyboardInterrupts.
  #In the exception catch code attempt to Stop the VREP Simulator so don 't have to Stop it manually when pressing CTRL+C
  try:
    soccerBotSim = VREP_SoccerBot('127.0.0.1', robotParameters, sceneParameters)
    soccerBotSim.StartSimulator()
    ballRB, blueRB, yellowRB, obstaclesRB = soccerBotSim.GetDetectedObjects()
    count = 0
    goal_found = False
    
    while True:
        
        #check to see if ball is in dribbler
        if soccerBotSim.BallInDribbler() == True:
            print("Ball Obtained")
            ballRB, blueRB, yellowRB, obstaclesRB = soccerBotSim.GetDetectedObjects()
            if goal_found == False:
                soccerBotSim.SetTargetVelocities(0, 0, 0.5)
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
                soccerBotSim.SetTargetVelocities(0.05, 0, headingRad)
                if bGoalRange < 0.65:
                    print("Shoot")
                    soccerBotSim.KickBall(0.5)
                    goal_found = False
        else:
            print("Looking for Ball")
            ballRB, blueRB, yellowRB, obstaclesRB = soccerBotSim.GetDetectedObjects()
            if ballRB == None:
                soccerBotSim.SetTargetVelocities(0, 0, 0.5)
            else:
                # Get Range and Bearing of Ball
                ballRange = ballRB[0]
                ballBearing = ballRB[1]
                # Generate Potential Field
                headingRad = generatePotentialField(ballBearing, obstaclesRB)
                soccerBotSim.SetTargetVelocities(0, 0, headingRad)
                soccerBotSim.SetTargetVelocities(0.05, 0, 0)
                
        
        soccerBotSim.UpdateBallPosition()

  except KeyboardInterrupt as e: #attempt to stop simulator so it restarts and don 't have to manually press the Stop button in VREP 
    soccerBotSim.StopSimulator()