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




# Obstacle Avoidance Procedure (1 Obstacle Input)


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
        
        
  except KeyboardInterrupt as e: #attempt to stop simulator so it restarts and don 't have to manually press the Stop button in VREP 
    soccerBotSim.StopSimulator()