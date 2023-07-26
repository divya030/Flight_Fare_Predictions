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

    def fit(self,X,y=None):
        return self
    
    def transform(self,X,y=None):
    
        if self.columns == 'Date_of_Journey':
            try:
                X['journey_day'] = X['Date_of_Journey'].str.split('/').str[0].astype(int)
                X['journey_month'] = X['Date_of_Journey'].str.split('/').str[1].str[1].astype(int)

                # Since we have converted Date_of_Journey column into integers, Now we can drop as it is of no use.
                # df.drop('Date_of_Journey',inplace = True,axis = 1)
            except Exception as e:
                raise CustomException(sys,e)
            
        elif self.columns == 'Dep_Time':
            try:
                X['Dep_hr'] = X['Dep_Time'].str.split(':').str[0].astype(int)
                X['Dep_min'] = X['Dep_Time'].str.split(':').str[1].astype(int)

                # Since we have converted Dep_Time column into integers, Now we can drop as it is of no use.
                # df.drop('Dep_Time',inplace = True,axis = 1)

            except Exception as e:
                raise CustomException(sys,e)
            

        elif self.columns == 'Arrival_Time':
            try:
                X['Arrival_hr'] = X['Arrival_Time'].str.split(" ").str[0].str.split(':').str[0].astype(int)
                X['Arrival_min'] = X['Arrival_Time'].str.split(" ").str[0].str.split(':').str[1].astype(int)


                # Since we have converted Dep_Time column into integers, Now we can drop as it is of no use.
                # df.drop('Arrival_Time',inplace = True,axis = 1)

            except Exception as e:
                raise CustomException(sys,e)
            

        elif self.columns == 'Duration':
            X['Duration_hr'] = 0
            X['Duration_min'] = 0
        
            try:

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
                    
                    
                # Since we have converted Duration column into integers, Now we can drop as it is of no use.

                # df.drop('Duration',inplace = True,axis = 1)


                # Since there are some nan values represting 0 mins , we are replacing those values with 0 

                X['Duration_min'].fillna(0,inplace = True)

            except Exception as e:
                raise CustomException(sys,e)
            
        return X

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

            target_column_name = schema[TARGET_COLUMN_KEY]

            # Drop missing values 
            train_df.dropna(inplace = True)
            test_df.dropna(inplace = True)

            # Drop Trujet airline since it has one entry
            indexx = train_df[train_df['Airline'] == 'Trujet'].index[0]
            train_df.drop(index = indexx,inplace = True)

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

            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir

            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")

            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            logging.info(f"Saving transformed training and testing array.")

            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path,array=test_arr)

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessing_obj_file_path,obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
            message="Data transformation successfull.",
            transformed_train_file_path=transformed_train_file_path,
            transformed_test_file_path=transformed_test_file_path,
            preprocessed_object_file_path=preprocessing_obj_file_path

            )
            logging.info(f"Data transformationa artifact: {data_transformation_artifact}")
            return data_transformation_artifact

            return input_feature_train_arr
        except Exception as e:
            raise CustomException(e,sys) from e

    def __del__(self):
        logging.info(f"{'>>'*30}Data Transformation log completed.{'<<'*30} \n\n")

            





        