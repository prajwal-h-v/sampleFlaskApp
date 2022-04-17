
from flask import  render_template,request
from app import api,app
import numpy as np
from app.models import CropRecommendation, Hello, Square
from app.utils import cropPrediction,weather_fetch

api.add_resource(Hello,"/api/")
api.add_resource(Square,"/api/square/<int:num>")
api.add_resource(CropRecommendation,'/api/crop-recommend')

@app.route('/')
def home():
    title= "Home Page"
    return render_template('index.html',title=title)

@app.route('/crop-recommend')
def crop_recommend():
    title = "Crop Recommendation"
    return render_template('crop.html',title=title)















@app.route('/crop-predict', methods=["POST"])
def cropRecommendPrediction():
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['potasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = cropPrediction(data)
            final_prediction = my_prediction.get_json()['crop']
            

            return render_template('crop-result.html',predictedCrop=final_prediction)
        else:
            return render_template('try_again.html',title="Error")