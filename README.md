# Flight_Fare_Predictions
First Machine Learning Project


python Flight_Fare/component/data_ingestion.py


config = Configuration(CONFIG_FILE_PATH,CURRENT_TIME_STAMP)
data_ingestion_config  = config.get_data_ingestion_config()
obj = DataIngestion(data_ingestion_config = config.get_data_ingestion_config(),table_name = 'train',keyspace = 'predict')
obj.initiate_data_ingestion()

valid = Datavalidation(data_validation_config=DataValidationConfig,data_ingestion_artifact=DataIngestionArtifact)
valid.initiate_data_validation()
trans = DataTransformation(data_transformation_config =  DataTransformationConfig,
                            data_ingestion_artifact =  DataIngestionArtifact,
                            data_validation_artifact = DataValidationArtifact)
trans.initiate_data_transformation()
model = ModelTrainer(model_trainer_config = ModelTrainerConfig, 
                        data_transformation_artifact = DataTransformationArtifact)

model_trainer= model.initiate_model_trainer()
model_eval = ModelEvaluation(model_evaluation_config = ModelEvaluationConfig,
                data_ingestion_artifact = DataIngestionArtifact,
                data_validation_artifact = DataValidationArtifact,
                model_trainer_artifact = ModelTrainerArtifact)

model_evaluation_artifact,model_accuracy,is_model_accepted = model_eval.initiate_model_evaluation()
print(model_evaluation_artifact,model_accuracy,is_model_accepted)