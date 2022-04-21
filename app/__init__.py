


from flask import Flask
from flask_restful import Api
import pymongo
from flask_session import Session

client = pymongo.MongoClient("mongodb+srv://prajji14:prajjivk169@cluster0.p8upr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('cropHelp')
admin = db.admin




app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
api = Api(app)

from app import views