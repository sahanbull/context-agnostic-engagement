import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

PATH_TO_DATASET_1="/home/meghana/Desktop/VLEngagement/new_dataset.csv"

CATEGORIES="categories"
TYPE="type"
WORD_COUNT="word_count"
DOCUMENT_ENTROPY="document_entropy"
TITLE_WORD_COUNT="title_word_count"
EASINESS="easiness"
FRACTION_STOPWORD_PRESENCE="fraction_stopword_presence"
FRACTION_STOPWORD_COVERAGE="fraction_stopword_coverage"
PREPOSITION_RATE="preposition_rate"
AUXILIARY_RATE="auxiliary_rate"
TOBE_VERB_RATE="tobe_verb_rate"
CONJUGATE_RATE="conjugate_rate"
NORMALIZATION_RATE="normalization_rate"
PRONOUN_RATE="pronoun_rate"
FRACTION_SILENT_WORDS="fraction_silent_words"
MIN_ENGAGEMENT="min_engagement"
MAX_ENGAGEMENT="max_engagement"
MED_ENGAGEMENT="med_engagemet"
MEAN_ENGAGEMENT="mean_engagement"
SD_ENGAGEMENT="sd_engagement"
NUM_LEARNERS="num_learners"
NUM_VIEWS="num_views"
TOTAL_LECTURE_DURATION="total_lecture_duration"
TOTAL_WORDS_DURATION="total_words_duration"

TIME="time"
DURATION="duration"

AUTH_TOPIC_RANK_1_SCORE="auth_topic_rank_1_score"
AUTH_TOPIC_RANK_2_SCORE="auth_topic_rank_2_score"
AUTH_TOPIC_RANK_3_SCORE="auth_topic_rank_3_score"
AUTH_TOPIC_RANK_4_SCORE="auth_topic_rank_4_score"
AUTH_TOPIC_RANK_5_SCORE="auth_topic_rank_5_score"

COVERAGE_TOPIC_RANK_1_SCORE="coverage_topic_rank_1_score"
COVERAGE_TOPIC_RANK_2_SCORE="coverage_topic_rank_2_score"
COVERAGE_TOPIC_RANK_3_SCORE="coverage_topic_rank_3_score"
COVERAGE_TOPIC_RANK_4_SCORE="coverage_topic_rank_4_score"
COVERAGE_TOPIC_RANK_5_SCORE="coverage_topic_rank_5_score"


class Dataset:

    def __init__(self,path_to_dataset):
       self.path=path_to_dataset

    def create_dataframe(self):
       self.df = pd.read_csv(self.path)
       #count_1=self.df[self.df["word_count"]>0 & (self.df["language"]=="en")].shape[0]
       #and self.df["language"] == "en"

    def size_dataset(self):
       self.num_of_observations=self.df.shape[0]
       self.num_of_features=self.df.shape[1]

    def categories_stats(self):
       categories = self.df[self.df["language"]=="en"][CATEGORIES].values
       list_remove_indexes=[]
       for i in range(len(categories)):
           if type(categories[i])!=float:
               categories[i]=categories[i].split('|')
           else:
               list_remove_indexes.append(i)
       categories = np.delete(categories,list_remove_indexes)
       flattened_categories = [y for x in categories for y in x]
       (unique, counts) = np.unique(flattened_categories, return_counts=True)
       frequencies = np.asarray((unique, counts)).T
       fig, ax = plt.subplots()
       #g=sns.displot(flattened_categories)
       #g = plt.hist(flattened_categories, align='left')
       # #plt.xticks(rotation=60)
       # for label in ax.xaxis.get_xticklabels():
       #     label.set_horizontalalignment('left')
       # g.set_xticklabels(rotation=60)
       # plt.tight_layout()
       # plt.show()
       # pie, ax = plt.subplots(figsize=[10, 6])
       # labels = unique.tolist()
       # _,_,pct_text=plt.pie(x=counts.tolist(), autopct="%.1f%%", explode=[0.03] * len(counts.tolist()), labels=labels, pctdistance=1.2,labeldistance=1.3,rotatelabels=30)
       # for txt in pct_text:
       #  txt.set_rotation(60)
       # plt.title("Categories distribution", fontsize=14);
       # plt.show()
       fig, ax = plt.subplots(figsize=(12, 6))
       #plt.boxplot(self.df[self.df['total_lecture_duration']<500000]['total_lecture_duration'])
       #plt.boxplot(self.df['duration'])
       #ax.set_ylim([0,1000])
       sns.displot(self.df[self.df["duration"]<40000],x="duration",kind="kde")
       plt.show()

    def univariate_analysis(self,list_variables):
        for i in range(len(list_variables)):
            max_variable=np.max(self.df[list_variables[i]])
            min_variable=np.min(self.df[list_variables[i]])
            print("Statistics for: ",list_variables[i])
            print("Maximum Value: ",max_variable)
            print("Minimum Value: ", min_variable)

    def multivariate_analysis(self):
        full_data_corr = self.df.corr(method='pearson')
        mask = np.zeros_like(full_data_corr, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        # f, ax = plt.subplots(figsize=(11, 9))
        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(full_data_corr, cmap=cmap, vmin=-1., vmax=1., center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5})
        plt.tight_layout()
        plt.show()

    def lecture_type_stats(self):
       self.lecture_types=self.df[self.df["language"]=="en"][TYPE].values
       (unique, counts) = np.unique(self.lecture_types, return_counts=True)
       frequencies = np.asarray((unique, counts)).T
       # g = sns.displot(self.lecture_types)
       # plt.tight_layout()
       # plt.show()

list_of_variables=[WORD_COUNT,TITLE_WORD_COUNT,
    DOCUMENT_ENTROPY,
    EASINESS,
FRACTION_STOPWORD_PRESENCE,
FRACTION_STOPWORD_COVERAGE,
PREPOSITION_RATE,
AUXILIARY_RATE,
TOBE_VERB_RATE,
CONJUGATE_RATE,
NORMALIZATION_RATE,
PRONOUN_RATE,
FRACTION_SILENT_WORDS,
NUM_LEARNERS,
NUM_VIEWS,
TOTAL_LECTURE_DURATION,
TOTAL_WORDS_DURATION,
TIME,
DURATION,
AUTH_TOPIC_RANK_1_SCORE,
AUTH_TOPIC_RANK_2_SCORE,
AUTH_TOPIC_RANK_3_SCORE,
AUTH_TOPIC_RANK_4_SCORE,
AUTH_TOPIC_RANK_5_SCORE,
COVERAGE_TOPIC_RANK_1_SCORE,
COVERAGE_TOPIC_RANK_2_SCORE,
COVERAGE_TOPIC_RANK_3_SCORE,
COVERAGE_TOPIC_RANK_4_SCORE,
COVERAGE_TOPIC_RANK_5_SCORE
                   ]

new_dataset=Dataset(PATH_TO_DATASET_1)
new_dataset.create_dataframe()
new_dataset.size_dataset()
#new_dataset.multivariate_analysis()
#new_dataset.univariate_analysis(list_of_variables)
#new_dataset.lecture_type_stats()
new_dataset.categories_stats()
print("")

