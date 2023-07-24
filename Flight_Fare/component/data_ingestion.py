import os
from os import sys, path
PARENT_DIR = path.dirname(path.dirname(path.abspath('F:\Ineuron DS\Internship\FFP\Flight_Fare_Predictions\Flight_Fare\exception')))
sys.path.append(PARENT_DIR)
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import DataIngestionArtifact
from Flight_Fare.constant import *
import opendatasets as od
import pandas as pd
from sklearn.model_selection import train_test_split

from Flight_Fare.component.data_validation import Datavalidation


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

            os.makedirs(os.path.dirname(self.data_ingestion_config.raw_data_dir),exist_ok=True)

            df.to_csv(self.data_ingestion_config.raw_data_dir,header=True,index = False)
            
            logging.info('Train Test Split Initiated')

            train_set, test_set = train_test_split(df,test_size = 0.3, random_state = 42)

            os.makedirs(os.path.dirname(self.data_ingestion_config.ingested_test_dir),exist_ok=True)
            os.makedirs(os.path.dirname(self.data_ingestion_config.ingested_train_dir),exist_ok=True)

            train_set.to_csv(self.data_ingestion_config.ingested_train_dir, index = False, header = True)

            test_set.to_csv(self.data_ingestion_config.ingested_test_dir, index = False, header = True)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir)

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
    config = Configuration((CONFIG_FILE_PATH,CURRENT_TIME_STAMP))
    data_ingestion_config  = config.get_data_ingestion_config()
    obj = DataIngestion(data_ingestion_config = config.get_data_ingestion_config())
    obj.initiate_data_ingestion()
    valid = Datavalidation(data_ingestion_config = config.get_data_ingestion_config(), 
                           data_validation_config= config.get_data_validation_config())
    print(valid.initiate_data_validation())
    
    
    