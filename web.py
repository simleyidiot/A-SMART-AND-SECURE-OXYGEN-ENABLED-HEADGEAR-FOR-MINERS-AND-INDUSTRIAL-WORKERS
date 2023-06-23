from flask import render_template, url_for, request
from gpiozero import Servo
import Adafruit_DHT
import pynmea2  
import serial
import string
import RPi.GPIO as GPIO
import time


pin=12
sensor = Adafruit_DHT.DHT11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN)
GPIO.setup(17,GPIO.IN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(2,GPIO.OUT)
GPIO.output(2,GPIO.HIGH)
Buzzer =21
valve = 27



from flask import Flask
app = Flask(__name__)

lat = "0.0"
lng = "0.0"
humi = 0
temp = 0
gas = "No harmful gas detected"

@app.route('/')

def index():
    harmful()
    return render_template("base.html",data={"lati":str(lat),"long":str(lng),"detect":str(gas),"tem":temp,"hum":humi})
       

def harmful():
    global gas
    gas_alert_7=GPIO.input(18)
    gas_alert_135=GPIO.input(17)
    if gas_alert_7==0 and gas_alert_135==0 :
        gas="Gas Detected"   
        gps()
        sensor_dht11()
        
    elif gas_alert_7==0 or gas_alert_135==0: 
        gas="Gas Detected"    
        gps()
        sensor_dht11()
        
      
    elif GPIO.input(16) == GPIO.HIGH:
        gas="Alert,Button was pushed!"  
        gps()
        sensor_dht11()
        
    else:
        gas="No Detection" 
        return gas
             
def gps():
    global lat,lng
    ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
    dataout = pynmea2.NMEAStreamReader()
    newdata = ser.readline()
    if '$GNGGA' in str(newdata):
        newmsg = pynmea2.parse(newdata.decode('utf-8'))
        lat = str(newmsg.latitude)
        lng =str(newmsg.longitude)
        print(lat,lng)
    else:
        lat="11.115216833"
        lng="77.188559166"    
       
def sensor_dht11():
     global humi,temp
     humidity, temperature = Adafruit_DHT.read(sensor, pin)
     if humidity is not None and temperature is not None:
        humi=humidity
        temp=temperature 
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80,debug=True)
    
