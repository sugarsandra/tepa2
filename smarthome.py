#! /usr/bin/env python
# -*- coding:Utf-8 -*-

# εγκατάσταση βιβλιοθηκων
import RPi.GPIO as GPIO
import time
import sys
from subprocess import call
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#δήλωση μεταβλητών για τις επαφές, το κουμπί εισόδου και τα leds
Right_Door=17
Left_Door = 18
button=27

red1=5            # led πρώτης θερμάστρας
red2=6            # led δεύτερης θερμάστρας
green=12       # led αφυγραντήρα

Left_open = None
Left_old = None
Right_open=None
Right_old=None

# Pins setup
GPIO.setup(red1,GPIO.OUT)
GPIO.setup(red2,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(Left_Door, GPIO.IN,pull_up_down = GPIO.PUD_UP)
GPIO.setup(Right_Door,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#module που ανάβει όλα τα Leds στην αρχή του προγράμματος   
def open_lights():
     GPIO.output(red1,1)
     GPIO.output(red2,1)
     GPIO.output(green,1)
     
# module για το σβήσιμο των Leds στην αρχή και στο τέλος του προγράμματος
def close_all_lights():
    GPIO.output(red1,0)
    GPIO.output(red2,0)
    GPIO.output(green,0)

# Module που δίνει την εντολή να ανάψει ο αφυγραντήρας
def open_dehumidifier():
    GPIO.output(green,1)
    
# Module που δίνει την εντολή να ανάψει η πρώτη θερμάστρα
def open_heater1():
    GPIO.output(red1,1)

 # Module που δίνει την εντολή να ανάψει η δεύτερη θερμάστρα
def open_heater2():
    GPIO.output(red2,1)
    
# Module ήχου κουδουνιού πόρτας 
def soundplay1():
    sound="/home/pi/Music/Doorbell.wav" 
    call(["aplay",sound])

# Module ήχου alarm μπαλκονόπορτας
def soundplay2():
    sound="/home/pi/Desktop/wav/Industrial.wav" 
    call(["aplay",sound])

#Module ελέγχου αριστερής/δεξιάς μπαλκονόπορτας μέσω μαγνητικών επαφών
def checkdoors(Left_open,Right_open):
    global Left_old
    global Right_old
    if (Left_open and(Left_open !=Left_old)):
        print("Left Door Opened")
        soundplay2()
    elif (Left_open != Left_old):
        print("Left Door Closed")
    if (Right_open and (Right_open !=Right_old)):
        print("Right Door Opened")
        soundplay2()
    elif (Right_open != Right_old):
        print("Right Door Closed")

# Module ελέγχου θερμοκρασίας / υγρασίας 
def check_hum_temp():
    humidity,temperature=Adafruit_DHT.read_retry(11,4,retries=5, delay_seconds=.5)
    if humidity is not None and temperature is not None:
        print('Temp:{0:0.1f} C  Humidity:{1:0.1f} %'.format(temperature,humidity))
        if (-10.0< temperature<20.0):
            open_heater1()
            open_heater2()
            if (humidity>25.0):
                open_dehumidifier()
        elif(20.1<temperature<28.0):
            open_heater1()
            if (humidity>25.0):
                open_dehumidifier()
        elif (28.1<temperature<50.0):
            if (humidity>25.0):
                open_dehumidifier()
        else:
            print("No data. Please try again!")
    
try:
    open_lights()
    time.sleep(2)
    call(['espeak "Welcome to the world of Robots" 2>/dev/null'], shell=True)# δημιουργία φωνητικού μηνύματος
    close_all_lights()
    while True:
        check_hum_temp()
        Left_old=Left_open
        Right_old=Right_open
        # διαβάζει από μαγνητικές επαφές
        Left_open = GPIO.input(Left_Door) 
        Right_open=GPIO.input(Right_Door)
        checkdoors(Left_open,Right_open)
        # διαβάζει από κουμπί εξώπορτας
        if not GPIO.input(button):
            soundplay1()
except KeyboardInterrupt:
    close_all_lights()
    GPIO.cleanup()
    sys.exit(0)
except:
    print(sys.exc_info())
