from Flight_Fare.pipeline.pipeline import Pipeline
from Flight_Fare.exception import CustomException
from Flight_Fare.logger import logging
import sys,os

def main():
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
    except Exception as e:
            raise CustomException(sys,e) from e

if __name__ == "__main__":
    main()