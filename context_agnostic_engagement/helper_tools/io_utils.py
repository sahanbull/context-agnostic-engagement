import pandas as pd

MIN_NUM_SESSIONS = 5

GEN_FEATURES = ['id', 'fold']

CONT_COLS = ['categories', 'freshness',
             'auxiliary_rate', 'conjugate_rate', 'normalization_rate', 'tobe_verb_rate', 'preposition_rate',
             'pronoun_rate', 'document_entropy', 'easiness', 'fraction_stopword_coverage',
             'fraction_stopword_presence', 'title_word_count', 'word_count']

WIKI_COLS = ['auth_topic_rank_1_url', 'auth_topic_rank_1_score',
             'auth_topic_rank_2_url', 'auth_topic_rank_2_score',
             'auth_topic_rank_3_url', 'auth_topic_rank_3_score',
             'auth_topic_rank_4_url', 'auth_topic_rank_4_score',
             'auth_topic_rank_5_url', 'auth_topic_rank_5_score',
             'coverage_topic_rank_1_url', 'coverage_topic_rank_1_score',
             'coverage_topic_rank_2_url', 'coverage_topic_rank_2_score',
             'coverage_topic_rank_3_url', 'coverage_topic_rank_3_score',
             'coverage_topic_rank_4_url', 'coverage_topic_rank_4_score',
             'coverage_topic_rank_5_url', 'coverage_topic_rank_5_score']

VID_COLS = ['duration', 'type', 'has_parts', "speaker_speed", 'silent_period_rate']

MEAN_ENGAGEMENT_RATE = 'mean_engagement'
MED_ENGAGEMENT_RATE = 'med_engagement'
MEAN_STAR_RATING = 'mean_star_rating'
VIEW_COUNT = "view_count"

LABEL_COLS = [MEAN_ENGAGEMENT_RATE, MED_ENGAGEMENT_RATE]

DOMAIN_COL = "categories"
ID_COL = "id"

COL_VER_1 = CONT_COLS
COL_VER_2 = CONT_COLS + WIKI_COLS
COL_VER_3 = CONT_COLS + WIKI_COLS + VID_COLS


def vectorise_video_features(lectures, columns):
    """converts the video specific categorical variables to one-hot encoding

    Args:
        lectures (pd.DataFrame): pandas DataFrame that has lectures dataset
        columns ([str]): set of feature columns

    Returns:
        lectures (pd.DataFrame): pandas DataFrame with updated columns that are one hot encoded
        columns ([str]): updated set of feature columns

    """
    dummies = pd.get_dummies(lectures['type']).rename(columns=lambda x: 'type_' + str(x))
    for col in dummies.columns:
        lectures[col] = dummies[col]
    columns += list(dummies.columns)
    columns.remove("type")

    return lectures, columns


def _wikititle_from_url(url):
    title = url.split("/")[-1]
    return title.strip()


def vectorise_wiki_features(lectures, columns):
    """converts the wikipedia specific categorical variables (topic 1 page rank and topic 1 cosine) to one-hot encoding

    Args:
        lectures (pd.DataFrame): pandas DataFrame that has lectures dataset
        columns ([str]): set of feature columns

    Returns:
        lectures (pd.DataFrame): pandas DataFrame with updated columns that are one hot encoded
        columns ([str]): updated set of feature columns

    """
    # get pageRank URL
    col_name = "auth_topic_rank_1_url"
    lectures[col_name] = lectures[col_name].apply(_wikititle_from_url)

    dummies = pd.get_dummies(lectures[col_name]).rename(columns=lambda x: 'authority_' + str(x))
    for col in dummies.columns:
        lectures[col] = dummies[col]
    columns += list(dummies.columns)

    # get cosine URL
    col_name = "coverage_topic_rank_1_url"
    lectures[col_name] = lectures[col_name].apply(_wikititle_from_url)

    dummies = pd.get_dummies(lectures[col_name]).rename(columns=lambda x: 'coverage_' + str(x))
    for col in dummies.columns:
        lectures[col] = dummies[col]
    columns += list(dummies.columns)

    for col in WIKI_COLS:
        columns.remove(col)

    lectures.drop(WIKI_COLS, axis='columns', inplace=True)

    return lectures, columns


