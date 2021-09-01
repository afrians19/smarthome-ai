import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(19, GPIO.OUT
           )
GPIO.setup(26, GPIO.IN)
GPIO.output(16, GPIO.LOW)

#!/usr/bin/python
import smbus
import time
 
# Define some constants from the datasheet
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20
 
bus = smbus.SMBus(3)  # Rev 2 Pi uses 1
 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
  return convertToNumber(data)

import pandas as pd
#import numpy as np #code baru
import keras
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    dff = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(dff.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(dff.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


def dataPreparation(data_1day):
    #load raw data
    
    # dataset = pd.DataFrame({"humidity":humidity, 
                        # "weather":weather,
                        # "device_id":device_id,
                        # "created_at":created_at,
                        # "switch_id":switch_id,
                        # "updated_at":updated_at,
                        # "id":id_number,
                        # "status":status,
                        # "days":days,
                        # "is_motion":is_motion,
                        # "light_intensity":light_intensity,
                        # "time_minutes":time_minutes,
                        # "temperature":temperature,
                        # })
    
    dataset = pd.DataFrame(data_1day)
    
    #use initial value for scaling 
    datatemp_ = pd.DataFrame({"humidity":[40.0,91.0, 50.0], 
                        "weather":[2.0, 7.0, 5.0],
                        "device_id":[0, 1.0, 1.0],
                        "created_at":[0, 1.0, 1.0],
                        "switch_id":[1, 1, 1],
                        "updated_at":[0, 1, 1],
                        "id":[1, 2, 1],
                        "status":[0, 0, 0],
                        "days":[1, 7, 2],
                        "is_motion":[1, 0, 0],
                        "light_intensity":[0.0,352.0,1.0],
                        "time_minutes":[0,1439,4],
                        "temperature":[23.0,36.0,25.0],
                        })
                        
    dataset = dataset.append(datatemp_)
    
    #select switch_id = 1
    #lamp1_data = dataset.query("switch_id == 1")

    #timestamp to pandas index
    #lamp1_data = lamp1_data.set_index('created_at')
    
    #reorder column
    lamp1_data = dataset[["status", "days", "weather", "temperature", "humidity", "light_intensity", "time_minutes", "is_motion"]]
    
    # full data
    values = lamp1_data.values

    # integer encode direction
    # make all data to float
    values = values.astype('float32')

    # normalize features
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    
    # frame as supervised learning
    reframed = series_to_supervised(scaled, 1, 1)
    # drop columns we don't want to predict
    reframed.drop(reframed.columns[[9,10,11,12,13,14,15]], axis=1, inplace=True)
    
    
    # select features (predictor)
    values = reframed.values
    values = values[:, :-1]
    values_input = values.reshape((values.shape[0], 1, values.shape[1]))
    
    return values_input
    
def daily_1min(humidity, weather, device_id, created_at, switch_id,
                updated_at,id_number, status, days, is_motion, light_intensity, 
                time_minutes, temperature):
    #code here          
    data_1minute = pd.DataFrame({"humidity":humidity, 
                        "weather":weather,
                        "device_id":device_id,
                        "created_at":created_at,
                        "switch_id":switch_id,
                        "updated_at":updated_at,
                        "id":id_number,
                        "status":status,
                        "days":days,
                        "is_motion":is_motion,
                        "light_intensity":light_intensity,
                        "time_minutes":time_minutes,
                        "temperature":temperature,
                        }, index=[0])
                        
    return data_1minute
    
    
##################################### cara pake fungsinya ################################################


#load model
loaded_model = load_model('/home/pi/apps/emb-motherthings/LSTM_final_model.h5py')

# data behaviour_dataset  


#predict_data itu nilai status alat elektronik on/off (0/1 || False/True)

##################################### yay! ################################################


import serial
from firebase import firebase
firebase = firebase.FirebaseApplication('https://neuronthings.firebaseio.com/', None)

serialkey = "bkjebrg123j41kjbn123"
tokenfirebase ="AIzaSyDNdbfDKHje81H_e3UWP8pUOXYq2Jap25c"
ip = "http://neurondigital.tech:8080"
tanda1 = 0
tanda2 = 0
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)
import Adafruit_DHT

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT22

# Example using a Beaglebone Black with DHT sensor
# connected to pin P8_11.
pin = '20'

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO23.
#pin = 23

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
from datetime import datetime
import json
import requests
import time

temp_i = 0
temp_j = 0

while 1:
    
    if (temp_i > 1439): # checkpoint
        # data_1day dikosongin 
        collect_data_daily.drop(collect_data_daily.columns[[0,1,2,3,4,5,6,7,8,9,10,11,12]], axis=1, inplace=True)
        collect_data_daily = collect_data_daily.dropna()
        temp_i = 0
    #print("atas")
    time_old = int(time.time())
    sign = 0
    s_humidity = 0
    s_temperature = 0
    s_lightLevel = 0
    s_arus1 = 0
    s_arus2 = 0
    s_motion = 0
    
    try:
        time_now = time_old
        while ((time_now-time_old)<=51):
            print(str(time_old)+"\n")
            time_now = int(time.time())
            print(str(time_now)+"\n")

            sign+=1
            r_humidity, r_temperature = Adafruit_DHT.read_retry(sensor, pin)
            
            if r_humidity is not None and r_temperature is not None:
                temperature = r_temperature
                humidity = r_humidity
                #print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)) 
            else:
                print('Failed to get reading. Try again!')
            
            lightLevel=readLight()
            #print("Light Level : " + format(lightLevel,'.2f') + " lx")
            i=GPIO.input(26)
            #if i==0:                 #When output from motion sensor is LOW
                #print ("No intruders")
            #elif i==1:
                #print ("Intruder detected")

           
            try:
                serial_input = ser.readline()
                print(str(serial_input))

                r_arus = str(serial_input).replace(r"\r\n'",'').replace("b'",'').split(',')
                if(len(r_arus)>1):
                    arus= []
                    arus.append(float(r_arus[0]))
                    arus.append(float(r_arus[1]))
                    #print(r_arus[1],r_arus[0])
                    #print ("Read input back: " + str(arus[1])+ "-" + str(arus[0]))
            except:
                print("An exception occurr 1")
            
            
            result = firebase.get('/relay', serialkey)
            if(result["relay1"]!=True):
                GPIO.output(16, GPIO.HIGH)
                tanda1 = 0
            else:
                GPIO.output(16, GPIO.LOW)
                tanda1 = 1

            if(result["relay2"]!=True):
                GPIO.output(19, GPIO.HIGH)
                tanda2 = 0
            else:
                GPIO.output(19, GPIO.LOW)
                tanda2 = 1
            #print (str(result["relay1"])+"\n")
             


            s_humidity += humidity
            s_temperature += temperature
            s_lightLevel += lightLevel
            s_arus1 += float(arus[0])
            s_arus2 += float(arus[1])
            s_motion = i
            #print("sampe sini") ############ AMAN 
            
        s_humidity = s_humidity/sign
        s_temperature = s_temperature/sign
        s_lightLevel = s_lightLevel/sign
        s_arus1 = s_arus1/sign
        s_arus2 = s_arus2/sign
        
        #print("sampe sini coba")
        
        # framing data untuk diterima oleh model ML
        h = int(datetime.now().strftime('%H'))
        m = int(datetime.now().strftime('%M'))
        time_minutes = (h * 60) + m
        day = (datetime.today().weekday())+1
        APPID = '91ed0876c4a3c96a12dd116ee93a0ed1'
        LAT = '-6.199809'
        LONG = '106.611350'
        # -6.199809, 106.611350
        url = 'http://api.openweathermap.org/data/2.5/weather?lat=' + LAT + '&lon='+ LONG +'&appid='+ APPID #weather based on user's lat long
        try:
            res = requests.get(url)
        except requests.ConnectionError:
            print ("Connection Error")
        response = res.text
        data_json = json.loads(response)
        if data_json['cod'] != 200:
            weather = 'Error ' + str(data_json['cod']) + ', ' + data_json['message']
        else:
            weather = data_json['weather'][0]['main']
            if weather == 'Clear':
                weather = '1'
            elif weather == 'Clouds':
                weather = '2'
            elif weather == 'Rain':
                weather = '3'
            elif weather == 'Drizzle':
                weather = '4'
            elif weather == 'Thunderstorm':
                weather = '5'
            elif weather == 'Mist':
                weather = '6'
            elif weather == 'Haze':
                weather = '7'
            elif weather == 'Fog':
                weather = '8'
            elif weather == 'Smoke':
                weather = '9'
            elif weather == 'Dust':
                weather = '10'
            elif weather == 'Ash':
                weather = '11'
            elif weather == 'Sand':
                weather = '12'
        #humidity, weather, device_id, created_at, switch_id, updated_at, id_number, status, days, is_motion, light_intensity, time_minutes, temperature
        
        ############################### start disini ###############################
        #print("sampe sini2")
        # data yesterday masuk 1 kali doang
        if (temp_j < 1):
            yesterday_data = pd.read_csv('data_switch_01-0205_start510pm.csv')
            temp_j = temp_j + 1 
        #print("sampe sini3")
        # data yesterday masuk ke result (blast per menit) 1 kali doang buat 1440 menit/1hari 
        if (temp_j < 2):
            inputML_kemaren = dataPreparation(yesterday_data)
            result_ML = loaded_model.predict(inputML_kemaren)
            temp_j = temp_j + 1
            
        #print("sampe sini4")
        # PR
        data1minute = daily_1min(s_humidity, weather, " ", " ", " ", " ", " ", tanda2, str(day), s_motion, s_lightLevel, time_minutes, s_temperature)
        
        #print("sampe sini5")
        collect_data_daily = data1minute.append(data1minute)
        #print("sampe sini6")
        if (collect_data_daily.weather.size == 1439):
            result_ML = loaded_model.predict(collect_data_daily)
        #print("sampe sini7")
        # #sampe sini 1 menit, looping 1 menit begitu seterusnya
        # input_ML = dataPreparation(data_1day)
        #load raw data
        
        # predict
        # result_arr = loaded_model.predict(input_ML)
        #print("test")
        #print(result_ML)
        #################################### run predict disini ######################################
        
        # result hasilnya bakal di sekitaran +-1. atau +-0. .round() biar jadinya bulet 1/0 -> True/False
        predict_data = int(result_ML[temp_i].round())
        print("hasil predict",predict_data)
        
        # nambahin kalo kejadian resultnya < 1439
        # if (temp_i == result.size):
        #     a = np.array([[0]])
        #     sisa = 1439 - temp_i   
        #     for tambahin in sisa:
        #         result = np.concatenate((result, a))

        print(temp_i)
        temp_i = temp_i + 1

        if(predict_data==1):
            tanda2 = 1
            firebase.put('/relay/bkjebrg123j41kjbn123','relay2',bool(True)) # blast
            GPIO.output(19, GPIO.LOW)
        else:
            GPIO.output(19, GPIO.HIGH)
            tanda2 = 0
            firebase.put('/relay/bkjebrg123j41kjbn123','relay2',bool(False)) # blast
        
        #################################### run predict disini ######################################
        
        print(str(bool(tanda2))+"test"+str(bool(tanda1)))
        params_s = {
            "serial_number": serialkey,
            "value1": s_temperature,
            "value2": s_motion,
            "value3": s_humidity,
            "value4": s_lightLevel,
        }
        params_p = {
            "switch_id1": 1,
            "switch_id2": 2,
            "device_id": 1,
            "current1": s_arus1,
            "current2": s_arus2,
        }
        params_b = {
            "switch_id1": 1,
            "switch_id2": 2,
            "device_id": 1,
            "status1": tanda1,
            "status2": tanda2,
        }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            resp_s = requests.put(url=ip+"/api/sensor-data/blast", data=json.dumps(params_s), headers=headers)
            resp_p = requests.post(url=ip+"/api/power-usage/blast", data=json.dumps(params_p), headers=headers)
            resp_b = requests.post(url=ip+"/api/behavior-dataset/blast", data=json.dumps(params_b), headers=headers)
        except:
            print("An exception occurr 2")
    except:
        print("An exception occurr 3")

