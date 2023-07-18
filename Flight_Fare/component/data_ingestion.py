import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.entity.config_entity import DataIngestionConfig
from Flight_Fare.entity.artifact_entity import DataIngestionArtifact
from six.moves import urllib

class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'='*20} Data Ingestion log started")
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise CustomException(sys,e) from e
        
    def download_data(self):
        try:

            # Download url
            download_url = self.data_ingestion_config.dataset_download_url

            # File location to save download file
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir

            # Create tgz folder 
            os.makedirs(tgz_download_dir,exist_ok=True)

            # Basename
            basename = 'Flight Fare Prediction.tgz'

            tgz_file_path = os.path.join(tgz_download_dir,basename)

            logging.info(f"Downloading file from: [{download_url}] to: [{tgz_file_path}]")

            # To download the file
            urllib.request.urlretrieve(download_url,tgz_file_path)

            logging.info('Successfully downloaded the file')

            return tgz_file_path

        except Exception as e:
            raise CustomException(sys,e) from e


    def extract_tgz_data(self,tgz_file_path:str):
        pass
            

    def split_data_trsin_test(self):
        pass
        
    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            tgz_file_path = self.download_data()
            # self.extract_tgz_data(tgz_file_path=tgz_file_path)

        except Exception as e:
            raise CustomException(sys,e) from e



if __name__=="__main__":
    obj = DataIngestion()
    print(obj.download_data())