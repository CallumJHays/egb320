import math
# catch all but could be bad - we'll see
from .OGMotorCode import *


class DriveSystem():

    SPEED_TUNER_CONSTANT = 0.5
    ROTATION_VEL_2_ACC_TUNER_CONSTANT = 0.5
    LENGTH_CENTER_2_WHEEL = 0.08 # m


    def __init__(self, speed_modifier):
        self.speed_modifier = speed_modifier
    

    def setTargetVelocities(self, velx, vely, velRot):
        V = self.SPEED_TUNER_CONSTANT * math.sqrt(math.pow(velx, 2), math.pow(vely, 2))
        theta = math.tan(vely / velx)
        A = self.ROTATION_VEL_2_ACC_TUNER_CONSTANT * velRot
        L = self.LENGTH_CENTER_2_WHEEL

        self.DriveMotors(
            self.speed_modifier * abs(V)*(-(math.sqrt(3)/2)*math.cos(theta) + 0.5 * math.sin(theta)) + A * L,
            self.speed_modifier * -abs(V)*(math.sin(theta)) + A*L,
            self.speed_modifier * abs(V)*((math.sqrt(3)/2)*math.cos(theta) + 0.5 * math.sin(theta)) + A * L
        )

    
    def DriveMotors(self, a, b, c): # Converts & Caps Individual Motor Values at PWM of 100

        # Caps Duty Cycle at 100 with min value of 50
        DutyA = (abs(a)*200) # (abs(a)*130)+30
        DutyB = (abs(b)*200)
        DutyC = (abs(c)*200)

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