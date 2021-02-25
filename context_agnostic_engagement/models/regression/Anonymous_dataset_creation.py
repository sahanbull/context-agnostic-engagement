import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.utils import shuffle

PATH_TO_DATASET_1="/home/meghana/Desktop/VLEngagement/new_dataset.csv"

class Anonymous_Dataset:

    def __init__(self,path_to_dataset):
       self.path=path_to_dataset

    def create_dataframe(self):
       self.df = pd.read_csv(self.path)
       self.df=shuffle(self.df,random_state=42)
       self.df.reset_index(inplace=True, drop=True)

       slug_list = list(self.df["slug"])
       slug_id_mapping = {slug: id + 1 for id, slug in enumerate(slug_list)}
       self.df["id"] = self.df["slug"].apply(lambda l: slug_id_mapping[l])

       stem_category_list=["Life_Sciences", "Physics","Technology", "Mathematics","Computer_Science", "Data_Science","Computers"]

       for i in range(self.df.shape[0]):
           if type(self.df["categories"].loc[i]) != float:
               self.df["categories"].loc[i] =self.df["categories"].loc[i].split('|')

       for i in range(self.df.shape[0]):
         if type(self.df["categories"].loc[i])!=float:
           count=0
           for elem in self.df["categories"].loc[i]:
              if elem in stem_category_list:
                  count=count+1
           if count==0:
               self.df["categories"].loc[i]="misc"
           elif count==len(self.df["categories"].loc[i]):
               self.df["categories"].loc[i] = "stem"
           else:
               self.df["categories"].loc[i] = "stem|misc"


        ##published date rounded##
       for i in range(self.df.shape[0]):
           self.df["time"].loc[i] = round(self.df["time"].loc[i]/10)*10

        ##lecture duration##
       for i in range(self.df.shape[0]):
           self.df["total_lecture_duration"].loc[i] = round(self.df["total_lecture_duration"].loc[i]/10)*10

        ##title word count##
           noise = self.df["title_word_count"] * np.random.normal(0., 1., self.df.shape[0]) * 0.1
           self.df["title_word_count"] = (self.df["title_word_count"] + noise).round().astype("int")

       num_folds=5
       kf = KFold(n_splits=num_folds, random_state=42, shuffle=True)
       self.df["fold"] = 0

       idx = 1
       for _, test_index in kf.split(self.df):
           _tmp = self.df.index.isin(test_index)
           self.df.loc[_tmp, "fold"] = idx
           idx += 1

       self.df.sort_values(by="fold", inplace=True)

       self.df.to_csv('/home/meghana/Desktop/VLEngagement/Anonymous_dataset.csv')
       print("")






new_dataset=Anonymous_Dataset(PATH_TO_DATASET_1)
new_dataset.create_dataframe()
print("")

