import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
import pandas as pd 
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab
import json


class Datavalidation:
    def __init__(self,data_validation_config:DataValidationConfig,
        data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'>>'*20}Data validation log started.{'<<'*20} ")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact

        except Exception as e:
            raise CustomException(sys,e) from e
    def get_train_test_data(self):
        try:
            config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
            ingestion = config.get_data_ingestion_config()
            basename = 'Flight_Fare_Prediction.csv'

            train_file_path = os.path.join(ingestion.ingested_train_dir,basename)
            test_file_path = os.path.join(ingestion.ingested_test_dir,basename)

            return train_file_path,test_file_path
        
        except Exception as e:
            raise CustomException(sys,e) from e
        
    def is_train_test_file_exist(self):
        try:
            logging.info("Checking if training and test file is available")

            is_train_file_exist = False
            is_test_file_exist = False

            train_file_path, test_file_path = self.get_train_test_data()
            

            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)

            logging.info(f"Is train and test file exists?-> Train_file:{is_train_file_exist}, Test_fiie: {is_test_file_exist}")

            if is_train_file_exist != True or is_test_file_exist != True:
                message = f"Training_file {train_file_path} or Testing_file {test_file_path} is not present"
                raise Exception(message)

            return is_train_file_exist, is_test_file_exist

        except Exception as e:
            raise CustomException(sys,e) from e


    def validate_dataset_schema(self):
        try:

            logging.info("Validating the train and test file")

            validation_status = False 

            train_file_path, test_file_path = self.get_train_test_data()

            train_df = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path)

            train_col = train_df.columns
            test_col = test_df.columns

            # Number of columns 

            if len(train_col) != len(test_col):
                message = f"Training_file {train_file_path} or Testing_file {test_file_path} is has missing columns"
                raise Exception(message)
            else:

                logging.info("Number of columns are same in both train and test file")

                # Column names 
                missing_col = []

                for i,j in zip(train_col,test_col):
                    if i in test_col:
                        continue
                    if j in train_col:
                        continue
                    
                    else:
                        missing_col.append(i,j)
            

            if len(missing_col) != 0:
                message = f"Training_file {train_file_path} or Testing_file {test_file_path} has a missing columns {missing_col}"
                raise Exception(message)
            
            else:
                logging.info("All columns are same in train and test file ")
                validation_status = True
            return validation_status
        except Exception as e:
            raise CustomException(sys,e) from e
        

    def save_data_drift_report(self):
        try:
            train_file_path,test_file_path = self.get_train_test_data()

            train_df = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path)

            profile = Profile(sections=[DataDriftProfileSection()])

            profile.calculate(train_df,test_df)

            report = json.loads(profile.json())

            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir,exist_ok=True)

            with open(report_file_path,"w") as report_file:
                json.dump(report, report_file, indent=6)
            return report

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def save_data_drift_report_page(self):
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()])
            train_file_path, test_file_path = self.get_train_test_data()
            dashboard.calculate(train_file_path,test_file_path)

            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)

            os.makedirs(report_page_dir,exist_ok=True)

            dashboard.save(report_page_file_path)

        except Exception as e:
            raise CustomException(e,sys) from e
        

    def is_data_drift_found(self)->bool:
        try:
            self.save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        except Exception as e:
            raise CustomException(e,sys) from e
        
    def initiate_data_validation(self)->DataValidationArtifact :
        try:
            self.is_train_test_file_exist()
            self.validate_dataset_schema()
            # self.is_data_drift_found()
            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successully."
            )
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            logging.info(f"{'>>'*20}Data validation log completed.{'<<'*20} \n\n")

            return data_validation_artifact
        except Exception as e:
            raise CustomException(e,sys) from e
        




            