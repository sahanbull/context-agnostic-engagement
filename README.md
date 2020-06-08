# VLEngagement: A Dataset of Video Lectures for Evaluating Population-based Engagement

This repository contains the dataset and source code of the experiments conducted at reported using the VLEngagement 
Dataset. The VLEngagement dataset provides a set of statistics aimed at studying population-based engagement 
in video lectures, together with other conventional metrics in subjective assessment such as average star ratings and 
number of views. We believe the dataset will serve the intelligent tutoring community to further 
understand what are the features of educational material that makes it engaging for learners. 

The structure of the repository divides the resources to two distinct components on top-level.
1. `VLEngagement_datasets`: This section stores the different versions of VLEngagement datasets (current version: `v1`)  
2. `contenxt_agnostic_engagement`: This module stores all the code related to manipulating and managing the datasets. 

In addtional, there are two files:
- `README.md`: The main source of information for understanding and working with the VLEngagement datasets.
- `setup.py`: Python setup file that will install the support tools to your local python environment. 

## Impact
-to be added

## 1. VLEngagement Datasets
This section makes the VLEngagement datasets publicly available. The VLEngagement dataset is constructed using the
 aggregated video lectures consumption data coming from a popular OER repository, 
 [VideoLectures.Net](http://videolectures.net/). These videos are recorded when researchers are presenting their work at 
 peer-reviewed conferences. Lectures are reviewed and hence material is controlled for correctness of knowledge and 
 pedagogical robustness. 
 
 ### Anonymity
 We restrict the final dataset to lectures that have been viewed by at least 5 unique users to preserve anonymity of 
 users and have reliable engagement measurements. Additionally, a regime of techniques are used for preserving the
  anonymity of the data authors using the remaining features. Rarely occurring values in *Lecture Type* feature were 
  grouped together to create the `other` category. *Language* feature is grouped into `en` and `non-en` categories. 
  Similarly, Domain category groups Life Sciences, Physics, Technology, Mathematics, Computer Science, Data Science 
  and Computers subjects to `stem` category and the other subjects to `misc` category. Rounding is used with 
  *Published Date*, rounding to the nearest 10 days. *Lecture Duration* is rounded to the nearest 10 seconds. 
  Gaussian white noise (10%) is added to *Title Word Count* feature and rounded to the nearest integer.

### Versions
All the relevant datasets are available as a Comma Separated Value (CSV) file within a version subdirectory 
(eg. `v1/VLEngagement_dataset_v1.cssv`). The current latest version of the dataset is `v1`. The tools required to load,
and manipulate the dataset are found in `context_agnostic_engagement.utils.io_utils` module.  
 
### Feature Extraction
There 4 main types of features extracted from the video lectures. These features can be categorised into six quality 
verticals [(1)](https://www.k4all.org/wp-content/uploads/2019/08/IJCAI_paper_on_quality.pdf). The overview of the set of XX features provided in the 
dataset is found in table 1.

Table here !!!!

#### General Features
Features that extracted from Lecture metadata that are associated with the language and subject of the materials.

#### Content-based Features
Features that have been extracted from the contents that are discussed within the lecture. These features are extracted
using the content transcript in English lectures. Features are extracted from the English translation where the lecture
is a non-english lecture. The transcription and translation services are provided by the 
[TransLectures](https://www.mllp.upv.es/projects/translectures/) project.

#### Wikipedia-based Features
Two features groups that associate to *content authority* and *topic coverage* are extracted by connecting the lecture 
transcript to Wikipedia. [Entity Linking](http://www.wikifier.org/) technology is used to identify Wikipedia concepts 
that are asscoated with the lecture contents. 

- Most Authoritative Topics
The Wikipedia topics in the lecture are used to build a Semantic graph of the lecture where the *Semantic Relatedness* 
is calculated using Milne and Witten method [(2)](https://www.aaai.org/Papers/Workshops/2008/WS-08-15/WS08-15-005.pdf). 
PageRank is run on the semantic graph to identify the most authoritative topics within the lecture. The top-5 most 
authoritative topic URLs and their respective PageRank value is included in the dataset.  

- Most Convered Topics
Similarly, the [Cosine Similarity](https://www.sciencedirect.com/topics/computer-science/cosine-similarity) between
 the Wikipedia topic page and the lecture transcript is used to rank the Wikipedia topics that are most covered in the 
 video lecture. The top-5 most covered topic URLs and their respective cosine similarity value is included in the 
 dataset.

#### Video-specific Features
Video-specific features are extracted and included in the dataset. Most of the features in this category are motivated
by prior work analyses done on engagement in video lectures [(3)](https://doi.org/10.1145/2556325.2566239). 

## 2. `content_agnostic_engagement` Module
This section contains the code that enables the research community to work with the VLEngagement dataset. The folder
structure in this section logically separates the code into three modules.
### `feature_extraction`
This section contains the programming logic of the functions used for feature extraction. The main use of this module
is when one is interested in populating the features for their own lecture corpus using the exact programming logic used
to populate VLEngagement data. Several files with feature extraction related functions are found in this module.
- `_api_utils.py`: Internal functions relevant to making API calls to the [Wikifier](http://www.wikifier.org/).
- `_text_utils.py`: Internal functions relevant to utility functions for handling text.
- `content_based_features`: Functions and logic associated with extracting content-based features.
- `wikipedia_based_features`: Functions and logic associated with extracting Wikipedia-based features.

### `helper_tools`
This module includes the helper tools that are useful in working with the dataset. The two main submodules contain 
helper functions relating to evaluation and input-output operations. 
- `evaluation_metrics`: contains the helper functions to run Root Mean Sqaure Error (RMSE), Spearman's Rank Order 
Correlation Coefficient (SROCC) and Pairwise Ranking Accuracy (Pairwise). 
- io_utils: contains the helper functions that are required for loading and manipulating the dataset. 

### `models` 
This module contains the python scripts that have been used to create the current baselines. Currently, `regression` 
models have been proposed as baseline models for the tasks. The two files `models/regression/train_gbm_regression_full_cv.py` 
and `models/regression/train_rf_regression_full_cv.py` can be used to reproduce the baseline performance for Gradient 
Boosting Machines (GBM) and Random Forests (RM) models.



## References
[1] Sahan Bulathwela, Emine Yilmaz, and John Shawe-Taylor (2019). Towards Automatic, Scalable Quality Assurance in Open 
Education.", In workshop on AI in United Nations SDGs at International Joint Conference in Artificial Intelligence,
 https://www.k4all.org/wp-content/uploads/2019/08/IJCAI_paper_on_quality.pdf.

[2] David Milne, Ian H. Witten (2008) An effective, low-cost measure of semantic relatedness obtained from Wikipedia 
links. In Proceedings of the first AAAI Workshop on Wikipedia and Artificial Intelligence, Chicago, I.L 

[3] Philip J. Guo, Juho Kim, and Rob Rubin. 2014. How video production affects student engagement: an empirical study 
of MOOC videos. In Proceedings of the first ACM conference on Learning @ scale conference (L@S ’14).
 Association for Computing Machinery, New York, NY, USA, 41–50. DOI:https://doi.org/10.1145/2556325.2566239