import yaml
import sys,os
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging

def read_yaml_file(file_path:str) -> dict:
    """
    Reads a yaml file and return the content in a dictionary
    file_path : str
    """
    try:
        with open(file_path,'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
        
    except Exception as e:
         raise CustomException(sys,e) from e

