import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
from Flight_Fare.util.util import *

from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder,LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import pandas as pd 




class FeatureGenerator(BaseEstimator, TransformerMixin):

    def __init__(self,columns):
        self.columns = columns

    def fit(self):
        return self
    
    def transform(self):
        try:
            # Date_of_Journey

            journey_day = self.columns.str.split('/').str[0].astype(int)

            journey_month = self.columns.str.split('/').str[1].str[1].astype(int)

            # self.x.drop('Date_of_Journey',inplace = True,axis = 1)

            # Dep_Time

            Dep_hr = self.columns.str.split(':').str[0].astype(int)

            Dep_min = self.columns.str.split(':').str[1].astype(int)

            # self.x.drop('Dep_Time',inplace = True,axis = 1)
            
            # Arrival_Time

            Arrival_hr = self.columns.str.split(" ").str[0].str.split(':').str[0].astype(int)

            Arrival_min = self.columns.str.split(" ").str[0].str.split(':').str[1].astype(int)

            # self.x.drop('Arrival_Time',inplace = True,axis = 1)

            # Duration

            Duration_hr = 0
            Duration_min = 0

            duration = list(self.columns)

            for i in range(len(duration)):
                if 'h' not in duration[i]:
                    duration[i] = '0h ' + duration[i]
                    
                if 'm' not in duration[i]:
                    duration[i] = duration[i] + ' 0m'
                    
            for i in range(len(duration)):
                hr = int(duration[i].split("h")[0])
                min_ = int(duration[i].split(" ")[1].split("m")[0])
                self.x['Duration_hr'][i] = hr
                self.x['Duration_min'][i] = min_
            
            self.x.drop('Duration',inplace = True,axis = 1)

            self.x['Duration_min'].fillna(0,inplace = True)


            return  self.columns

        except Exception as e:
            raise CustomException(sys,e) from e
        



class DataTransformation:

    def __init__(self, data_transformation_config: DataTransformationConfig,
                data_ingestion_artifact: DataIngestionArtifact,
                data_validation_artifact: DataValidationArtifact):
        try:
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = DataIngestionArtifact
            self.data_validation_artifact = DataValidationArtifact

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def get_data_transformer_object(self) -> ColumnTransformer:
        try:
            schema_file_path = SCHEMA_FILE_PATH

            dataset_schema = read_yaml_file(file_path=schema_file_path)

            num_cols = dataset_schema[NUMERICAL_COLUMN_KEY]
            cat_one = dataset_schema[CATEGORICAL_COLUMN_KEY]
            cat_label_coding = dataset_schema[CATEGORICAL_COLUMN_KEY_LABEL]

            num_pipeline = Pipeline(steps=[
                ('feature_generator', FeatureGenerator(columns='Date_of_Journey')),
                ('scaler', StandardScaler())
            ]
            )

            cat_pipeline = Pipeline(steps=[
                 ('one_hot_encoder', OneHotEncoder()),
                 ('scaler', StandardScaler(with_mean=False))
            ]
            )

            cat_label = Pipeline(steps=[
            ('Labe_encoding',LabelEncoder()),
            ('scaler', StandardScaler(with_mean=False))
            ]
            )


            logging.info(f"Categorical columns performing One Hot Encoding: {cat_one}")
            logging.info(f"Numerical columns: {num_cols}")
            logging.info(f"Categorical column performing Label encoding:{cat_label_coding}")


            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, num_cols),
                ('cat_pipeline', cat_pipeline, cat_one),
                ('cat_label',cat_label,cat_label_coding)
            ])
            return preprocessing
        
        except Exception as e:
            raise CustomException(sys,e) from e
        

    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")

            preprocessing_obj = self.get_data_transformer_object()

            config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
            ingestion = config.get_data_ingestion_config()
            basename = 'Flight_Fare_Prediction.csv'

            train_file_path = os.path.join(ingestion.ingested_train_dir,basename)
            test_file_path = os.path.join(ingestion.ingested_test_dir,basename)

            logging.info(f"Loading training and test data as pandas dataframe.")

            train_df = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path)

            schema = read_yaml_file(file_path=SCHEMA_FILE_PATH)

            





        