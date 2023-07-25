import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.component.data_ingestion import DataIngestion
from Flight_Fare.component.data_validation import Datavalidation
from Flight_Fare.constant import *



class Pipeline:
    def __init__(self,config:Configuration) -> None:
        try:
            self.config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config = self.config)
            return data_ingestion.initiate_data_ingestion()

        except Exception as e:
            raise CustomException(sys,e) from e
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact)-> DataValidationArtifact:
        try:
            data_validation = Datavalidation(data_ingestion_config = self.config.get_data_ingestion_config(), 
                                             data_validation_config= self.config.get_data_validation_config(),
                                             data_ingestion_artifact = DataValidationArtifact
                                             )
            return data_validation.initiate_data_validation()
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(DataIngestionArtifact)

        except Exception as e:
            raise CustomException(sys,e) from e