from flask import Flask, request


app = Flask(__name__)


@app.route('/via_postman', methods=['POST']) # for calling the API from Postman/SOAPUI
def math_operation_via_postman():
    if (request.method=='POST'):
        print('Thank you ')



if __name__ == "__main__":
    app.run(debug=True,port=5000)


import sys

import pip
from Flight_Fare.util.util import read_yaml_file, write_yaml_file
from Flight_Fare.logger import logging
from Flight_Fare.exception import CustomException
import os, sys
import json
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.constant import CONFIG_DIR, CURRENT_TIME_STAMP
from Flight_Fare.pipeline.pipeline import Pipeline
from Flight_Fare.entity.Flight_Fare_Predictor import FarePredictor, Flight_Data



ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "logs"
PIPELINE_FOLDER_NAME = "Flight_Fare"
SAVED_MODELS_DIR_NAME = "saved_models"
LOG_DIR = os.path.join(ROOT_DIR, LOG_FOLDER_NAME)
PIPELINE_DIR = os.path.join(ROOT_DIR, PIPELINE_FOLDER_NAME)
MODEL_DIR = os.path.join(ROOT_DIR, SAVED_MODELS_DIR_NAME)


from Flight_Fare.logger import CURRENT_TIME_STAMP

FLIGHT_FARE_DATA_KEY = "Flight_Fare_Data"
FLIGHT_FARE_PRICE_VALUE_KEY = "Flight_Fare_Price"

    context = {
        FLIGHT_FARE_DATA_KEY: None,
        FLIGHT_FARE_PRICE_VALUE_KEY: None
    }

    if (request.method == 'POST'):
        Airline = object(request.form['Airline'])
        Date_of_Journey = object(request.form['Date_of_Journey'])
        Source = object(request.form['Source'])
        Destination = object(request.form['Destination'])
        Route = object(request.form['Route'])
        Dep_Time = object(request.form['Dep_Time'])
        Arrival_Time = object(request.form['Arrival_Time'])
        Duration = object(request.form['Duration'])
        Total_Stops = object(request.form['Total_Stops'])
        Additional_Info = object(request.form['Additional_Info'])

        Flight_Fare_Data = Flight_Data(
                 Airline = Airline,
                 Date_of_Journey = Date_of_Journey,
                 Source = Source,
                 Destination = Destination,
                 Route = Route,
                 Dep_Time = Dep_Time,
                 Arrival_Time = Arrival_Time,
                 Duration = Duration,
                 Total_Stops = Total_Stops,
                 Additional_Info = Additional_Info
                 )
        
        df = Flight_Data.get_Flight_input_data_frame()
        Fare_predictor = FarePredictor(model_dir=MODEL_DIR)
        Flight_Fare_value = Fare_predictor.predict(X=df)
        context = {
            FLIGHT_FARE_DATA_KEY: Flight_Fare_Data.get_Filght_data_as_dict(),
            FLIGHT_FARE_PRICE_VALUE_KEY: Flight_Fare_value,
        }
        return context[FLIGHT_FARE_PRICE_VALUE_KEY][0]