def _numerise_categorical(lectures):
    # lectures["language"] = lectures["language"].apply(lambda l: 1 if l == "en" else 0)
    lectures["categories"] = lectures["categories"].apply(lambda l: 1 if l == "stem" else 0)

    return lectures


def transform_features(lectures):
    """converts the string represented metadata related features to numeric features.
    Args:
        lectures (pd.DataFrame): pandas DataFrame that has lectures dataset

    Returns:
        lectures (pd.DataFrame): pandas DataFrame with updated columns that are one hot encoded

    """
    lectures = _numerise_categorical(lectures)

    return lectures


def load_lecture_dataset(input_filepath, col_version=1):
    """ takes in a distributed path to lecture data and pulls the data

    Args:
        input_filepath (str): input filepath where the dataset CSV file is.
        col_version (int): column version that defines the set of features being considered (could be 1, 2 or 3)

    Returns:
        lectures (pd.DataFrame): pandas DataFrame containing all the relevant fields from lectures data
    """
    if col_version == 1:
        columns = GEN_FEATURES + COL_VER_1
    elif col_version == 2:
        columns = GEN_FEATURES + COL_VER_2
    else:
        columns = GEN_FEATURES + COL_VER_3

    lectures = pd.read_csv(input_filepath)

    columns += LABEL_COLS

    return lectures[columns]


def get_label_from_dataset(label_param):
    """gets actual label column name based on parameter

    Args:
        label_param (str): label parameter defined in the traning scripts.

    Returns:
        (str): column name of the relevant label as per the dataset.

    """
    if label_param == "mean":
        return MEAN_ENGAGEMENT_RATE
    elif label_param == "median":
        return MED_ENGAGEMENT_RATE
    elif label_param == "rating":
        return MEAN_STAR_RATING
    else:
        return VIEW_COUNT


def get_features_from_dataset(col_cat, lectures):
    """returns the correct set of feature column names and the relevant columns from the dataset.

    Args:
        col_cat (int): column category parameter that defines the final feature set.
        lectures (pd.DataFrame): pandas DataFrame with the full dataset including all features

    Returns:
        lectures (pd.DataFrame): pandas DataFrame with the full dataset including relevant features
        columns ([str]): list of column names relevant to the column category

    """
    if col_cat == 1:
        columns = COL_VER_1
        lectures = transform_features(lectures)

    if col_cat == 2:
        columns = COL_VER_2
        lectures = transform_features(lectures)
        # add wiki features
        lectures, columns = vectorise_wiki_features(lectures, columns)

    if col_cat == 3:
        columns = COL_VER_3
        lectures = transform_features(lectures)
        # add wiki features
        lectures, columns = vectorise_wiki_features(lectures, columns)
        # add video features
        lectures, columns = vectorise_video_features(lectures, columns)

    return columns, lectures


def get_fold_from_dataset(lectures, fold):
    fold_train_df = lectures[lectures["fold"] != fold].reset_index(drop=True)
    fold_test_df = lectures[lectures["fold"] == fold].reset_index(drop=True)

    return fold_train_df, fold_test_df


def get_pairwise_version(df, is_gap, label_only=False):
    """Get the pairwise representation of the lecture dataset

    Args:
        df (spark.DataFrame): spark DataFrame that need to transformed to pairwise format
        is_gap (bool): is gap between the features are calculated
        label_only (bool): are only the labels being considered

    Returns:
        cross_df (spark.DataFrame): park DataFrame that is transformed to pairwise format

    """
    from pyspark.sql import functions as func

    if label_only:
        tmp_columns = [ID_COL, DOMAIN_COL] + LABEL_COLS
        df = df.select(tmp_columns)

    _df = df
    cols = set(_df.columns)

    # rename columns
    for col in cols:
        _df = _df.withColumnRenamed(col, "_" + col)

    # do category wise pairing on different observations from the category
    cross_df = (df.crossJoin(_df).
                where(func.col(ID_COL) != func.col("_" + ID_COL)))

    if is_gap:
        gap_cols = cols
        for col in gap_cols:
            cross_df = cross_df.withColumn("gap_" + col, func.col(col) - func.col("_" + col))

    if label_only:
        cross_df = cross_df.select(
            [ID_COL, "_" + ID_COL, DOMAIN_COL] + ["gap_" + c for c in LABEL_COLS])

    return cross_df
