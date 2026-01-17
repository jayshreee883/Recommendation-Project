from flask import Flask,request,render_template,url_for,redirect,session
import pandas as pd
import numpy as np
import pickle
from flask_sqlalchemy import SQLAlchemy
import bcrypt



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()







        





# loading datasets

symptm_df = pd.read_csv("D:/RECOMMENDATION_PROJECT/datasets/new-symptom.csv")
precaution_df = pd.read_csv("D:/RECOMMENDATION_PROJECT/datasets/new-precaution.csv")
description_df= pd.read_csv("D:/RECOMMENDATION_PROJECT/datasets/new-description.csv")



# loading model
svc = pickle.load(open('D:/RECOMMENDATION_PROJECT/models/svc.pkl','rb'))




#function for helping the prediction function

def helper(dis):
    desc = description_df[description_df['Disease'] == dis]['Description'] #entered disease(dis) is matched with 'disease' in the dataset to fetch description

    desc = " ".join([w for w in desc])#joins the words in a single string with spaces
    
    pre = precaution_df[precaution_df['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4' ]]
    pre = [col for col in pre.values] #converting precautions into list
    
    return desc,pre

#actual numbers for symptoms  
symptoms_dict = {'itchy skin': 0, 'skin rash': 1, 'red patches':2,'nodal skin eruptions': 3, 'continuous sneezing':4 , 'shivering':5 , 'chills':6 , 'watery eyes':7 ,'headache':8,'mild headache':9, 'intense headache':10, 'pain on one side of head':11, 'blurred vision':12, 'sensitivity':13, 'hunger':14,  'excessive thirst':15, 'irregular sugar level':16, 'frequent urination':17, 'weight changes':18, 'vomiting':19, 'high fever':20, 'sweating':21}
diseases_list = {4:'Skin Fungal Infection', 0:'Allergy', 5:'Tension Headache', 1:'Diabetes',  3:'Migraine',  2:'Malaria'} #unique numbers assignd to disease

#Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        input_vector[symptoms_dict[item]] = 1
    return diseases_list[svc.predict([input_vector])[0]]
   











#predict page as the results should be should after clicking on predict
@app.route('/predict', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        print(symptoms)
        if symptoms =="Symptoms":
            message = "Please either write symptoms or you have written misspelled symptoms"
            return render_template('precaution.html', message=message)
        else:

            # Split the user's input into a list of symptoms (assuming they are comma-separated)
            user_symptoms = [s.strip() for s in symptoms.split(',')]
            # Remove any extra characters, if any
            user_symptoms = [symptom.strip("[]' ") for symptom in user_symptoms]
            predicted_disease = get_predicted_value(user_symptoms)
            dis_des, precautions = helper(predicted_disease)

            my_precautions = []
            for i in precautions[0]:
                my_precautions.append(i)

            return render_template('precaution.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=my_precautions)

    return render_template('precaution.html')











@app.route('/')
def start():
    return render_template('signup.html')


@app.route('/home')
def home():
    return render_template('home.html')





@app.route('/precaution')
def precaution():
    return render_template('precaution.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')




@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['eemail']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['eemail'] = user.email
            return redirect('/home')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

    



@app.route('/signup',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['uname']
        email = request.form['eemail']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')



    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')






if __name__ == "__main__":
    app.run(debug=True)
    