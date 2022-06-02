



from flask import Flask
from flask_restful import Api
import pymongo
from flask_session import Session
import os


if "MONGODB_URI" in os.environ:
    mongo_client_uri = os.environ.get('MONGODB_URI')
else:
    from app import config
    mongo_client_uri = config.MONGODB_URI


if "WEATHER_API_KEY" in os.environ:
    weather_api_key = os.environ.get("WEATHER_API_KEY")
else:
    from app import config
    weather_api_key = config.weather_api_key

if weather_api_key is not None and mongo_client_uri is not None:
    print("Api loaded ...\n")


client = pymongo.MongoClient(mongo_client_uri)

db = client.get_database('cropHelp')
admin = db.admin
crop_db = db.crop_data
disease_db = db.diseases




app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
api = Api(app)

from app import views