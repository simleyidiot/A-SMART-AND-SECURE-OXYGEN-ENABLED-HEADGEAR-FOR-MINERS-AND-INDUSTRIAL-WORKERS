import mysql.connector
import Adafruit_DHT
import pynmea2  
import serial
import RPi.GPIO as GPIO
import time


# MySQL database configuration
db_config = {
    'user': 'Bala',
    'password': 'bala1234',
    'host': 'localhost',
    'database': 'helmetdb'
}

pin = 12
sensor = Adafruit_DHT.DHT11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN)
GPIO.setup(17,GPIO.IN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(2,GPIO.OUT)
GPIO.output(2,GPIO.HIGH)


lat = "0.0"
lng = "0.0"
humi = "0"
temp = "0"
gas = "no gas"
id = 0

    
def harmful():
    global gas
    gas_alert_7=GPIO.input(18)
    gas_alert_135=GPIO.input(17)
    if gas_alert_7==0 and gas_alert_135==0 :
        gas="Gas Detected"  
        gps()
        sensor_dht11()
        add_to_database()
        
    elif gas_alert_7==0 or gas_alert_135==0: 
        gas="Gas Detected"  
        gps()
        sensor_dht11()
        add_to_database()
        
      
    elif GPIO.input(16) == GPIO.HIGH:
        gas="Alert,Button was pushed!"  
        gps()
        sensor_dht11()
        add_to_database()
        
    else:
        gas = "No Gas Detected"
        

def gps():
    global lat, lng
    ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
    dataout = pynmea2.NMEAStreamReader()
    newdata = ser.readline()
    if '$GNGGA' in str(newdata):
        newmsg = pynmea2.parse(newdata.decode('utf-8'))
        lat = str(newmsg.latitude)
        lng = str(newmsg.longitude)
        print(lat, lng)
    else:
        lat = 11.115216833
        lng = 77.188559166
        


def sensor_dht11():
    global humi, temp
    humidity, temperature = Adafruit_DHT.read(sensor, pin)
    if humidity is not None and temperature is not None:
        humi = humidity
        temp = temperature
    

def add_to_database():
    global id, gas,humi,temp,lat,lng
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the data into the database
        insert_query = "INSERT INTO data (id, gas, latitude, longitude, temperature, humidity) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (id ,gas, lat, lng, temp, humi)
        cursor.execute(insert_query, val)


        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Data added to the database")
    except mysql.connector.Error as error:
        print("Failed to add data to the database: {}".format(error))


# Main loop
while True:
    harmful()
    time.sleep(1)
