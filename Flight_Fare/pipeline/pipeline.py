import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging

from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.util.util import *
from Flight_Fare.component.data_ingestion import DataIngestion
from Flight_Fare.component.data_validation import Datavalidation
from Flight_Fare.component.data_transformation import DataTransformation
from Flight_Fare.component.model_trainer import ModelTrainer
from Flight_Fare.component.model_evaluation import ModelEvaluation
from Flight_Fare.component.model_pusher import ModelPusher
from Flight_Fare.constant import *

from collections import namedtuple
from datetime import datetime
import uuid
from threading import Thread
from typing import List
from multiprocessing import Process
import pandas as pd


Experiment = namedtuple("Experiment", ["experiment_id", "initialization_timestamp", "artifact_time_stamp",
                                       "running_status", "start_time", "stop_time", "execution_time", "message",
                                       "experiment_file_path", "accuracy", "is_model_accepted"])


class Pipeline(Thread):
    experiment_file_path = None
    experiment: Experiment = Experiment(*([None] * 11))

    def __init__(self,config:Configuration) -> None:
        try:
            training_pipeline_file_path = config.get_training_pipeline_config().artifact_dir
            Pipeline.experiment_file_path = os.path.join(training_pipeline_file_path,EXPERIMENT_DIR_NAME,EXPERIMENT_FILE_NAME)

            super().__init__(daemon=False, name="pipeline")
            self.config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)

        except Exception as e:
            raise CustomException(sys,e) from e
        

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config = self.config.get_data_ingestion_config(),
                                           table_name = 'train',keyspace = 'predict')
            return data_ingestion.initiate_data_ingestion()

        except Exception as e:
            raise CustomException(sys,e) from e
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact)-> DataValidationArtifact:
        try:
            data_validation = Datavalidation( data_validation_config= self.config.get_data_validation_config(),
                                             data_ingestion_artifact = DataValidationArtifact
                                             )
            return data_validation.initiate_data_validation()
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def start_data_transformation(self,
                                  data_ingestion_artifact: DataIngestionArtifact,
                                  data_validation_artifact: DataValidationArtifact
                                  ) -> DataTransformationArtifact:
        try:
            data_transformation = DataTransformation(
                data_transformation_config=self.config.get_data_transformation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            return data_transformation.initiate_data_transformation()
        except Exception as e:
            raise CustomException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(model_trainer_config=self.config.get_model_trainer_config(),
                                         data_transformation_artifact=data_transformation_artifact
                                         )
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def start_model_evaluation(self, data_ingestion_artifact: DataIngestionArtifact,
                               data_validation_artifact: DataValidationArtifact,
                               model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:
        try:
            model_eval = ModelEvaluation(
                model_evaluation_config=self.config.get_model_evaluation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact,
                model_trainer_artifact=model_trainer_artifact)
            return model_eval.initiate_model_evaluation()
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def start_model_pusher(self, model_eval_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(
                model_pusher_config=self.config.get_model_pusher_config(),
                model_evaluation_artifact=model_eval_artifact
            )
            return model_pusher.initiate_model_pusher()
        except Exception as e:
            raise CustomException(e, sys) from e

        
    def run_pipeline(self):
        try:
            if Pipeline.experiment.running_status == True:
                logging.info("Pipeline is already running")
                return Pipeline.experiment
            
            logging.info("Pipeline starting.")

            experiment_id = str(uuid.uuid4())

            Pipeline.experiment = Experiment(experiment_id=experiment_id,
                                             initialization_timestamp = CURRENT_TIME_STAMP,
                                             artifact_time_stamp= CURRENT_TIME_STAMP,
                                             running_status=True,
                                             start_time= datetime.now(),
                                             stop_time=None,
                                             execution_time=None,
                                             message="Pipeline has been started.",
                                             experiment_file_path=Pipeline.experiment_file_path,
                                             accuracy=None,
                                             is_model_accepted=None
                                             )
            
            logging.info(f"Pipeline experiment: {Pipeline.experiment}")

            self.save_experiment()

            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact = data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)

            model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_ingestion_artifact,
                                                                    data_validation_artifact=data_validation_artifact,
                                                                    model_trainer_artifact=model_trainer_artifact)
            
            acc_file_path = os.path.join(ROOT_DIR,'Accuracy','Accuracy.yaml')
            acc = read_yaml_file(acc_file_path)
            accuracy = acc['model_accuracy']
            model_accepted = acc['is_model_accepted']

            if model_accepted == True:
                model_pusher_artifact = self.start_model_pusher(model_eval_artifact=model_evaluation_artifact)
                logging.info(f'Model pusher artifact: {model_pusher_artifact}')
            else:
                logging.info("Trained model rejected.")
            logging.info("Pipeline completed.")


            stop_time = datetime.now()
            
            Pipeline.experiment = Experiment(experiment_id=Pipeline.experiment.experiment_id,
                                             initialization_timestamp=self.config.time_stamp,
                                             artifact_time_stamp=self.config.time_stamp,
                                             running_status=False,
                                             start_time=Pipeline.experiment.start_time,
                                             stop_time=stop_time,
                                             execution_time=stop_time - Pipeline.experiment.start_time,
                                             message="Pipeline has been completed.",
                                             experiment_file_path=Pipeline.experiment_file_path,
                                             is_model_accepted=model_accepted,
                                             accuracy=accuracy
                                             )
            logging.info(f"Pipeline experiment: {Pipeline.experiment}")
            self.save_experiment()
            return

        except Exception as e:
            raise CustomException(e, sys) from e

    def run(self):
        try:
            self.run_pipeline()
        except Exception as e:
            raise e
        


    def save_experiment(self):
        try:
            if Pipeline.experiment.experiment_id is not None:
                experiment = Pipeline.experiment
                experiment_dict = experiment._asdict()
                experiment_dict: dict = {key: [value] for key, value in experiment_dict.items()}

                experiment_dict.update({
                    "created_time_stamp": [datetime.now()],
                    "experiment_file_path": [os.path.basename(Pipeline.experiment.experiment_file_path)]})

                experiment_report = pd.DataFrame(experiment_dict)

                os.makedirs(os.path.dirname(Pipeline.experiment_file_path), exist_ok=True)
                if os.path.exists(Pipeline.experiment_file_path):
                    experiment_report.to_csv(Pipeline.experiment_file_path, index=False, header=False, mode="a")
                else:
                    experiment_report.to_csv(Pipeline.experiment_file_path, mode="w", index=False, header=True)
            else:
                print("First start experiment")
        except Exception as e:
            raise CustomException(e, sys) from e

    @classmethod
    def get_experiments_status(cls, limit: int = 5) -> pd.DataFrame:
        try:
            if os.path.exists(Pipeline.experiment_file_path):
                df = pd.read_csv(Pipeline.experiment_file_path)
                limit = -1 * int(limit)
                return df[limit:].drop(columns=["experiment_file_path", "initialization_timestamp"], axis=1)
            else:
                return pd.DataFrame()
        except Exception as e:
            raise CustomException(e, sys) from e
        





    """def save_experiment(self):
        try:
            if Pipeline.experiment.experiment_id is not None:
                experiment = Pipeline.experiment

                experiment_dict = {
                    "created_time_stamp": [datetime.now()],
                    "experiment_file_path": [os.path.basename(Pipeline.experiment.experiment_file_path)]}

                experiment_report = pd.DataFrame(experiment_dict)

                os.makedirs(os.path.dirname(Pipeline.experiment_file_path), exist_ok=True)
                if os.path.exists(Pipeline.experiment_file_path):
                    experiment_report.to_csv(Pipeline.experiment_file_path, index=False, header=False, mode="a")
                else:
                    experiment_report.to_csv(Pipeline.experiment_file_path, mode="w", index=False, header=True)
            else:
                print("First start experiment")
        except Exception as e:
            raise CustomException(e, sys) from e
        

    @classmethod
    def get_experiments_status(cls, limit: int = 5) -> pd.DataFrame:
        try:
            if os.path.exists(Pipeline.experiment_file_path):
                df = pd.read_csv(Pipeline.experiment_file_path)
                limit = -1 * int(limit)
                return df[limit:].drop(columns=["experiment_file_path", "initialization_timestamp"], axis=1)
                #return df
            else:
                return pd.DataFrame()
        except Exception as e:
            raise CustomException(e, sys) from e
        """


"""if __name__=="__main__":
    config_path = os.path.join("config","config.yaml")
    pipeline = Pipeline(Configuration(config_file_path=config_path))
    pipeline.start_data_ingestion()"""