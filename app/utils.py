
import pickle
from flask import jsonify
from sklearn.utils import shuffle

from app import weather_api_key
from smtplib import SMTP
import requests
import string 
import random

crop_recommendation_model_path = "app/trainedModel/DecisionTree.pkl"
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

def cropPrediction(data):
    my_prediction = crop_recommendation_model.predict(data)
    #print(my_prediction)
    finalPrediction = my_prediction[0]
    return jsonify({"crop":finalPrediction})



def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid="+api_key+"&q="+city_name
    response = requests.get(complete_url)
    x = response.json()
    if x['cod'] != '404':
        y = x['main']
        temperature = round((y['temp'] - 273.15),2)
        humidity = y['humidity']
        return temperature,humidity
    else:
        return None

    
def generatePassword():
    length = 10
    characters =list(string.ascii_letters+string.digits+"!@#$%^&*()")
    random.shuffle(characters)

    password = []
    for i in range(length):
        password.append(random.choice(characters))

    random,shuffle(password)
    newPassword = "".join(password)
    return newPassword

def sendMail(dest, message):
    

    conn = SMTP('smtp.gmail.com',587)
    conn.starttls()
    sender = 'prajjisharma@gmail.com'
    conn.login(sender,'prajjivk169')
    conn.sendmail(sender,dest,message)

    conn.quit()