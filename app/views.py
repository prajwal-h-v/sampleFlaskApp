



import json
from bson.json_util import dumps
from flask import redirect, render_template,request, url_for,session, Markup
from app.utilities.diseases import disease_dic
from app import api,app,admin, crop_db, disease_db
import numpy as np
from app.models import CropDataAPI, CropRecommendation, Hello, Square, DieasePredictorAPI
from app.utils import cropPrediction, getCrops, predict_image,weather_fetch, generatePassword,sendMail,getCropByName, getCropByid



# api.add_resource(Hello,"/api/")
# api.add_resource(Square,"/api/square/<int:num>")
appName= "Floria"
api.add_resource(CropRecommendation,'/api/crop-recommend')
api.add_resource(DieasePredictorAPI, '/api/disease-prediction')
api.add_resource(CropDataAPI, '/api/all-crops')

#############################################################
###################### Home Page ############################
#############################################################
@app.route('/')
def home():
    title= "Home Page"
    return render_template('index.html',title=title, appName=appName)

#############################################################
################## Crop Recomendation Page ##################
#############################################################
@app.route('/crop-recommend')
def crop_recommend():
    title = "Crop Recommendation"
    return render_template('crop.html',title=title,appName=appName)

#############################################################
#################### Disease Detection Page #################
#############################################################
@app.route('/diseaseDetect')
def diseaseDetectionPage():
    title = "Disease Detection"
    return render_template('diseaseDetectPage.html', title=title,appName=appName)
    
#############################################################
###################### Crop Info Page #######################
#############################################################
@app.route('/cropInformation')
def cropInformationPage():
    crops = getCrops()
    # return render_template('cropLists.html', title = "Crop List")
    cropNames = []

    for r in crops:
        print(r['_id'])
        cropNames.append( (str(r['_id']), r['name'], r['url'] ))
    # for i in range(1000):
    #     cropNames.append('test:'+str(i))
    
    return render_template('cropLists.html', title='Crop List', crops = cropNames,appName=appName)


@app.route('/cropInformation/<name>')
def getCropInfo(name):
    info = getCropByName(name)
    data = json.loads(dumps(info))
    return data

@app.route('/getCropById/<id>')
def getCropById(id):
    info = getCropByid(id)
    data = json.loads(dumps(info))
    print(data)
    return render_template('cropData.html', title=data['name'], cropData = data,appName=appName)

#############################################################
###################### Crop Center Page #####################
#############################################################
@app.route('/cropCenterPage')
def cropCenterPage():
    if session.get('name'):
        title = "Add Crop Info"
        return render_template('addCropData.html',title=title,name=session.get('name'),email = session.get('email'))
    else:
        return redirect(url_for('adminLoginPage'))


#############################################################
###################### Try Again ############################
#############################################################
@app.route('/try_again')
def try_again():
    title="Try Again"
    return render_template('try_again.html',title=title,home=request.args.get('home'),appName=appName)


#############################################################
###################### Add Admin Page #####################
#############################################################
@app.route('/addAdminPage')
def addAdminPage():
    if session.get('name'):
        print(session.get('name'))
        title = "Add Admin"
        return render_template('addAdmin.html',title=title,name=session.get('name'),email = session.get('email'),appName=appName)
    else:
        return redirect(url_for('adminLoginPage'))

#############################################################
###################### Admin Login Page #####################
#############################################################
@app.route('/adminLoginPage')
def adminLoginPage():
    title = "Admin Login"
    return render_template('adminLogin.html',title=title,appName=appName)

#############################################################
###################### Admin Dashboard ######################
#############################################################
@app.route('/adminDashboard')
def adminDashboard():
    title = "Admin Dashboard"
    if session.get('name'):
        return render_template('adminDashboard.html',title=title,name=session.get('name'),email = session.get('email'),appName=appName)
    else:
        return redirect(url_for('adminLoginPage'))

#############################################################
###################### Admin Logout #########################
#############################################################
@app.route('/logout')
def adminLogout():
    session['name'] = None
    session['email']=None
    return redirect(url_for('adminLoginPage'))


#############################################################
###################### Add Crop Page ########################
#############################################################

