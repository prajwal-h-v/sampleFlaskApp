


import json

from bson.json_util import dumps
import numpy as np
from app import disease_db
from flask import jsonify,request
from flask_restful import Resource
from app.utils import cropPrediction, getCropByid, getCrops,weather_fetch, predict_image





class Hello(Resource):
    def get(self):
        return jsonify({"message":'hello, welcome'})

    def post(self):
        data = request.get_json()
        return jsonify({'data':data})

class Square(Resource):
    def get(self,num):
        return jsonify({"square":num**2})

class CropRecommendation(Resource):
    def post(self):
        req_dat = request.get_json()
        N = int(req_dat['nitrogen'])
        P = int(req_dat['phosphorous'])
        K = int(req_dat['pottasium'])
        ph = float(req_dat['ph'])
        rainfall = float(req_dat['rainfall'])
        city = req_dat['city']
        
        if weather_fetch(city) != None:
            tmp, hum = weather_fetch(city)
            data = np.array([[N,P,K,tmp,hum,ph,rainfall]])
            myPred = cropPrediction(data)
        
        return myPred


class DieasePredictorAPI(Resource):
    def post(self):
        print(request.files.get('key'))
        data = request.files['key']
        print(data)
        # print(type(data.read()))

        # req_data = request.files['image'].read()
        pred = predict_image(data.read())
        print(pred)
        diseaseDetails = disease_db.find_one({'disease_name':pred})
        # print(diseaseDetails)
        del diseaseDetails['_id']
        # print(diseaseDetails)
        return {'message': diseaseDetails}


class CropDataAPI(Resource):
    def get(self):
        crops = getCrops()
        print(crops)
        crops_json = json.loads(dumps(crops))
        return crops_json