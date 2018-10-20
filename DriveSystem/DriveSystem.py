# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 22:33:29 2018

@author: Phoenix Seybold
"""

import RPi.GPIO as GPIO # Import GPIO Modual
import time # Import Time Modual
import math # Math Modual
import pygame # Modual to Utilize PS3 Controller

# Initialise the pygame library
pygame.init()

# Connect to the first JoyStick
j = pygame.joystick.Joystick(0)
j.init()

""" will be using GPIO's
20 = blue wire = High - Low Direction control
21 = purple wire = PWM Duty Cycle
Voltage of motor max = nominal battery 7.4V

Mode Pin = 16 brown Wire. - FOR ALL MOTOR DRIVERS


class motors
    int PHASE
    int ENABLE

"""
GPIO.setmode(GPIO.BCM) # Set the GPIO Pin Nameing Convention to BCM
# Setsting up motor Phase and Enable Outputs
# Left of kicker
EnableA = 13
EnableB = 5
EnableC = 19
DIRA = 6
DIRB = 16
DIRC = 26
MODE = 16

UpdateMotors = False
threshold = 0.1

GPIO.setup(EnableA,GPIO.OUT)
GPIO.setup(EnableB,GPIO.OUT) # ENABLE
GPIO.setup(EnableC,GPIO.OUT)
GPIO.setup(DIRA,GPIO.OUT)
GPIO.setup(DIRB,GPIO.OUT) # PHASE
GPIO.setup(DIRC,GPIO.OUT)
GPIO.setup(MODE,GPIO.OUT)
GPIO.output(MODE,GPIO.HIGH) # Set MODE pin HIGH on all Drivers - Phase/Enable mode

# Settingup PWM

pwmA = GPIO.PWM(13, 500) # Initiates PWM signal - Phase
pwmB = GPIO.PWM(21, 500) # Initiates PWM signal - Phase
pwmC = GPIO.PWM(19, 500) # Initiates PWM signal - Phase

class DriveSystem(object):
    
    # Class Constructor
    def __init__(self, xvel, yvel, rotvel):
        self.xvel = xvel
        self.yvel = yvel
        self.rotvel = rotvel
    
    def stop(self):
        raw_input('press a key to stop:')
        pwmA.stop() # Stops PWM
        pwmB.stop() # Stops PWM
        pwmC.stop() # Stops PWM
        GPIO.cleanup()
        quit()
    
    def setTargetVelocities(self, xvel, yvel, rotvel)
        direction = math.atan(yvel/xvel)
        speed = math.sqrt(xvel * xvel + yvel * yvel)
        SpeedModifier = 1
        MotorControl(direction, speed, rotvel) # angle = ControlAngle(j.get_axis(0),j.get_axis(1))
        DriveMotors(MotorControl.Va * SpeedModifier, MotorControl.Vb * SpeedModifier, MotorControl.Vc * SpeedModifier)
        

def TestMotorSetup():
 pwmA.start(50)
 GPIO.output(DIRA,1)
 time.sleep(2)
 pwmA.stop()

 pwmB.start(50)
 GPIO.output(DIRB,1)
 time.sleep(2)
 pwmB.stop()

 pwmC.start(50)
 GPIO.output(DIRC,0)
 time.sleep(2)
 pwmC.stop()

def MotorControl(Angle, Speed, RotationalA):
 theta = Angle # converts Input Radians to Degrees
 V = Speed
 A = RotationalA
 L = 0.08 # Length from center to wheels

 MotorControl.Va = abs(V)*(-(math.sqrt(3)/2)*math.cos(theta) + 0.5*math.sin(theta)) + A*L
 MotorControl.Vb = -abs(V)*(math.sin(theta)) + A*L
 MotorControl.Vc = abs(V)*((math.sqrt(3)/2)*math.cos(theta) + 0.5*math.sin(theta)) + A*L
 print(MotorControl.Va, MotorControl.Vb, MotorControl.Vc)
 
def DriveMotors(A, B, C):
 a=A
 b=B
 c=C   
            
 DutyA = (abs(a)*200) # (abs(a)*130)+30
 DutyB = (abs(b)*200)
 DutyC = (abs(c)*200)
 if DutyA >= 100:
     DutyA = 100
 if DutyB >= 100:
     DutyB = 100
 if DutyC >= 100:
     DutyC = 100

 
 print(DutyA,DutyB,DutyC)

           # LEFT Wheel - working
 pwmA.start(DutyA)
 if a < 0:
    GPIO.output(6,0)
 else:
    GPIO.output(6,1)
# BACK Wheel - working
 pwmB.start(DutyB)
 if b < 0:
    GPIO.output(20,0)
 else:
    GPIO.output(20,1)

# RIGHT Wheel - working
 pwmC.start(DutyC)
 if c < 0:
    GPIO.output(26,1)
 else:
    GPIO.output(26,0)
 
def ControlAngle(Horizontal, Vertical):
    H = Horizontal
    V = Vertical # * (-1)
    
    Rad = math.atan2(H,V)
    if Rad<0: # switch Degrees -180 to 180 -> 360
        Rad = (Rad)+2*math.pi
# Correct Orientation for Controller
        
        """
    if Rad<=(math.pi/2):
        Rad = Rad+(3/(2*math.pi))
    if Rad>=(math.pi/2):
        Rad = Rad-(math.pi/2)
        """
    
    print(math.degrees(Rad))
    return(Rad)

def Rotate(ControlValue):
 if ControlValue>0.2: # Rotate Right
    GPIO.output(DIRA,1)
    GPIO.output(DIRB,1)
    GPIO.output(DIRC,0)
    pwmA.start(60)
    pwmB.start(60)
    pwmC.start(60)
    
 if ControlValue<-0.2: # Rotate Left
    GPIO.output(DIRA,0)
    GPIO.output(DIRB,0)
    GPIO.output(DIRC,1)
    pwmA.start(60)
    pwmB.start(60)
    pwmC.start(60)
    return
    
 
    
def BrakeMotors():
    pwmA.start(0)
    pwmB.start(0)
    pwmC.start(0)
    
# Quickly Test All Motors are Turning in correct direction at speed
TestMotorSetup()  

def drive(self):

# Move Forward
# while True:
#     try:
#     # Check for any queued events and then process each one
#         for event in pygame.event.get():
#           UpdateMotors = False

#           # Check if one of the joysticks has moved
#           if j.get_axis(0)>threshold or j.get_axis(0)<(threshold*-1) or j.get_axis(1)>threshold or j.get_axis(1)<(threshold*-1):
#                   UpdateMotors = True
              
#         if UpdateMotors == True:
            
#             # Controller Inputs
#             #SpeedModifier = 0.25 * j.get_axis(13) + 0.75
#             #Direction = ControlAngle(j.get_axis(0),j.get_axis(1))\

#             MotorControl((Direction),0.5 ,j.get_axis(2)) # angle = ControlAngle(j.get_axis(0),j.get_axis(1))
#             DriveMotors(MotorControl.Va * SpeedModifier, MotorControl.Vb * SpeedModifier, MotorControl.Vc * SpeedModifier)
#             print(MotorControl.Va * SpeedModifier, MotorControl.Vb * SpeedModifier, MotorControl.Vc * SpeedModifier)
            
#         if j.get_axis(14) > (-0.2) and (j.get_axis(0)<threshold and j.get_axis(0)<(threshold*-1)):
            
#             Rotate(j.get_axis(2)) # Rotate to second joystick Horizontal input
    
            
#         elif UpdateMotors == False:
#             BrakeMotors()
#         time.sleep(0.1) # Debuging Perposes - Limits Loop speed to make reading console easier
#     except(KeyboardInterrupt):
#         raw_input('press a key to stop:')
#         pwmA.stop() # Stops PWM
#         pwmB.stop() # Stops PWM
#         pwmC.stop() # Stops PWM
#         GPIO.cleanup()
#         quit()
