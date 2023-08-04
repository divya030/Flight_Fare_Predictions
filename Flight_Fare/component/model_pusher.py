import os
import sys
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging

from Flight_Fare.config.configuration import Configuration
from Flight_Fare.entity.artifact_entity import *
from Flight_Fare.entity.config_entity import *
from Flight_Fare.constant import *
from Flight_Fare.util.util import *
import shutil

class ModelPusher:

    def __init__(self, model_pusher_config: ModelPusherConfig,
                 model_evaluation_artifact: ModelEvaluationArtifact
                 ):
        try:
            logging.info(f"{'>>' * 30}Model Pusher log started.{'<<' * 30} ")
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact

        except Exception as e:
            raise CustomException(e, sys) from e
        

    def export_model(self)-> ModelPusherArtifact:

        try:
            config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)

            evaluated_model_path = config.get_model_trainer_config().trained_model_file_path
            export_dir = config.get_model_pusher_config().export_dir_path
            model_file_name = os.path.basename(evaluated_model_path)
            model_file_name = model_file_name.split(".")[0]

            export_model_file_path = os.path.join(export_dir,model_file_name)
            logging.info(f"Exporting model file: [{export_model_file_path}]")

            os.makedirs(export_model_file_path,exist_ok=True)

            shutil.copy(evaluated_model_path,export_model_file_path)
            logging.info(
                f"Trained model: {evaluated_model_path} is copied in export dir:[{export_model_file_path}]")

            model_pusher_artifact = ModelPusherArtifact(is_model_pusher=True,
                                                        export_model_file_path=export_model_file_path
                                                        )
            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")

            logging.info(f"{'>>' * 20}Model Pusher log completed.{'<<' * 20} ")
            
            return model_pusher_artifact
        
        except Exception as e:
            raise CustomException(e, sys) from e
        
    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            return self.export_model()
        except Exception as e:
            raise CustomException(e, sys) from e