@app.route('/addCropPage')
def addCropPage():

    if session.get('name'):
        title = "Add New Crop Info"
        return render_template('NewCropPage.html',title=title,name=session.get('name'),email = session.get('email'),appName=appName)
    else:
        return redirect(url_for('adminLoginPage'))

@app.route('/addDiseasePage')
def addDiseasePage():
    return redirect(url_for('try_again',home="adminDashboard"))


########################################################################################################
####################################### Post Data Requests##############################################
########################################################################################################

#############################################################
################## Predict Crop Recommendation ##############
#############################################################
@app.route('/crop-predict', methods=["POST"])
def cropRecommendPrediction():
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
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


#############################################################
###################### Adding new Admin #####################
#############################################################
@app.route('/addAdmin',methods=['POST'])
def addAdmin():
    if session.get('name'):
        #Getting form data
        fullname = request.form['fullName']
        username = request.form['username']
        dest_email = request.form['emailid']
        password = generatePassword()
        added_by = session.get('name')

        # Creating query Object
        queryObject = {
            'fullname':fullname,
            'username':username,
            'email':dest_email,
            'password':password,
            'added_by':added_by
        }

        # Cheching if account already exists
        if admin.count_documents({'email':dest_email}) > 0:
            warning = "Admin account already exists."
            return render_template('addAdmin.html',warning=warning,name=session.get('name'),email = session.get('email'))

        # Creating new account if not present
        query = admin.insert_one(queryObject)
        if query.acknowledged:
            # Sending mail to the new account if created
            subject = "Admin Account"
            msg = f"Dear {fullname},\n\tYou have been granted admin previllages at CropHelp.\nYour credentials:\n\n\tUsername: {username}\n\tPassword: {password}\n\nRegards,\nTeam CropHelp"
            message = 'Subject: {}\n\n{}'.format(subject,msg)
            sendMail(dest_email,message)
        else:
            print("Failed...")


        return redirect(url_for('adminDashboard'))
    else:
        return redirect(url_for('adminLoginPage'))

#############################################################
###################### Admin Login ##########################
#############################################################

@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    # Getting form data
    username = request.form['adminUsername']
    password = request.form['adminPassword']

    queryObject = {'email':username}
    query = admin.find_one(queryObject)
    # checking if account exists
    if query == None:
        msg = "Admin account not found."
        return render_template('adminLogin.html',warning=msg)
    else:
        if password == query['password']:
            # Chhecking if password matches
            print('Password match.')
            print("Welcome {}".format(query['fullname']))
            session['email']=query['email']
            session['name']=query['username']

        else:
            msg = "Invalid Password"
            return render_template('adminLogin.html',warning=msg)
        return redirect(url_for('adminDashboard'))
    
#############################################################
###################### diseasePrediction ####################
#############################################################
@app.route('/diseasePrediction', methods=['POST'])
def diseasePrediction():
    title = "Disease Result"
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files.get('file')
    if not file:
        return redirect(url_for('diseaseDetectionPage'))
   
    img = file.read()
         
    prediction = predict_image(img)

    prediction1 = Markup(str(disease_dic[prediction]))
    pred_from_db = disease_db.find_one({'disease_name':prediction})
    print(pred_from_db)
    return render_template('disease_result.html',prediction=prediction1, title = title)
  

@app.route('/addNewCrop', methods=['POST'])
def addNewCrop():
    if session.get('name'):
        cropName = request.form['cropName']
        description = request.form['description']
        usage = request.form['usage']
        propagation = request.form['propagation']
        url = request.form['url']

        queryObject = {
            "name":cropName,
            "description" : description,
            'usage':usage,
            'propagation':propagation,
            "url":url

        }
        # Checking if crop already exists
        if crop_db.count_documents({'name':cropName}) > 0:
            warning = "Crop already exists."
            return render_template(
                'NewCropPage.html',
                warning=warning,
                name=session.get('name'),
                email = session.get('email'))
        query = crop_db.insert_one(queryObject)
        if query.acknowledged:
            return render_template(
                'NewCropPage.html',
                success = "Crop Added",
                name=session.get('name'),
                email = session.get('email'))

    else:
        return redirect(url_for('adminLoginPage'))