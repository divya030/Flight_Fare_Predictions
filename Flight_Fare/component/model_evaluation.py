import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging

from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
from Flight_Fare.util.util import *
from Flight_Fare.component.model_trainer import ModelTrainer


class ModelEvaluation:

    def __init__(self, model_evaluation_config: ModelEvaluationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            logging.info(f"{'>>' * 30}Model Evaluation log started.{'<<' * 30} ")
            self.model_evaluation_config = model_evaluation_config
            self.model_trainer_artifact = model_trainer_artifact
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e
        

    def initiate_model_evaluation(self):

        try:
            config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
            trained_modef_file_path = config.get_model_trainer_config().trained_model_file_path
            model_evaluation_file_path = config.get_model_evaluation_config().model_evaluation_file_path

            model_trainer = ModelTrainer(model_trainer_config = ModelTrainerConfig, 
                            data_transformation_artifact = DataTransformationArtifact)
            
            model_accuracy = model_trainer.initiate_model_trainer()[1]

            index_number = 0

            data = {'best_model':
                        {'model_path': trained_modef_file_path,
                        'model_accuracy': float(model_accuracy),
                        'time_stamp': CURRENT_TIME_STAMP
                        }
                    }

            if os.path.exists(model_evaluation_file_path) == False:
                os.makedirs(os.path.dirname(model_evaluation_file_path),exist_ok=True)
                write_yaml_file(model_evaluation_file_path,data)
                index_number = 0

            else:
                model = read_yaml_file(model_evaluation_file_path)
                if model is None:
                    logging.info("Not found any existing model. Hence accepting trained model")
                    write_yaml_file(model_evaluation_file_path,data)
                    index_number = 0

                else:
                    if model['best_model']['model_accuracy'] < model_accuracy:
                        data = {'best_model':
                            {'model_path': trained_modef_file_path,
                            'model_accuracy': float(model_accuracy),
                            'time_stamp': CURRENT_TIME_STAMP
                            }
                        }
                        write_yaml_file(model_evaluation_file_path,data)
                        index_number = 0

            logging.info(f"Model evaluation completed. model metric artifact: {data}")
                
            if index_number == 0:
                is_model_accepted = False
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=model_evaluation_file_path,
                                                                            is_model_accepted=is_model_accepted)
                logging.info("Trained model is no better than existing model hence not accepting trained model")
            else:
                is_model_accepted = True
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=model_evaluation_file_path,
                                                                            is_model_accepted=is_model_accepted)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
            
            
            return model_evaluation_artifact,model_accuracy,is_model_accepted

        except Exception as e:
            raise CustomException(e, sys) from e

            