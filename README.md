# VLEngagement: A Dataset of Video Lectures for Evaluating Population-based Engagement

This repository contains the dataset and source code of the experiments conducted at reported using the VLEngagement 
Dataset. The VLEngagement dataset provides a set of statistics aimed at studying population-based engagement 
in video lectures, together with other conventional metrics in subjective assessment such as average star ratings and 
number of views.  We believe the dataset will serve the community applying AI in Education to further understand what 
are the features of educational material that makes it engaging for learners.

## Use Cases and Impact
VLEngagement dataset can be considered as a highly impactful resource contribution to the research community as it will 
enable a whole new line of research that is geared towards next generation information and knowledge management within 
educational repositories, Massively Open Online Course platforms and other  Video platforms. The Dataset is a pivotal 
milestone in uplifting **sustainability** of future knowledge systems having direct impact scalable, automatic quality 
assurance [(1)](https://www.k4all.org/wp-content/uploads/2019/08/IJCAI_paper_on_quality.pdf), 
[(2)](https://arxiv.org/pdf/2006.00592.pdf) and personalised education [(3)](https://arxiv.org/pdf/1912.01592.pdf). It 
improves **transparency** by allowing the interpretation of humanly intuitive features and their influence in 
population-based engagement prediction. 

This dataset complements the ongoing effort of understanding learner engagement in video lectures 
[(5)](DOI:https://doi.org/10.1145/2556325.2566239). However, it dramatically uplifts the research landscape by formally 
establishes two objectively measurable novel tasks related to predicting engagement of educational 
videos while making a significantly large, more-focused dataset and its baselines available to the research community. 
AI in Education, Intelligent Tutoring and Educational Data Mining communities are on a rapid growth trajectory right now. 
The simultaneously growing need for scalable, personalised learning solutions makes this dataset a central piece within 
community for many more years to come.     

## Using the Dataset and Its Tools
The resource is developed in a way that any researcher with very basic technological literacy can start building on top 
of this dataset. 
- The dataset is provided in `Comma Seperate Values (CSV)` format making it *human-readable* while being accessible 
through a wide range of data manipulation and statistical software suites. 
- The resource includes 
`helper_tools` ([Found Here](https://github.com/sahanbull/context-agnostic-engagement/tree/master/context_agnostic_engagement/helper_tools))
 that provides a set of functions that any researcher with *basic python knowledge* can use to interact with the dataset 
 and also evaluate the built models.
- `models.regression` ([Found Here](https://github.com/sahanbull/context-agnostic-engagement/tree/master/context_agnostic_engagement/models/regression))
provides *well-documented example code snippets* that can 1) enable the researcher to reproduce results reported for 
baseline models, 2) use an example coding snippets to understand how to build novel models using the VLEngagement dataset.
- `feature_extraction` ([Found Here](https://github.com/sahanbull/context-agnostic-engagement/tree/master/context_agnostic_engagement/feature_extraction))
 module presents the programming logic of how features in the dataset are calculated. The feature extraction logic is 
 presented in the form of *well-documented (PEP-8 standard, Google Docstrings format)* Python functions that can be used
 to 1) understand the logic behind feature extraction or 2) apply the feature extraction logic to your own lecture records
 to generate more data
 
 ## Structure of the Resource

The structure of the repository divides the resources to two distinct components on top-level.
1. `VLEngagement_datasets`: This section stores the different versions of VLEngagement datasets (current version: `v1`)  
2. `contenxt_agnostic_engagement`: This module stores all the code related to manipulating and managing the datasets. 

In addition, there are two files:
- `README.md`: The main source of information for understanding and working with the VLEngagement datasets.
- `setup.py`: Python setup file that will install the support tools to your local python environment. 
 
### Table of Contents
- [VLEngagement Datasets](#vlengagement-datasets)
    - [Anonymity](#anonymity)
    - [Versions](#versions)
    - [Features](#features)
        - [General Features](#general-features)
        - [Content-based Features](#content-based-features)
        - [Wikipedia-based Features](#wikipedia-based-features)
        - [Video-specific Features](#video-specific-features)
- [`content_agnostic_engagement` Module](#content_agnostic_engagement-module)
    - [`feature_extraction`](#feature_extraction)
    - [`helper_tools`](#helper_tools)
    - [`models`](#models)
- [References](#references)
        

## VLEngagement Datasets
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
 
### Features
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
is calculated using Milne and Witten method [(4)](https://www.aaai.org/Papers/Workshops/2008/WS-08-15/WS08-15-005.pdf). 
PageRank is run on the semantic graph to identify the most authoritative topics within the lecture. The top-5 most 
authoritative topic URLs and their respective PageRank value is included in the dataset.  

- Most Convered Topics
Similarly, the [Cosine Similarity](https://www.sciencedirect.com/topics/computer-science/cosine-similarity) between
 the Wikipedia topic page and the lecture transcript is used to rank the Wikipedia topics that are most covered in the 
 video lecture. The top-5 most covered topic URLs and their respective cosine similarity value is included in the 
 dataset.

#### Video-specific Features
Video-specific features are extracted and included in the dataset. Most of the features in this category are motivated
by prior work analyses done on engagement in video lectures [(5)](https://doi.org/10.1145/2556325.2566239). 

## `content_agnostic_engagement` Module
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
- `io_utils`: contains the helper functions that are required for loading and manipulating the dataset. 

### `models` 
This module contains the python scripts that have been used to create the current baselines. Currently, `regression` 
models have been proposed as baseline models for the tasks. The two files `models/regression/train_gbm_regression_full_cv.py` 
and `models/regression/train_rf_regression_full_cv.py` can be used to reproduce the baseline performance for Gradient 
Boosting Machines (GBM) and Random Forests (RM) models.



## References
(1) Sahan Bulathwela, Emine Yilmaz, and John Shawe-Taylor (2019). Towards Automatic, Scalable Quality Assurance in Open 
Education.", In workshop on Artificial Intelligence for United Nations SDGs at International Joint Conference in 
Artificial Intelligence (IJCAI '19), https://www.k4all.org/wp-content/uploads/2019/08/IJCAI_paper_on_quality.pdf.
 
(2) Sahan Bulathwela, Maria Perez-Ortiz, Aldo Lipani, Emine Yilmaz, and John Shawe-Taylor (2020). Predicting Engagement 
in Video Lectures. In Proc. of Int. Conf. on Educational Data Mining (EDM ’20).  https://arxiv.org/pdf/2006.00592.pdf

(3) Sahan Bulathwela, Maria Perez-Ortiz, Emine Yilmaz, and John Shawe-Taylor (2020). 
Towards an Integrative Educational Recommender for Lifelong Learners. In AAAI Conference on Artificial Intelligence 
(AAAI ’20), https://arxiv.org/pdf/1912.01592.pdf

(4) David Milne, Ian H. Witten (2008) An effective, low-cost measure of semantic relatedness obtained from Wikipedia 
links. In Proceedings of the first AAAI Workshop on Wikipedia and Artificial Intelligence, Chicago, I.L 

(5) Philip J. Guo, Juho Kim, and Rob Rubin (2014). How video production affects student engagement: an empirical study 
of MOOC videos. In Proceedings of the first ACM conference on Learning @ scale conference (L@S ’14).
 Association for Computing Machinery, New York, NY, USA, 41–50. DOI:https://doi.org/10.1145/2556325.2566239