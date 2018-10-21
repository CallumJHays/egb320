import RPi.GPIO as GPIO
import time


class KickerSystem():

    KICK_SLEEP = 0.15 # seconds after kicking before resuming function

    def __init__(self):
        self.DribDIR = 21
        self.DribENA = 20
        self.KICKER_PIN = 17

        GPIO.setup(self.DribDIR, GPIO.OUT)
        GPIO.setup(self.DribENA, GPIO.OUT)
        GPIO.setup(self.KICKER_PIN, GPIO.OUT)

        self.pwmDRIB = GPIO.PWM(self.DribENA, 500)
    
    def start_dribbling(self):
        self.pwmDRIB.start(90)

    
    def stop_dribbling(self):
        self.pwmDRIB.start(0)

    def kick(self):
        GPIO.output(self.KICKER_PIN, GPIO.HIGH)
        time.sleep(self.KICK_SLEEP)
        GPIO.output(self.KICKER_PIN, GPIO.LOW)