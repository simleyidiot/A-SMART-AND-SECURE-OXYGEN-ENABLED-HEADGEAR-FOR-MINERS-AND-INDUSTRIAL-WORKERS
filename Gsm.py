import Adafruit_DHT
import pynmea2  
import string
import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

def getResponse(cmd, reply, timeout):
    cmd = cmd + '\r'
    print('CPU' + ':' + cmd)
    ser.write(bytes(cmd, 'utf-8'))
    time.sleep(0.01)
    for i in range(0, timeout):
        in_msg = ser.readline()
        in_msg = in_msg.decode('utf-8').strip()
        time.sleep(0.01)
        ans = in_msg.find(reply)
        if(ans != -1):
            i = timeout
    print('GSM' + ':' + in_msg)
    time.sleep(0.5)

def gsmPrint(cmd, timeout):
    cmd = cmd + '\r'
    print('CPU' + ':' + cmd)
    ser.write(bytes(cmd, 'utf-8'))
    time.sleep(0.01)
    for i in range(0, timeout):
        in_msg = ser.readline()
        in_msg = in_msg.decode('utf-8').strip()
        time.sleep(0.01)
        if(len(in_msg) > 0): # something in reply
            i = timeout
    print('GSM' + ':' + in_msg)
    time.sleep(0.5)

def gsmEndcommand():
    ser.write(bytes(chr(26), 'utf-8'))
    time.sleep(1)
    in_msg = ser.readline()
    in_msg = in_msg.decode('utf-8').strip()
    print('GSM' + ':' + in_msg)
    time.sleep(1)

def send_message(number, message):
    getResponse('AT', 'OK', 2)
    getResponse('AT+CMGF=1', 'OK', 2)
    cmd = f'AT+CMGS={number}'
    getResponse(cmd, '>', 2)
    gsmPrint(message, 2)
    gsmEndcommand()

def send_message_to_all(numbers, message):
    for number in numbers:
        send_message(number, message)

def msg():
    numbers = [ '"+919688309024"', '"+919976705472"', '"+919344149403"','"+919865519133"']
    message = f"{gas}\n Live Location:https://www.google.com/maps?q={lat},{lng}\n Temperature: {temp}C\nHumidity: {humi}%"
    send_message_to_all(numbers, message)





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


lat = '0.0'
lng = '0.0'
humi = 0
temp = 0
gas = "No harmful gas detected"


def harmful():
    global gas
    gas_alert_7=GPIO.input(18)
    gas_alert_135=GPIO.input(17)
    
    if gas_alert_7==0 and gas_alert_135==0 :
        gas="Gas Detected"
        GPIO.setup(Buzzer,GPIO.OUT)
        GPIO.output(Buzzer,GPIO.HIGH) 
        time.sleep(2)
        GPIO.output(Buzzer,GPIO.LOW) 
        GPIO.setup(valve,GPIO.OUT)
        GPIO.output(valve,GPIO.HIGH)    
        gps()
        sensor_dht11()
        msg()
    elif gas_alert_7==0 or gas_alert_135==0: 
        gas="Gas Detected"
        GPIO.setup(Buzzer,GPIO.OUT)
        GPIO.output(Buzzer,GPIO.HIGH) 
        time.sleep(2)
        GPIO.output(Buzzer,GPIO.LOW) 
        GPIO.setup(valve,GPIO.OUT)
        GPIO.output(valve,GPIO.HIGH)    
        gps()
        sensor_dht11()
        msg()
      
    elif GPIO.input(16) == GPIO.HIGH:
        gas="Alert,Button was pushed!"  
        gps()
        sensor_dht11()
        msg()

    else:
        gas="No Detection" 
        GPIO.setup(Buzzer,GPIO.OUT)
        GPIO.output(Buzzer,GPIO.LOW)
        time.sleep(1)   
        GPIO.setup(valve,GPIO.OUT)
        GPIO.output(valve,GPIO.LOW)
       
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
         

while True:
    harmful()
    time.sleep(1)        
