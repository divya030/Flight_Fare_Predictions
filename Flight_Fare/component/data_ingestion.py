import os
from os import sys, path
PARENT_DIR = path.dirname(path.dirname(path.abspath('F:\Ineuron DS\Internship\FFP\Flight_Fare_Predictions\Flight_Fare\exception')))
sys.path.append(PARENT_DIR)
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
import opendatasets as od
import pandas as pd
from sklearn.model_selection import train_test_split
from Flight_Fare.util.util import read_yaml_file
import openpyxl
from Flight_Fare.component.data_validation import Datavalidation
from Flight_Fare.component.data_transformation import DataTransformation
from Flight_Fare.component.model_trainer import ModelTrainer
from Flight_Fare.component.model_evaluation import ModelEvaluation


class DataIngestion:

    def __init__(self,data_ingestion_config ):
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20} ")
            self.data_ingestion_config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
            self.data_ingestion_config = self.data_ingestion_config.get_data_ingestion_config()

        except Exception as e:
            raise CustomException(sys,e) from e
        
    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            df = pd.read_excel('notebook\Data_Train.xlsx')

            logging.info('Read the dataset as dataframe')

            raw_path = self.data_ingestion_config.raw_data_dir
            os.makedirs(raw_path,exist_ok=True)

            basename = "Flight_Fare_Prediction.csv"

            raw_file_path = os.path.join(raw_path,basename)

            df.to_csv(raw_file_path,header=True,index = False)
            
            logging.info('Train Test Split Initiated')

            train_set, test_set = train_test_split(df,test_size = 0.3, random_state = 42)

            test_path = self.data_ingestion_config.ingested_test_dir
            train_path = self.data_ingestion_config.ingested_train_dir

            os.makedirs(test_path,exist_ok=True)
            os.makedirs(train_path,exist_ok=True)

            train_file_path = os.path.join(train_path,basename)
            test_file_path = os.path.join(test_path,basename)

            train_set.to_csv(train_file_path, index = False, header = True)

            test_set.to_csv(test_file_path, index = False, header = True)

            
            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                test_file_path=test_file_path,
                                is_ingested=True,
                                message=f"Data ingestion completed successfully."
                                )

            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            logging.info(f"{'>>'*20}Data Ingestion log completed.{'<<'*20} \n\n")

            return data_ingestion_artifact

        except Exception as e:
            raise CustomException(sys,e) from e
        

        



if __name__=="__main__":
    config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
    data_ingestion_config  = config.get_data_ingestion_config()
    obj = DataIngestion(data_ingestion_config = config.get_data_ingestion_config())
    obj.initiate_data_ingestion()
    valid = Datavalidation(data_validation_config=DataValidationConfig,data_ingestion_artifact=DataIngestionArtifact)
    valid.initiate_data_validation()
    trans = DataTransformation(data_transformation_config =  DataTransformationConfig,
                                data_ingestion_artifact =  DataIngestionArtifact,
                                data_validation_artifact = DataValidationArtifact)
    trans.initiate_data_transformation()
    model = ModelTrainer(model_trainer_config = ModelTrainerConfig, 
                            data_transformation_artifact = DataTransformationArtifact)

    model_trainer= model.initiate_model_trainer()
    model_eval = ModelEvaluation(model_evaluation_config = ModelEvaluationConfig,
                 data_ingestion_artifact = DataIngestionArtifact,
                 data_validation_artifact = DataValidationArtifact,
                 model_trainer_artifact = ModelTrainerArtifact)
    
    acc,file = model_eval.initiate_model_evaluation()
    print(acc,file)
   
   
    
    
    
    