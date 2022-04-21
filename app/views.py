

import email
from flask import   redirect, render_template,request, url_for,session


from app import api,app,admin
import numpy as np
from app.models import CropRecommendation, Hello, Square
from app.utils import cropPrediction,weather_fetch, generatePassword,sendMail


api.add_resource(Hello,"/api/")
api.add_resource(Square,"/api/square/<int:num>")
api.add_resource(CropRecommendation,'/api/crop-recommend')

#############################################################
###################### Home Page ############################
#############################################################
@app.route('/')
def home():
    title= "Home Page"
    return render_template('index.html',title=title)

#############################################################
################## Crop Recomendation Page ##################
#############################################################
@app.route('/crop-recommend')
def crop_recommend():
    title = "Crop Recommendation"
    return render_template('crop.html',title=title)


#############################################################
###################### AAdd Admin Page #####################
#############################################################
@app.route('/addAdminPage')
def addAdminPage():
    if session.get('name'):
        print(session.get('name'))
        title = "Add Admin"
        return render_template('addAdmin.html',title=title,name=session.get('name'),email = session.get('email'))
    else:
        return redirect(url_for('adminLoginPage'))

#############################################################
###################### Admin Login Page #####################
#############################################################
@app.route('/adminLoginPage')
def adminLoginPage():
    title = "Admin Login"
    return render_template('adminLogin.html',title=title)

#############################################################
###################### Admin Dashboard ######################
#############################################################
@app.route('/adminDashboard')
def adminDashboard():
    title = "Admin Dashboard"
    if session.get('name'):
        return render_template('adminDashboard.html',title=title,name=session.get('name'),email = session.get('email'))
    else:
        return redirect(url_for('adminLoginPage'))

#############################################################
###################### Adding new Admin #####################
#############################################################
@app.route('/logout')
def adminLogout():
    session['name'] = None
    session['email']=None
    return redirect(url_for('adminLoginPage'))

#############################################################
#################### Disease Detection Page #################
#############################################################
@app.route('/diseaseDetect')
def diseaseDetectionPage():
    return redirect(url_for('try_again'))
    
#############################################################
###################### Crop Info Page #######################
#############################################################
@app.route('/cropInformation')
def cropInformationPage():
    return redirect(url_for('try_again'))

#############################################################
###################### Crop Center Page #####################
#############################################################
@app.route('/cropCenterPage')
def cropCenterPage():
    return redirect(url_for('try_again'))


#############################################################
###################### try Again ############################
#############################################################
@app.route('/try_again')
def try_again():
    title="Try Again"
    return render_template('try_again.html',title=title)


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
    