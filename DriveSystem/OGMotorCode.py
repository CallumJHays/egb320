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

    pwmDRIB.start(50)
    GPIO.output(DribDIR,0)
    time.sleep(2)
    pwmDRIB.stop()

def MotorControl(Angle, Speed, Acceleration): # This Calculates the velocities of three wheels to travel at direction Theta Without Spining
    # if V = 0, Robot will rotate at Velocity of A.
    # else Velocity of A will be added to V for simultanious Rotation and Translation 
    theta = Angle # converts Input Radians to Degrees
    V = Speed
    A = Acceleration
    L = 0.08 # Length from center to wheels

    MotorControl.Va = abs(V)*(-(math.sqrt(3)/2)*math.cos(theta) + 0.5*math.sin(theta)) + A*L
    MotorControl.Vb = -abs(V)*(math.sin(theta)) + A*L
    MotorControl.Vc = abs(V)*((math.sqrt(3)/2)*math.cos(theta) + 0.5*math.sin(theta)) + A*L
    print(MotorControl.Va, MotorControl.Vb, MotorControl.Vc)
 
def DriveMotors(A, B, C): # Converts & Caps Individual Motor Values at PWM of 100

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
    # Below: Sets the - Velocities to flip direction of rotating wheel
    # LEFT Wheel - working
    pwmA.start(DutyA)
    if a < 0:
    GPIO.output(DIRA,0)
    else:
    GPIO.output(DIRA,1)
    # BACK Wheel - working
    pwmB.start(DutyB)
    if b < 0:
    GPIO.output(DIRB,0)
    else:
    GPIO.output(DIRB,1)

    # RIGHT Wheel - working
    pwmC.start(DutyC)
    if c < 0:
    GPIO.output(DIRC,1)
    else:
    GPIO.output(DIRC,0)
 
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
    
 
    
def BrakeMotors(): # Turns Motors off if Nothing is being called.
    pwmA.start(0)
    pwmB.start(0)
    pwmC.start(0)
    
def Dribbler(On):
    if On == True:
        pwmDRIB.start(80)
    else:
        pwmDRIB.start(0)
    
# # Quickly Test All Motors are Turning in correct direction at speed
# TestMotorSetup()  

# Move Forward
if __name__ == "__main__":
    while True:
        try:
        # Check for any queued events and then process each one
            for event in pygame.event.get():
                UpdateMotors = False

            # Check if one of the joysticks has moved
            if j.get_axis(0)>threshold or j.get_axis(0)<(threshold*-1) or j.get_axis(1)>threshold or j.get_axis(1)<(threshold*-1):
                    UpdateMotors = True
                
            if UpdateMotors == True:
                
                
                SpeedModifier = 0.25 * j.get_axis(13) + 0.75
                Direction = ControlAngle(j.get_axis(0),j.get_axis(1)*4) # takes x and y inputs from joystick
                MotorControl((Direction),0.5 ,j.get_axis(2)*4) # angle = ControlAngle(j.get_axis(0),j.get_axis(1))
                DriveMotors(MotorControl.Va * SpeedModifier, MotorControl.Vb * SpeedModifier, MotorControl.Vc * SpeedModifier)
                print(MotorControl.Va * SpeedModifier, MotorControl.Vb * SpeedModifier, MotorControl.Vc * SpeedModifier)
                
            if j.get_axis(14) > (-0.2):
                Dribbler(True)
            else:
                Dribbler(False)    
        
                
            if UpdateMotors == False:
                BrakeMotors()
            time.sleep(0.1) # Debuging Perposes - Limits Loop speed to make reading console easier
        except(KeyboardInterrupt): # Turn off all output signals, Prevents 
            raw_input('press a key to stop:')
            pwmA.stop() # Stops PWM
            pwmB.stop() # Stops PWM
            pwmC.stop() # Stops PWM
            pwmDRIB.stop() # Stops Dribbler PWM
            GPIO.cleanup()
            quit()
