from collections import namedtuple

DataIngestionConfig = namedtuple("DataIngestionConfig",
                                 ["dataset_download_url","tgz_download_dir","train_data_path","test_data_path","raw_data_path"])

DataValidationConfig = namedtuple("DataValidationConfig",["schema_dir","schema_file_path","report_file_name","report_page_file_name"])

DataTransformationConfig = namedtuple("DataTransformationConfig",["transformed_dir","transformed_train_dir","transformed_test_dir",
                                                                  "preprocessing_dir","preprocessed_object_file_name"])

ModelTrainerConfig = namedtuple("ModelTrainerConfig",["trained_model_dir","model_file_name","base_accuracy","model_config_dir",
                                                      "model_config_file_name"])

ModelEvaluationConfig = namedtuple("ModelEvaluationConfig",['model_evaluation_file_path','time_stamp'])

ModelPusherConfig = namedtuple("ModelPusherConfig",['export_dir_path'])

TrainingPipelineConfig = namedtuple("TrainingPipelineConfig", ["artifact_dir"])

