from flask import Flask, send_file, send_from_directory, flash, request,\
        redirect, render_template, url_for, make_response
from app import app
from forms import PredictionForm
import numpy as np
import pandas as pd
from pickle import load
import json
from os.path import join
from firebase_admin import credentials, firestore, initialize_app

# loading machine learning model
model = load(open("model",'rb'))

# loading the json file 
with open("scorer.json") as f:
    data = json.load(f)

columns = ['age', 'duration', 'campaign', 'pdays', 'previous',\
           'emp_var_rate','cons_price_idx', 'cons_conf_idx',\
           'euribor3m', 'nr_employed','job', 'marital',\
           'education', 'default', 'housing', 'loan',\
           'contact', 'month', 'day_of_week', 'poutcome']

# dictionary to hold the values
dict_val = {}
for i in range(len(columns)):
    dict_val[i] = None
# assigning some constant values
dict_val[13] = 0
dict_val[7] = 1.5
dict_val[8] = 1.5
dict_val[5] = 1.5


# dataframe
dataframe = None

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('users')
todo_ref2 = db.collection('info')

@app.route("/")
def home():
    return render_template("sign-in.html")

@app.route("/registration")
def register():
    return render_template("sign-up.html")

@app.route('/add', methods=['POST'])
def create():
   
    if request.method == 'GET':
        return make_response('failure')
    if request.method == 'POST':
        try:
            x = {
              "name" : request.form['name'],
              "mail" : request.form['mail'],
              "password" : request.form['password']

            }

            todo_ref.document().set(x)
            #return jsonify({"success": True}), 200
            return render_template("sign-in.html")

        except Exception as e:
            #return f"An Error Occured: {e}"
            return render_template("sign-up.html")

@app.route('/addinfo', methods=['POST'])
def addinfo():
   
    if request.method == 'GET':
        return make_response('failure')
    if request.method == 'POST':
        try:
            x = {
              "age" : request.form['age'],
              "job" : request.form['job'],
              "marital" : request.form['marital'],
              "education" : request.form['education'],
              "housing" : request.form['housing'],
              "loan" : request.form['loan'],

              "contact" : request.form['contact'],
              "month" : request.form['month'],
              "day_of_week" : request.form['day_of_week'],
              "duration" : request.form['duration'],

              "campaign" : request.form['campaign'],
              "pdays" : request.form['pdays'],
              "previous" : request.form['previous'],
              "poutcome" : request.form['poutcome'],

              "cons_price_idx" : request.form['cons_price_idx'],
              "nr_employed" : request.form['nr_employed']
            }

            todo_ref2.document().set(x)
            #return jsonify({"success": True}), 200
            return render_template("prediction.html")

        except Exception as e:
            #return f"An Error Occured: {e}"
            return render_template("index.html")

@app.route('/prediction')
def prediction():
    """
    """
    global dataframe
    value = model.predict(dataframe)[0]
    if value == 1:
        value = "User is more likely to buy the product"
    else:
        value = "User is less likely tp buy the product"
    return render_template('prediction.html',value = value, filename='graph.png')

@app.route('/dashboard', methods=['POST', 'GET'])
def index_page():
    """
    """
    username = request.form['username']
    password = request.form['password']

    print(username)
    print(password)
    
    all_todos = [doc.to_dict() for doc in todo_ref.stream()]

    email = [item.get('mail') for item in all_todos]
    pwd = [item.get('password') for item in all_todos]
    

    for x in range(len(email)):
        if username == email[x]:
            result1 = 1
            break
        else:
            result1 = 0
    
    for x in range(len(pwd)):
        if password == pwd[x]:
            result2 = 1
            break
        else:
            result2 = 0
    
    if result1 == 1 and result2 == 1:
        global data,columns,dict_val, dataframe
        form = PredictionForm()
        if form.validate_on_submit():
            # creating a dataframe with the input values
            for val in form:
                if val.id in columns:
                    # if the value categorical
                    if val.id in data:
                        # obtaining the labeled id 
                        temp_val = data[val.id].index(val.data)
                        idx = columns.index(val.id)
                        dict_val[idx] = temp_val
                    else:
                        idx = columns.index(val.id)
                        dict_val[idx] = val.data
            print(dict_val)
            arr = [val for val in dict_val.values()]
            arr = np.array([arr])
            df = pd.DataFrame(arr,columns=columns)
            dataframe = df
            print(df)
            flash(f"prediction completed!", 'success')
            return redirect(url_for('prediction'))
        return render_template('index.html', form=form)
    else:
         return render_template("sign-in.html")

@app.route('/show/<filename>')
def showImage(filename):
    return redirect(url_for('static',filename = join('images',filename),
                            code = 301))



if __name__ == "__main__":
    app.run(debug=False , host = '0.0.0.0')
