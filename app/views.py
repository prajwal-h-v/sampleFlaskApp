
from flask import render_template
from app import api,app
from app.models import Hello, Square

api.add_resource(Hello,"/api/")
api.add_resource(Square,"/api/square/<int:num>")

@app.route('/')
def home():
    title= "Home Page"
    return render_template('index.html',title=title)

