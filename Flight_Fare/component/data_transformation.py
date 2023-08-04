import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
from Flight_Fare.util.util import *
import openpyxl
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder,LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import pandas as pd 




class Num_FeatureGenerator(BaseEstimator,TransformerMixin):

    def fit(self,X,y=None):
        return self

    def transform(self,X,y=None):
            try:
        
                X['journey_day'] = X['Date_of_Journey'].str.split('/').str[0].astype(int)
                X['journey_month'] = X['Date_of_Journey'].str.split('/').str[1].str[1].astype(int)

            
                X['Dep_hr'] = X['Dep_Time'].str.split(':').str[0].astype(int)
                X['Dep_min'] = X['Dep_Time'].str.split(':').str[1].astype(int)

                X['Arrival_hr'] = X['Arrival_Time'].str.split(" ").str[0].str.split(':').str[0].astype(int)
                X['Arrival_min'] = X['Arrival_Time'].str.split(" ").str[0].str.split(':').str[1].astype(int)

                X['Duration_hr'] = 0
                X['Duration_min'] = 0
            
                duration = list(X['Duration'])

                for i in range(len(duration)):
                    if 'h' not in duration[i]:
                        duration[i] = '0h ' + duration[i]
                        
                    if 'm' not in duration[i]:
                        duration[i] = duration[i] + ' 0m'
                        
                for i in range(len(duration)):
                    hr = int(duration[i].split("h")[0])
                    min_ = int(duration[i].split(" ")[1].split("m")[0])
                    X['Duration_hr'][i] = hr
                    X['Duration_min'][i] = min_

                X['Duration_min'].fillna(0,inplace = True)

                X.drop(['Date_of_Journey','Dep_Time','Arrival_Time','Duration'],inplace = True,axis =1 )

                # Drop missing values 
                X.dropna(inplace = True)

                return X
            
            except Exception as e:
                raise CustomException(sys,e) from e
            


class Cat_FeatureGenerator(BaseEstimator,TransformerMixin):

    def fit(self,X,y=None):
        return self

    def transform(self,X,y=None):
            try:
                X.drop(['Additional_Info','Route'],inplace = True,axis = 1)
                return X
            
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
            

            num_pipeline = Pipeline(steps=[
                ('num_feature_generator', Num_FeatureGenerator()),
                ('scaler', StandardScaler())
            ]
            )

            cat_pipeline = Pipeline(steps=[
                ('Cat_feature_generature',Cat_FeatureGenerator()),
                ('impute', SimpleImputer(strategy="most_frequent")),
                ('one_hot_encoder', OneHotEncoder()),
                ('scaler', StandardScaler(with_mean=False))
            ]
            )

            


            logging.info(f"Categorical columns : {cat_one}")
            logging.info(f"Numerical columns: {num_cols}")

            preprocessing = ColumnTransformer(transformers = [
                ('num_pipeline', num_pipeline,num_cols),
                ('cat_pipeline', cat_pipeline, cat_one)
            ],remainder='passthrough')
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

            target_column_name = schema[TARGET_COLUMN_KEY]
            # remove_columns = schema[COLUMNS_TO_REMOVE]

            # Drop Trujet airline since it has one entry
            indexx = train_df[train_df['Airline'] == 'Trujet'].index[0]
            train_df.drop(index = indexx,inplace = True)
            #train_df.drop(remove_columns,inplace = True,axis = 1)
            #test_df.drop(remove_columns,inplace=True,axis =1)
            
            logging.info(f"Splitting input and target feature from training and testing dataframe.")

            input_feature_train_df = train_df.drop(columns=[target_column_name],axis = 1)
            input_feature_test_df = test_df.drop(columns=[target_column_name],axis = 1)

            target_feature_train_df = train_df[target_column_name]
            target_feature_test_df = test_df[target_column_name]

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[ input_feature_train_arr, np.array(target_feature_train_df)]

            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            data_transformation_config = config.get_data_transformation_config()
            transformed_train_dir = data_transformation_config.transformed_train_dir
            transformed_test_dir = data_transformation_config.transformed_test_dir

            transformed_train_file_path = os.path.join(transformed_train_dir,basename).replace(".csv",".npz")
            transformed_test_file_path = os.path.join(transformed_test_dir,basename).replace(".csv",".npz")

            logging.info(f"Saving transformed training and testing array.")

            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path,array=test_arr)

            preprocessing_obj_file_path = data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessing_obj_file_path,obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
            message="Data transformation successfull.",
            transformed_train_file_path=transformed_train_file_path,
            transformed_test_file_path=transformed_test_file_path,
            preprocessed_object_file_path=preprocessing_obj_file_path

            )
            logging.info(f"Data transformationa artifact: {data_transformation_artifact}")
            logging.info(f"{'>>'*30}Data Transformation log completed.{'<<'*30} \n\n") 


            return data_transformation_artifact

            
        except Exception as e:
            raise CustomException(e,sys) from e

            
    
    







        