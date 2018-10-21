import numpy as np
import math


class NavigationSystem():

    GOAL_P = 0.5
    MAX_ROBOT_ROT = 1
    MAX_ROBOT_VEL = 0.05


    def __init__(self, vision_system, drive_system, kicker_dribbler, debug_print):
        self.vision_system = vision_system
        self.drive_system = drive_system
        self.headingRad = 0
        self.goal_found = False
        self.lastHeading = 0.4
        self.kicker_dribbler = kicker_dribbler
        self.debug_print = debug_print


    def update(self):
        ballRB, blueRB, yellowRB, obstaclesRB = self.get_vision_results_vrep_format()
        BALL_IN_DRIBBLER_RB = (0.03, 0.3)
        ball_in_dribbler = ballRB and ballRB[0] < BALL_IN_DRIBBLER_RB and abs(ballRB) < BALL_IN_DRIBBLER_RB[1]

        # perform PID control on the drive system#check to see if ball is in dribbler
        if ball_in_dribbler: # soccerBotSim.BallInDribbler() == True:
            self.kicker_dribbler.start_dribbling()
            self.debug_print("Ball Obtained")
            if self.goal_found:
                self.drive_system.setTargetVelocities(0, 0, 0.5)
                if blueRB != None:
                    bGoalRange = blueRB[0]
                    bGoalBearing = blueRB[1]
                    self.goal_found = True
                    self.debug_print("Goal Found")
            else:
                self.debug_print("Heading towards Goal")
                if blueRB != None:
                    bGoalRange = blueRB[0]
                    bGoalBearing = blueRB[1]
                else:
                    self.goal_found = False
                self.headingRad = self.generatePotentialField(bGoalBearing, obstaclesRB)
                if obstaclesRB != None:
                    if len(obstaclesRB) == 1:
                        self.debug_print("1 Obstacle")
                        self.avoidSingleObstacle(bGoalRange, bGoalBearing, obstaclesRB, self.headingRad)
                    if len(obstaclesRB) == 2:
                        self.debug_print("2 Obstacle")
                        self.avoidDoubleObstacle(bGoalRange, bGoalBearing, obstaclesRB, self.headingRad)
                else:
                    desired_rot_vel = min(self.MAX_ROBOT_ROT, max(-self.MAX_ROBOT_ROT, self.headingRad * self.GOAL_P))
                    desired_vel = self.MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel)/self.MAX_ROBOT_ROT)
                    self.drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)
                if bGoalRange < 0.65:
                    self.debug_print("Shoot")
                    self.kicker_dribbler.kick()
                    self.goal_found = False
                    self.lastHeading = 0.4
        else:
            self.kicker_dribbler.stop_dribbling()
            self.debug_print("Looking for Ball")
            if ballRB == None:
                self.debug_print("Cant see ball, rotating...")
                self.drive_system.setTargetVelocities(0, 0, self.lastHeading + 0.1)
                self.lastHeading = 0.4
            else:
                self.debug_print("Ball in sight! chasing it down")
                # Get Range and Bearing of Ball
                ballRange = ballRB[0]
                ballBearing = ballRB[1]
                self.lastHeading = ballBearing
                # Generate Potential Field
                self.debug_print("Generating potential field")
                self.headingRad = self.generatePotentialField(ballBearing, obstaclesRB)
                if obstaclesRB != None:
                    if len(obstaclesRB) == 1:
                        self.debug_print("1 Obstacle")
                        self.avoidSingleObstacle(ballRange, ballBearing, obstaclesRB, self.headingRad)
                    if len(obstaclesRB) == 2:
                        self.debug_print("2 Obstacle")
                        self.avoidDoubleObstacle(ballRange, ballBearing, obstaclesRB, self.headingRad)
                else:
                    desired_rot_vel = min(self.MAX_ROBOT_ROT, max(-self.MAX_ROBOT_ROT, self.headingRad * self.GOAL_P))
                    desired_vel = self.MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel) / self.MAX_ROBOT_ROT)
                    self.drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)


    def get_vision_results_vrep_format(self):
        objs = self.vision_system.objects_to_track # for shorthand

        def vrep_format(bearings_distances, multi=False):
            if any(bearings_distances):
                if multi:
                    return bearings_distances[::-1]
                else:
                    return bearings_distances[0][::-1]
            else:
                return None

        return (
            vrep_format(objs["ball"].bearings_distances),
            vrep_format(objs["blue_goal"].bearings_distances),
            vrep_format(objs["yellow_goal"].bearings_distances),
            vrep_format(objs["obstacle"].bearings_distances, multi=True),
        )

        
    def avoidSingleObstacle(self, goalRange, goalBearing, obstaclesRB, headingRad):
        obstacle = obstaclesRB[0]
        obs_range = obstacle[0]
        obs_bear = obstacle[1] # Radians
        desired_rot_vel = min(self.MAX_ROBOT_ROT, max(-self.MAX_ROBOT_ROT, self.headingRad * self.GOAL_P))
        desired_vel = self.MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel) / self.MAX_ROBOT_ROT)
        desired_velx = desired_vel * math.sin(desired_rot_vel)
        desired_vely = desired_vel * math.cos(desired_rot_vel)
        if goalRange > obs_range and obs_range < 0.4:
            if goalBearing < 0 and goalBearing > obs_bear:
                self.drive_system.setTargetVelocities(desired_velx, desired_vely, -desired_rot_vel)
            elif goalBearing < 0 and goalBearing < obs_bear:
                self.drive_system.setTargetVelocities(-desired_velx, -desired_vely, desired_rot_vel)
            elif goalBearing > 0 and goalBearing > obs_bear:
                self.drive_system.setTargetVelocities(desired_velx, desired_vely, -desired_rot_vel)
            elif goalBearing > 0 and goalBearing < obs_bear:
                self.drive_system.setTargetVelocities(-desired_velx, -desired_vely, desired_rot_vel)
        else:
            self.drive_system.setTargetVelocities(desired_vel, 0, desired_rot_vel)

    def avoidDoubleObstacle(self, goalRange, goalBearing, obstaclesRB, headingRad):
        obstacle1 = obstaclesRB[0]
        obstacle2 = obstaclesRB[1]
        obs_range1 = obstacle1[0]
        obs_bear1 = obstacle1[1] # Radians
        obs_range2 = obstacle2[0]
        obs_bear2 = obstacle2[1] # Radians
        obs_x1 = obs_range1 * math.sin(obs_bear1)
        obs_y1 = obs_range1 * math.cos(obs_bear1)
        obs_x2 = obs_range2 * math.sin(obs_bear2)
        obs_y2 = obs_range2 * math.cos(obs_bear2)
        dist_obstaclesx = abs(obs_x1 - obs_x2)
        dist_obstaclesy = abs(obs_y1 - obs_y2)
        dist_obstacle = math.sqrt(dist_obstaclesx * dist_obstaclesx + dist_obstaclesy * dist_obstaclesy)
        chosen_obstacle_range, chosen_obstacle_bear = closestObstacle(obs_range1, obs_bear1, obs_range2, obs_bear2)
        desired_rot_vel = min(self.MAX_ROBOT_ROT, max(-self.MAX_ROBOT_ROT, self.headingRad * self.GOAL_P))
        desired_vel = self.MAX_ROBOT_VEL * (1.0 - 0.9*abs(desired_rot_vel) / self.MAX_ROBOT_ROT)
        if dist_obstacle > 0.4 and (dist_obstaclesy > 0.4 or dist_obstaclesx > 0.4):
            obstacle = [[chosen_obstacle_range, chosen_obstacle_bear]]
            self.avoidSingleObstacle(goalRange, goalBearing, obstacle, headingRad)
        elif dist_obstacle < 0.5:
            self.drive_system.setTargetVelocities.SetTargetVelocities(desired_vel, 0, chosen_obstacle_bear)
    
    # Get Attraction Field
    def getAttractionField(self, goal_rad):
        # Field Map with size of 60 degrees scaled to 360 degrees
        goal_deg = round((math.degrees(goal_rad) + 30))
        attractionField = np.zeros(61)
        # At the goal_deg is max attraction, therefore set to 1
        attractionField[goal_deg] = 1
        gradient = 1/float(60)
        for angle in range (0, 31, 1):
            attractionField[Clip_Deg_60(goal_deg + angle)] = 1 - angle*gradient
            attractionField[Clip_Deg_60(goal_deg - angle)] = 1 - angle*gradient
        return attractionField


    # Get Repulsion Field
    def getRepulsionField(self, obstacles):
        
        repulsionField = np.zeros(61)
        r_radius = 0.18/2
        
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
    def getResidualField(self, attractionField, repulsionField):
        residualField = attractionField - repulsionField
        return residualField


    # Potential Field Generation
    def generatePotentialField(self, goal, obstaclesRB):
        # Generate Attraction Field
        attractionField = np.zeros(61)
        attractionField = self.getAttractionField(goal)
        # Generate Obstacle Field
        repulsionField = np.zeros(61)
        if obstaclesRB != None:
            repulsionField = self.getRepulsionField(obstaclesRB)
        # Generate Residual Field
        residualField = self.getResidualField(attractionField, repulsionField)
        headingDeg = np.argmax(residualField)
        headingRad = math.radians(headingDeg - 30)
        #self.debug_print(headingDeg)
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

# Returns the closet obstacle
def closestObstacle(obs_range1, obs_bear1, obs_range2, obs_bear2):
    if obs_range1 > obs_range2:
        return obs_range2, obs_bear2
    else:
        return obs_range1, obs_bear1