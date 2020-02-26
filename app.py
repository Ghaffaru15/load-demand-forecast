from flask import Flask, request, jsonify
from joblib import load
import pandas as pd
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# import scheduler
import models
app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return 'This is a change'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'

db = SQLAlchemy(app)


@app.route('/api/predict/hourly', methods=['POST'])
def hourly_predict():
    hourly_model = load('model/xgb0.939.joblib')
    day = request.json['day']
    hour = request.json['hour']
    month = request.json['month']
    humidity = request.json['humidity']
    temperature = request.json['temperature']

    test = {
        'Day': day,
        'Hour': hour,
        'Month': month,
        'Relative Humidity': humidity,
        'Temperature': temperature
    }
    prediction = hourly_model.predict(pd.DataFrame(test, index=[0]))[0]

    return jsonify({'prediction': str(prediction)})


@app.route('/api/predict/daily', methods=['POST'])
def daily_predict():
    daily_model = load('model/daily/XG0.88.joblib')
    day = request.json['day']
    month = request.json['month']
    humidity = request.json['humidity']
    temperature = request.json['temperature']
    pressure = request.json['pressure']

    test = pd.DataFrame(
        {
            "Day": day,
            "Month": month,
            "Pressure": pressure,
            "Relative Humidity": humidity,
            "Temperature": temperature
        },
        index=[0])

    prediction = daily_model.predict(test)[0]
    return jsonify({'prediction': str(prediction)})


@app.route('/api/hourly/predictions/<int:year>/<int:month>/<int:day>')
def hourly_predictions(year, month, day):

    data = models.HourlyPrediction.query.filter_by(year=year,
                                                   month=month,
                                                   day=day).all()

    all_data = []
    hours = []
    predictions = []
    for i in range(len(data)):
        hours.append(data[i].hour)
        predictions.append(data[i].prediction)

    return jsonify({'hours': hours, 'predictions': predictions})


if __name__ == '__main__':
    app.run(debug=True)
