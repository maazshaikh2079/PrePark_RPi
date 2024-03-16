import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
from time import sleep

GPIO.setmode(GPIO.BCM)

servo_pin = 17
GPIO.setup(servo_pin, GPIO.OUT)

factory = PiGPIOFactory()

servo = AngularServo(servo_pin, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory)

try:
    while True:
        servo.angle = -90
        print("Servo at -90 degrees")
        sleep(2)

        servo.angle = 0
        print("Servo at 0 degrees")
        sleep(2)

        servo.angle = 90
        print("Servo at 90 degrees")
        sleep(2)

except KeyboardInterrupt:
   GPIO.cleanup()
