import yaml
import sys,os
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.constant import *
import numpy as np
import dill

from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error
import pickle
from sklearn.model_selection import GridSearchCV


def write_yaml_file(file_path:str,data:dict=None):
    """
    Create yaml file 
    file_path: str
    data: dict
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path,"w") as yaml_file:
            if data is not None:
                yaml.dump(data,yaml_file)
    except Exception as e:
        raise CustomException(e,sys)
    

def read_yaml_file(file_path) -> dict:
    """
    Reads a yaml file and return the content in a dictionary
    file_path : str
    """
    try:
        with open(file_path ,'r') as yaml_file:
            return yaml.safe_load(yaml_file)
        
    except Exception as e:
         raise CustomException(sys,e) from e


def load_numpy_array_data(file_path: str) -> np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise CustomException(e, sys) from e
    

def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise CustomException(e, sys) from e
    

def save_object(file_path:str,obj):
    """
    file_path: str
    obj: Any sort of object
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e,sys) from e
    

def load_object(file_path:str):
    """
    file_path: str
    """
    try:
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise CustomException(e,sys) from e
    

def evaluate_model(X_train,X_test,y_train,y_test,models,param):
    """
    Evaluating the models
    """
    try:

        model_report = {}
        model_config = {}
        model_acc = {}
        model_rmse = {}


        for i in models:
                
                logging.info(f"{'>>'*30}Started evaluating model: [{models}] {'<<'*30}")

                model = GridSearchCV(models[i], param_grid = param[i], cv = 5)
                
                model.fit(X_train,y_train)
                
                #Getting prediction for training and testing dataset
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)
                
                #Calculating r squared score on training and testing dataset
                train_acc = r2_score(y_train,y_train_pred)
                test_acc = r2_score(y_test,y_test_pred)

                #Calculating mean squared error on training and testing dataset
                train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
                test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

                # Calculating harmonic mean of train_accuracy and test_accuracy
                model_accuracy = (2 * (train_acc * test_acc)) / (train_acc + test_acc)
                diff_test_train_acc = abs(test_acc - train_acc)

                #logging all important metric
                logging.info(f"{'>>'*30} Score {'<<'*30}")
                logging.info(f"Train Score\t\t Test Score\t\t Average Score")
                logging.info(f"{train_acc}\t\t {test_acc}\t\t{model_accuracy}")

                logging.info(f"{'>>'*30} Loss {'<<'*30}")
                logging.info(f"Diff test train accuracy: [{diff_test_train_acc}].") 
                logging.info(f"Train root mean squared error: [{train_rmse}].")
                logging.info(f"Test root mean squared error: [{test_rmse}].")

                #if model accuracy is greater than base accuracy and train and test score is within certain thershold
                #we will accept that model as accepted model
                if model_accuracy >= 0.6 and diff_test_train_acc < 0.05:
                    model_report[i] = model_accuracy
                    model_config[i] = model
                    model_acc[i] = [train_acc,test_acc]
                    model_rmse[i] = [train_rmse,test_rmse]
                    

                
        return model_report,model_config,model_acc,model_rmse
    except Exception as e:
        raise CustomException(e,sys) from e
    