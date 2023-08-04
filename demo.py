from Flight_Fare.pipeline.pipeline import Pipeline
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
import sys,os
from Flight_Fare.config.configuration import Configuration

def main():
    try:
        config_path = os.path.join("config","config.yaml")
        pipeline = Pipeline(Configuration(config_file_path=config_path))
        pipeline.run()
        logging.info("main function execution completed.")
    except Exception as e:
        logging.error(f"{e}")
        print(e)

if __name__ == "__main__":
    main()