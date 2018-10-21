import math
import RPi.GPIO as GPIO # Import GPIO Modual


class DriveSystem():

    SPEED_TUNER_CONSTANT = 0.5
    ROTATION_VEL_2_ACC_TUNER_CONSTANT = 0.5
    LENGTH_CENTER_2_WHEEL = 0.08 # m


    def __init__(self, speed_modifier):
        self.speed_modifier = speed_modifier
        GPIO.setmode(GPIO.BCM) # Set the GPIO Pin Nameing Convention to BCM
        # Setting up motor Phase and Enable Outputs
        # starting Left of kicker wheels A, B, C finishing with Right of Kicker
        self.EnableA = 13
        self.EnableB = 5
        self.EnableC = 19
        self.DIRA = 6
        self.DIRB = 12
        self.DIRC = 26
        self.MODE = 16

        self.UpdateMotors = False
        self.threshold = 0.1

        GPIO.setup(self.EnableA,GPIO.OUT)
        GPIO.setup(self.EnableB,GPIO.OUT) # ENABLE
        GPIO.setup(self.EnableC,GPIO.OUT)
        GPIO.setup(self.DIRA,GPIO.OUT)
        GPIO.setup(self.DIRB,GPIO.OUT) # PHASE
        GPIO.setup(self.DIRC,GPIO.OUT)
        GPIO.setup(self.MODE,GPIO.OUT)
        GPIO.output(self.MODE,GPIO.HIGH) # Set MODE pin HIGH on all Drivers - Phase/Enable mode

        # Settingup PWM
        self.pwmA = GPIO.PWM(self.EnableA, 500) # Initiates PWM signal - Phase
        self.pwmB = GPIO.PWM(self.EnableB, 500) # Initiates PWM signal - Phase
        self.pwmC = GPIO.PWM(self.EnableC, 500) # Initiates PWM signal - Phase
    

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
        self.pwmA.start(DutyA)
        if a < 0:
            GPIO.output(self.DIRA,0)
        else:
            GPIO.output(self.DIRA,1)
        # BACK Wheel - working
        self.pwmB.start(DutyB)
        if b < 0:
            GPIO.output(self.DIRB,0)
        else:
            GPIO.output(self.DIRB,1)

        # RIGHT Wheel - working
        self.pwmC.start(DutyC)
        if c < 0:
            GPIO.output(self.DIRC,1)
        else:
            GPIO.output(self.DIRC,0)