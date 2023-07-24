import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import DataIngestionArtifact
from Flight_Fare.component.data_ingestion import DataIngestion


class Pipeline:
    def __init__(self,config:Configuration()) -> None:
        try:
            self.config = config

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP))
            return data_ingestion.initiate_data_ingestion()

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()

        except Exception as e:
            raise CustomException(sys,e) from e