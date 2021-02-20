import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

PATH_TO_DATASET_1="/home/meghana/Desktop/VLEngagement/new_dataset.csv"

CATEGORIES="categories"
TYPE="type"
WORD_COUNT="word_count"
TITLE_WORD_COUNT="title_word_count"

class Dataset:

    def __init__(self,path_to_dataset):
       self.path=path_to_dataset

    def create_dataframe(self):
       self.df = pd.read_csv(self.path)

    def size_dataset(self):
       self.num_of_observations=self.df.shape[0]
       self.num_of_features=self.df.shape[1]

    def categories_stats(self):
       categories = self.df[CATEGORIES].values
       list_remove_indexes=[]
       for i in range(len(categories)):
           if type(categories[i])!=float:
               categories[i]=categories[i].split('|')
           else:
               list_remove_indexes.append(i)
       categories = np.delete(categories,list_remove_indexes)
       flattened_categories = [y for x in categories for y in x]
       g=sns.displot(flattened_categories)
       g.set_xticklabels(rotation=60)
       plt.tight_layout()
       plt.show()

    def univariate_analysis(self):
        list_variables=[WORD_COUNT,TITLE_WORD_COUNT]
        for i in range(len(list_variables)):
            max_variable=np.max(self.df[list_variables[i]])
            min_variable=np.min(self.df[list_variables[i]])
            print("Statistics for: ",list_variables[i])
            print("Maximum Value: ",max_variable)
            print("Minimum Value: ", min_variable)

    def lecture_type_stats(self):
       self.lecture_types=self.df[TYPE].values
       g = sns.displot(self.lecture_types)
       plt.tight_layout()
       plt.show()


new_dataset=Dataset(PATH_TO_DATASET_1)
new_dataset.create_dataframe()
new_dataset.size_dataset()
new_dataset.univariate_analysis()
#new_dataset.lecture_type_stats()
#new_dataset.categories_stats()
print("")

