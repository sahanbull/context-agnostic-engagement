import pandas as pd

MIN_NUM_SESSIONS = 5

GEN_FEATURES = ['id', 'fold']

CONT_COLS = ['language', 'domain', 'published_date',
             'auxiliary_rate', 'conjugate_rate', 'normalization_rate', 'tobe_verb_rate', 'preposition_rate',
             'pronoun_rate', 'document_entropy', 'easiness', 'fraction_stopword_coverage',
             'fraction_stopword_presence', 'title_word_count', 'word_count']

WIKI_COLS = ['topic_1_pageRank_url', 'topic_1_pageRank_val', 'topic_2_pageRank_url', 'topic_2_pageRank_val',
             'topic_3_pageRank_url', 'topic_3_pageRank_val', 'topic_4_pageRank_url', 'topic_4_pageRank_val',
             'topic_5_pageRank_url', 'topic_5_pageRank_val', 'topic_1_cosine_url', 'topic_1_cosine_val',
             'topic_2_cosine_url', 'topic_2_cosine_val', 'topic_3_cosine_url', 'topic_3_cosine_val',
             'topic_4_cosine_url', 'topic_4_cosine_val', 'topic_5_cosine_url', 'topic_5_cosine_val']

VID_COLS = ['duration', 'type', 'is_chunked', "speaker_speed", 'silent_period_rate']

MEAN_ENGAGEMENT_RATE = 'mean_engagement_rate'
MED_ENGAGEMENT_RATE = 'median_engagement_rate'
MEAN_STAR_RATING = 'mean_star_rating'
VIEW_COUNT = "view_count"

LABEL_COLS = [MEAN_ENGAGEMENT_RATE, MED_ENGAGEMENT_RATE]

DOMAIN_COL = "domain"
ID_COL = "id"

COL_VER_1 = CONT_COLS
COL_VER_2 = CONT_COLS + WIKI_COLS
COL_VER_3 = CONT_COLS + WIKI_COLS + VID_COLS


def vectorise_video_features(lectures, columns):
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
    # get pageRank URL
    col_name = "topic_1_pageRank_url"
    lectures[col_name] = lectures[col_name].apply(_wikititle_from_url)

    dummies = pd.get_dummies(lectures[col_name]).rename(columns=lambda x: 'authority_' + str(x))
    for col in dummies.columns:
        lectures[col] = dummies[col]
    columns += list(dummies.columns)

    # get cosine URL
    col_name = "topic_1_cosine_url"
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
    lectures["language"] = lectures["language"].apply(lambda l: 1 if l == "en" else 0)
    lectures["domain"] = lectures["domain"].apply(lambda l: 1 if l == "stem" else 0)

    return lectures


def transform_features(lectures):
    lectures = _numerise_categorical(lectures)

    return lectures


def load_lecture_dataset(input_filepath, col_version=1):
    """ takes in a distributed path to lecture data and pulls the data

    Args:
        spark (SparkSession): Spark session object
        input_filepath (str): input filepath

    Returns:
        lectures (DataFrame): dataframe containing all the relevant fields from lectures data
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
    if label_param == "mean":
        return MEAN_ENGAGEMENT_RATE
    elif label_param == "median":
        return MED_ENGAGEMENT_RATE
    elif label_param == "rating":
        return MEAN_STAR_RATING
    else:
        return VIEW_COUNT


def get_features_from_dataset(col_cat, lectures):
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


def get_pairwise_version(df, is_gap, label_only=False, labels=None):
    """Get the pairwise

    Args:
        df:
        is_gap:

    Returns:

    """
    if label_only:
        tmp_columns = [ID_COL, DOMAIN_COL] + LABEL_COLS
        df = df.select(tmp_columns)

    from pyspark.sql import functions as func
    if labels is None:
        labels = []

    _df = df
    cols = set(_df.columns)

    # rename columns
    for col in cols:
        _df = _df.withColumnRenamed(col, "_" + col)

    # do category wise pairing on different observations from the category
    cross_df = (df.crossJoin(_df).
                where(func.col(ID_COL) != func.col("_" + ID_COL)))

    if is_gap:
        # gap_cols = cols - set(LABEL_UNCERTAINTY_COLS + [LECT_ID_COL, CAT_COL])
        gap_cols = cols
        for col in gap_cols:
            cross_df = cross_df.withColumn("gap_" + col, func.col(col) - func.col("_" + col))

    # cross_df = cross_df.drop("_" + CAT_COL)

    if labels:
        return cross_df.select(labels)

    if label_only:
        cross_df = cross_df.select(
            [ID_COL, "_" + ID_COL, DOMAIN_COL] + ["gap_" + c for c in LABEL_COLS])

    return cross_df
