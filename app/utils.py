
from dis import dis
import io
import pickle
from app import crop_db, disease_db
from PIL import Image
from flask import jsonify
from torchvision import transforms
from sklearn.utils import shuffle
import torch
import torch.nn.functional as F
from app import weather_api_key
from smtplib import SMTP
import requests
import string 
import random
from bson.objectid import ObjectId

from app.utilities.model import ResNet9

disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy'
                   ]

# Loading Crop Recommendation model
crop_recommendation_model_path = "app/trainedModel/DecisionTree.pkl"
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

#Loading Disease Detection model
disease_model_path = 'app/trainedModel/plant-disease-model.pth'
disease_model = ResNet9(3, len(disease_classes))
disease_model.load_state_dict(torch.load(
                                disease_model_path, map_location=torch.device('cpu')))
disease_model.eval()

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

def predict_image(img, model=disease_model):
    """
    Tansforms image to tensors and predicts disease
    """

    transform = transforms.Compose([transforms.Resize(256), transforms.ToTensor()])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t,0)
    print('unqueesed image...')
    #Get Prediction From Model
    yb = model(img_u)

    # Pick index with highest probability
    _, preds = torch.max(yb,dim=1)
    
    # get probability
    prob = F.softmax(yb, dim=1)
    top_p, top_class = prob.topk(1,dim=1)
    print(top_p.item(), top_class.item())
    # end

    if top_p.item() > 0.85:
        print("probability is more than 0.85")
        prediction = disease_classes[top_class.item()]
        print(prediction)
    else:
        prediction = 'Could not detect crop'
    return prediction



def addCropData():
    return

def getCrops():
    cursor = crop_db.find()
    
    return cursor

def getCropByName(name):
    cursor = crop_db.find_one({'name':name})
    return cursor

def getCropByid(id):
    print('ObjectId(\''+id+'\')')
    reqDic = {'_id':ObjectId(id)}
    print(reqDic)
    cursor = crop_db.find_one(reqDic)
    print(cursor)
    return cursor
