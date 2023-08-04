from Flight_Fare.entity.Flight_Fare_Predictor import Flight_Data,FarePredictor

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

if __name__=="__main__":
    Flight_Fare_Data = Flight_Data(
                 Airline = 'Air India',
                 Date_of_Journey = '1/06/2019',
                 Source = 'Delhi',
                 Destination = 'Cochin',
                 Route = 'DEL → BOM → COK',
                 Dep_Time = '07:00',
                 Arrival_Time = '19:15',
                 Duration = '12h 15m',
                 Total_Stops = '1 stop',
                 Additional_Info = 'No info'
                 )
    
    df = Flight_Fare_Data.get_Flight_input_data_frame()
    Fare_predictor = FarePredictor(model_dir=MODEL_DIR)
    Flight_Fare_value = Fare_predictor.predict(X=df)
    context = {
        FLIGHT_FARE_DATA_KEY: Flight_Fare_Data.get_Filght_data_as_dict(),
        FLIGHT_FARE_PRICE_VALUE_KEY: Flight_Fare_value,
    }
    print (context[FLIGHT_FARE_PRICE_VALUE_KEY][0])
    