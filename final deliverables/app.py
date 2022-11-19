from flask import Flask, jsonify, request,render_template
from datetime import datetime
from datetime import timedelta
import requests
import json
import math
import pickle
import pandas as pd
app = Flask(__name__,template_folder="templates")
model = pickle.load(open('lasso.pk1','rb'))
API_KEY = "8r_73r_kobxkRh4xVZMTU29nikPAwCq3_2et93LJDKCj"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
@app.route('/')
def home():
    return render_template('intro.html')
@app.route('/predict')
def predict():
    return render_template('predict.html')
@app.route('/windapi',methods=['POST'])
def windapi():
    city=request.form.get('city')
    apikey="b306f1dbd82f1f344edf17a98e5f7aaa"
    url="http://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+apikey
    resp = requests.get(url)
    resp=resp.json()
    temp = str((resp["main"]["temp"])-273.15) +" °C"
    humid = str(resp["main"]["humidity"])+" %"
    pressure = str(resp["main"]["pressure"])+" mmHG"
    speed = str((resp["wind"]["speed"])*3.6)+" Km/s"
    return render_template('predict.html', temp=temp, humid=humid, pressure=pressure,speed=speed)   
@app.route('/y_predict',methods=['POST'])
def y_predict():
    '''
    For rendering results on HTML GUI
    '''
    x_test = [[float(x) for x in request.form.values()]]
    print(x_test)
    payload_scoring = {"input_data": 
			[{"field": [["Theoretical_Power_Curve (KWh)", "WindSpeed(m/s)"]], 
			"values": x_test}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/f33e7f01-076e-46b1-846a-7a3a74afa11b/predictions?version=2021-10-28', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    print("Scoring response")
    predictions =response_scoring.json()
    print(predictions)
    print('Final Prediction Result',predictions['predictions'][0]['values'][0][0])


    pred =response_scoring.json()
    print(pred)
    #print('Final Prediction Result',predictions['predictions'][0]['values'][0][0])

   # prediction = model.predict(x_test)
    print(pred)
    output = pred['predictions'][0]['values'][0][0]
    return render_template('predict.html', prediction_text='The energy predicted is {:.2f} KWh'.format(output))
if __name__ == "__main__":
     app.run(debug=False)
