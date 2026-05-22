"""
This file utilises an example dataset (downloaded from Kaggle - https://www.kaggle.com/datasets/harishkumardatalab/housing-price-prediction) which contains
some example housing data, which could be used to predict the value of a house. The csv of this data can be found in this folder, under Housing.csv. The purpose
of it in this folder is to both test, and act as an example for how to use the DataManager class in the data_manager.py file.  
"""

from data_manager import DataManager

dm = DataManager("hahahah")

# print(dm.table_exists("housing_data") == False)

if dm.table_exists("housing_data") == False:
    dm.create_table_from_csv("test_schema" 
                             ,"housing_data"
                             ,"src/data/Housing.csv")
    

df = dm.load_table("test_schema"
              ,"housing_data")

print(df.head(5))

dm.delete_table("test_schema"
                ,"housing_data")