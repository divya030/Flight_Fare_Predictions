import os
import sys

from Flight_Fare.exception import CustomException
from Flight_Fare.util.util import load_object

import pandas as pd


class Flight_Data:

    def __init__(self,
                 Airline:object,
                 Date_of_Journey:object,
                 Source:object,
                 Destination:object,
                 Route:object,
                 Dep_Time:object,
                 Arrival_Time:object,
                 Duration:object,
                 Total_Stops:object,
                 Additional_Info:object
                 ):
        
        try:
            self.Airline = Airline
            self.Date_of_Journey = Date_of_Journey
            self.Source = Source
            self.Destination = Destination
            self.Route = Route
            self.Dep_Time = Dep_Time
            self.Arrival_Time = Arrival_Time
            self.Duration = Duration
            self.Total_Stops = Total_Stops
            self.Additional_Info = Additional_Info

        except Exception as e:
            raise CustomException(e, sys) from e
        

    def get_Flight_input_data_frame(self):

        try:
            Flight_input_dict = self.get_Filght_data_as_dict()
            return pd.DataFrame(Flight_input_dict)
        except Exception as e:
            raise CustomException(e, sys) from e
        

    def get_Filght_data_as_dict(self):
        try:
            input_data = {
                'Airline': [self.Airline],
                "Date_of_Journey":[self.Date_of_Journey], 
                "Source": [self.Source],
                "Destination": [self.Destination],
                "Route": [self.Route],
                "Dep_Time":[self.Dep_Time],
                "Arrival_Time": [self.Arrival_Time],
                "Duration":[self.Duration],
                "Total_Stops": [self.Total_Stops],
                "Additional_Info": [self.Additional_Info]
                }

            return input_data
        
        except Exception as e:
            raise CustomException(e, sys) from e
        

class FarePredictor:
    def __init__(self, model_dir: str):
        try:
            self.model_dir = model_dir
        except Exception as e:
            raise CustomException(e, sys) from e
    
    def get_latest_model_path(self):
        try:
            folder_name = os.listdir(self.model_dir)[-1]
            latest_folder_dir = os.path.join(self.model_dir,folder_name)
            folder_name = os.listdir(latest_folder_dir)[0]
            latest_folder_dir = os.path.join(latest_folder_dir, folder_name)
            file_name = os.listdir(latest_folder_dir)[0]
            latest_model_path = os.path.join(latest_folder_dir,file_name)
            return latest_model_path
        except Exception as e:
            raise CustomException(e, sys) from e

    def predict(self, X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            median_house_value = model.predict(X)
            return median_house_value
        except Exception as e:
            raise CustomException(e, sys) from e
