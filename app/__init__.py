


# from app import config
from flask import Flask
from flask_restful import Api
import pymongo
from flask_session import Session
import os

mongo_client_uri = os.environ.get('MONGODB_URI')
weather_api_key = os.environ.get("WEATHER_API_KEY")

# print(mongo_client_uri, weather_api_key)
# # if mongo_client_uri == None:
# #     mongo_client_uri = config.MONGODB_URI

# # if weather_api_key == None:
# #     weather_api_key = config.weather_api_key

# print(mongo_client_uri, weather_api_key)


client = pymongo.MongoClient(mongo_client_uri)

db = client.get_database('cropHelp')
admin = db.admin




app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
api = Api(app)

from app import views