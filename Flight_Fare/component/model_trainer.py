import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging

from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
from Flight_Fare.util.util import *

from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error

import pandas as pd


class ModelTrainer:

    def __init__(self, model_trainer_config:ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info(f"{'>>' * 30}Model trainer log started.{'<<' * 30} ")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            logging.info(f"Loading transformed training dataset")

            config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
            model_trainer = config.get_model_trainer_config()
            data_transformation = config.get_data_transformation_config()
            base_name = "Flight_Fare_Prediction.npz"

            transformed_train_file_path = os.path.join(data_transformation.transformed_train_dir,base_name)
            train_array = load_numpy_array_data(file_path=transformed_train_file_path)
            
            logging.info(f"Loading transformed test dataset")

            transformed_test_file_path = os.path.join(data_transformation.transformed_test_dir,base_name)
            test_array = load_numpy_array_data(file_path=transformed_test_file_path)

            logging.info(f"Splitting training and testing input and target feature")
            x_train,y_train,x_test,y_test = train_array[:,:-1],train_array[:,-1],test_array[:,:-1],test_array[:,-1]
            
            models = {
                #'Decision_tree': DecisionTreeRegressor(),
                #'Randon_forest': RandomForestRegressor(),
                'Linear_reg': LinearRegression()
                #'Xg_boost': XGBRegressor()
                #'Ada_boost': AdaBoostRegressor()
                    }
            

            param = {
                #'Decision_tree':{},
                #'Randon_forest': {
                    #'n_estimators': [100,115,134,145,156],
                    #'max_depth': [10,12,15,17,19,20],
                    #'min_samples_split': [6,8,10],
                    #'random_state':[42],
                    #'min_samples_leaf': [1, 2, 5, 10]
                #},
                'Linear_reg': {}
                #'Xg_boost': {
                    #'eta': [.0001,.001,0.01,.1],
                    #'max_depth':[4,6,8,10],
                    #'alpha' : np.arange(0.1,2,0.1),
                    #'n_estimators':[225,250,257,280], 
                    #'random_state':[30]
                #}
                #'Ada_boost': {}
                    }

            logging.info('Initializing the model training phase')

            model_report,model_config,model_acc,model_rmse = evaluate_model(X_train=x_train,X_test=x_test,
                                                                             y_train=y_train,y_test=y_test,
                                                                            models=models,param =param )

            scores = pd.DataFrame.from_dict(model_report,orient='index')
            best_model = scores[scores[0] == max(scores[0])].index[0]
            best_model_score = scores[scores[0] == max(scores[0])][0][0]

            best_model_config = model_config[best_model]
            model_accuracy = model_acc[best_model]
            best_model_rmse = model_rmse[best_model]

            logging.info(f"Best model on both training and testing dataset:{best_model}")

            preprocessing_obj_file_path = os.path.join(data_transformation.preprocessed_object_file_path)

            trained_model_file_path = model_trainer.trained_model_file_path

            preprocessing_obj =  load_object(file_path=preprocessing_obj_file_path)

            Flight_Fare_Prediction_Model = Flight_fare_predict_model(preprocessed_obj=preprocessing_obj,
                                                                     trained_model_object=best_model_config)
            
            logging.info(f'Saving the model at:{trained_model_file_path}')

            save_object(
                file_path=trained_model_file_path,
                obj=Flight_Fare_Prediction_Model
            )

            model_trainer_artifact=  ModelTrainerArtifact(is_trained=True,message="Model Trained successfully",
            trained_model_file_path=trained_model_file_path,
            train_rmse= best_model_rmse[0],
            test_rmse= best_model_rmse[1],
            train_accuracy= model_accuracy[0],
            test_accuracy= model_accuracy[1],
            model_accuracy= model_report[best_model]
            
            ), best_model_score

            logging.info(f"Model Trainer Artifact: {model_trainer_artifact}")
            logging.info(f"{'>>' * 30}Model trainer log completed.{'<<' * 30} ")
            return model_trainer_artifact
            
        except Exception as e:
            raise CustomException(e, sys) from e
    
         

class Flight_fare_predict_model:
    def __init__(self,preprocessed_obj,trained_model_object):
        """
        TrainedModel constructor
        preprocessing_object: preprocessing_object
        trained_model_object: trained_model_object
        """
        self.preprocessed_obj = preprocessed_obj
        self.trained_model_object = trained_model_object

    def predict(self,X):
         """
        function accepts raw inputs and then transformed raw input using preprocessing_object
        which gurantees that the inputs are in the same format as the training data
        At last it perform prediction on transformed features
        """
        
         transformed_feature = self.preprocessed_obj.transform(X)
         return self.trained_model_object.predict(transformed_feature)
    
    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__}()"