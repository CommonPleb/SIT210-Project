# Imports the required libraries
from socket import *
from time import sleep
from datetime import datetime, timedelta
import PyNAU7802
import RPi.GPIO as GPIO
import board
import pwmio
from adafruit_motor import servo
import smbus2


def pulse():
    GPIO.output(VIBRATION, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(VIBRATION, GPIO.LOW)


def WeightOfFood():
    return scale.getWeight() - NOT_FOOD


# Opens the cover
def open():
    cover.angle = 90
    sleep(0.25)
    pulse()
    print("open")


# Closes the cover
def close():
    cover.angle = 175
    print("close")


# Code to notify of an error
def error(availFood):
    while availFood < weightThreshold:
        GPIO.output(PARTICLE_ERROR, GPIO.HIGH)
        availFood = WeightOfFood()
    GPIO.output(PARTICLE_ERROR, GPIO.LOW)
    return availFood


# Code to feed the cat
def feed(feedAfterNightMode, lastFed, availFood):
    if nightMode:
        feedAfterNightMode = True
        return feedAfterNightMode, lastFed, availFood
    lastFed = datetime.now()
    availFood = scale.getWeight() - NOT_FOOD
    errorCount = 0
    while availFood < weightThreshold:
        open()
        sleep(1)
        errorCount += 1
        availFood = WeightOfFood()
        if errorCount > 1:
            availFood = error(availFood)
    close()
    return feedAfterNightMode, lastFed, availFood


def CalculateNightMode():
    nightEndTime = datetime(datetime.now().year, datetime.now().month, datetime.now().day, clientNightEnd, 0, 0)
    if datetime.now() > nightEndTime:
        nightEndTime = nightEndTime + timedelta(days=1)

    nightStartTime = datetime(datetime.now().year, datetime.now().month, datetime.now().day, clientNightStart, 0, 0)
    while nightStartTime < nightEndTime:
        nightStartTime = nightStartTime + timedelta(days=1)
    nightStartTime = nightStartTime - timedelta(days=1)

    currentNightStart, currentNightEnd = clientNightStart, clientNightEnd
    return currentNightStart, currentNightEnd, nightEndTime, nightStartTime


# Define pins
VIBRATION = 16
COVER = 23
PARTICLE_ERROR = 17
PARTICLE_HEALTH = 27

# Create PWM for the servo
pwm = pwmio.PWMOut(board.D23, duty_cycle=0, frequency=50)
cover = servo.Servo(pwm, min_pulse=400, max_pulse=2400)

# Define starting variables
NOT_FOOD = 0.125
NIGHT_ON = 1
NIGHT_OFF = 0
HOURLY = 1
DAILY = 2
fedDaily = False
prevFeedTime = datetime.now()
currentDay = datetime.now().day
lastFed = datetime.now()
night = 0
clientNightStart = 0
clientNightEnd = 0
currentNightStart = 0
currentNightEnd = 0
nightStartTime = datetime.now()
nightEndTime = datetime.now()
nightMode = False
feedAfterNightMode = False

# All of the food platform is 125g. Screw, glue, bowl, wood
# Calibrates the scale
scale = PyNAU7802.NAU7802()
bus = smbus2.SMBus(1)
scale.begin(bus)
scale.calculateZeroOffset()
scale.calculateCalibrationFactor(NOT_FOOD)

availFood = WeightOfFood()

# Specifies the server IP and port number
ServerIP = "127.0.0.1"
ServerPort = 9999

# Initialises the GPIO
GPIO.setup(COVER, GPIO.OUT)
GPIO.setup(VIBRATION, GPIO.OUT)
GPIO.setup(PARTICLE_ERROR, GPIO.OUT)
GPIO.setup(PARTICLE_HEALTH, GPIO.OUT)
GPIO.output(PARTICLE_ERROR, GPIO.LOW)
GPIO.output(PARTICLE_HEALTH, GPIO.LOW)


close()

# Creates a UDP socket for the client to use
ClientSocket = socket(AF_INET, SOCK_DGRAM)

while True:
    # Send a message to the server to request the information
    Query = "Connect"
    ClientSocket.sendto(Query.encode(), (ServerIP, ServerPort))

    # Gets the required variables and assigns them
    Response, ServerAddress = ClientSocket.recvfrom(2048)
    currentMode, hour, weightThreshold, night, clientNightStart, clientNightEnd = Response.decode().split(";")
    currentMode, hour, weightThreshold, night, clientNightStart, clientNightEnd = int(currentMode), int(hour), int(weightThreshold), int(night), int(clientNightStart), int(clientNightEnd)

    # Checks to see if the date has changed to allow the cat to feed again if the mode is set to feed once a day
    if currentDay != datetime.now().day:
        fedDaily = False
        currentDay = datetime.now().day

    # Calculating night mode
    if night == NIGHT_ON:
        if currentNightStart != clientNightStart or currentNightEnd != clientNightEnd:
            currentNightStart, currentNightEnd, nightEndTime, nightStartTime = CalculateNightMode()
        elif not nightMode and currentNightStart == clientNightStart and currentNightEnd == clientNightEnd and datetime.now() > nightEndTime:
            nightStartTime = nightStartTime + timedelta(days=1)
            nightEndTime = nightEndTime + timedelta(days=1)

        if nightStartTime < datetime.now() < nightEndTime:
            nightMode = True
        else:
            nightMode = False
    else:
        nightMode = False

    # Code for feeding the cat once every few hours
    if currentMode == HOURLY:
        nextFeedTime = prevFeedTime + timedelta(hours=hour)
        if nextFeedTime > prevFeedTime:
            prevFeedTime = datetime.now()
            feedAfterNightMode, lastFed, availFood = feed(feedAfterNightMode, lastFed, availFood)

    # Code for feeding the cat once a day
    elif currentMode == DAILY:
        currentHour = datetime.now().hour
        if not fedDaily and currentHour == hour:
            fedDaily = True
            feedAfterNightMode, lastFed, availFood = feed(feedAfterNightMode, lastFed, availFood)
    else:
        print("Startup, waiting for input")

    # Perform a health alert of the cat has not eaten in over a day
    if lastFed + timedelta(days=1) < datetime.now():
        GPIO.output(PARTICLE_HEALTH, GPIO.HIGH)
    else:
        GPIO.output(PARTICLE_HEALTH, GPIO.LOW)



    if feedAfterNightMode and not nightMode:
        feedAfterNightMode, lastFed, availFood = feed(feedAfterNightMode, lastFed, availFood)
        feedAfterNightMode = False

    sleep(10)


# Vibration motor

# Delta time https://thispointer.com/add-minutes-to-current-time-in-python/

# Weight sensor library https://pypi.org/project/PyNAU7802/

# Enabling I2C interface https://www.mathworks.com/help/supportpkg/raspberrypiio/ref/enablei2c.html

# Servo code https://docs.circuitpython.org/projects/motor/en/latest/examples.html
