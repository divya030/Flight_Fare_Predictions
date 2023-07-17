from setuptools import setup
from typing import List


# Declaring variables for setup function
PROJECT_NAME = 'Flight Fare Predictions'
VERSION = '0.0.1'
AUTHOR = 'Divya'
DESCRIPTION = 'Predicitng the Price of the Flight Tickets'
PACKAGES = ['src']
REQUIREMENTS_FILE_NAME = 'requirements.txt'

def get_requirements_list()->List[str]:
    """
    Description: This function is going to return list of requirement
    mention in requirements.txt file
    Return: This function is going to return a list which contain name
    of libraries mentioned in requirements.txt file
    """
    with open(REQUIREMENTS_FILE_NAME) as library_name:
        library = library_name.readlines()
        library = [i.replace('\n',"")   for i in library]
        if '-e .' in library:
            library.remove('-e .')
        return library

setup(
    name= PROJECT_NAME,
    version= VERSION,
    author= AUTHOR,
    description= DESCRIPTION,
    packages= PACKAGES,
    install_requires = get_requirements_list()
)

