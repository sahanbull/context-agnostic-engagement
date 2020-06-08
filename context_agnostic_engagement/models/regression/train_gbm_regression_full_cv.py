from pyspark.sql import SparkSession

import pandas as pd
import numpy as np

from os.path import join
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib

from sklearn.model_selection import GridSearchCV

from context_agnostic_engagement.utils.io_utils import load_lecture_dataset, ID_COL, DOMAIN_COL, COL_VER_1, COL_VER_2, \
    COL_VER_3, MEAN_ENGAGEMENT_RATE, MED_ENGAGEMENT_RATE, transform_features, vectorise_wiki_features, \
    vectorise_video_features, get_pairwise_version


def main(args):
    spark = (SparkSession.
             builder.
             config("spark.driver.memory", "4g").
             config("spark.executor.memory", "4g").
             config("spark.driver.maxResultSize", "4g").
             config("spark.rpc.lookupTimeout", "300s").
             config("spark.rpc.lookupTimeout", "300s").
             config("spark.master", "local[{}]".format(args["k_folds"]))).getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    performance_values = []

    folds = args["k_folds"]
    jobs = args["n_jobs"]
    col_cat = args['feature_cat']

    lectures = load_lecture_dataset(args["training_data_filepath"], col_version=col_cat)

    if args["label"] == "mean":
        label = MEAN_ENGAGEMENT_RATE
    else:
        label = MED_ENGAGEMENT_RATE

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

    cnt = 1
    # make pairwise observations
    for i in range(folds):
        fold_train_df = lectures[lectures["fold"] != cnt].reset_index(drop=True)
        fold_test_df = lectures[lectures["fold"] == cnt].reset_index(drop=True)

        X_train, Y_train = fold_train_df[columns], np.array(fold_train_df[label])
        X_test, Y_test = fold_test_df[columns], np.array(fold_test_df[label])

        if args["is_log"]:
            # log transformation of the data
            Y_train = np.log(Y_train)
            Y_test = np.log(Y_test)

        params = {'n_estimators': [100, 500, 750, 1000],
                  'max_depth': [3, 5, 10, 25],
                  'random_state': [42],
                  "min_samples_split": [2, 6, 10],
                  "learning_rate": [.001, .01, .1]}

        print("\n\n\n ========== dataset {} created !!! ===========\n\n".format(cnt))
        print("no. of features: {}".format(X_train.shape[1]))
        print("training data size: {}".format(len(X_train)))
        print("testing data size: {}\n\n".format(len(X_test)))

        grid_model = GridSearchCV(GradientBoostingRegressor(), params, cv=folds, n_jobs=jobs, refit=True)
        grid_model.fit(X_train, Y_train)

        train_pred = grid_model.predict(X_train)

        print("Model Trained...")

        test_pred = grid_model.predict(X_test)

        joblib.dump(grid_model, join(args["output_dir"], "model_{}.pkl".format(cnt)), compress=True)

        if args["is_log"]:
            Y_train = np.exp(Y_train)
            train_pred = np.exp(train_pred)
            Y_test = np.exp(Y_test)
            test_pred = np.exp(test_pred)

        from sklearn import metrics as skm
        from scipy.stats import spearmanr

        train_rmse = np.sqrt(skm.mean_squared_error(Y_train, train_pred))
        test_rmse = np.sqrt(skm.mean_squared_error(Y_test, test_pred))

        train_spearman = spearmanr(Y_train, train_pred)
        test_spearman = spearmanr(Y_test, test_pred)

        train_Y_p = spark.createDataFrame(fold_train_df)
        train_Y_p = get_pairwise_version(train_Y_p, is_gap=True, label_only=True).toPandas()[
            [ID_COL, "_" + ID_COL, "gap_" + label, DOMAIN_COL]]

        predict_train_Y_p = fold_train_df
        predict_train_Y_p[label] = train_pred
        predict_train_Y_p = spark.createDataFrame(predict_train_Y_p)
        predict_train_Y_p = \
            get_pairwise_version(predict_train_Y_p, is_gap=True, label_only=True).toPandas()[
                [ID_COL, "_" + ID_COL, "gap_" + label, DOMAIN_COL]]

        test_Y_p = spark.createDataFrame(fold_test_df)
        test_Y_p = get_pairwise_version(test_Y_p, is_gap=True, label_only=True).toPandas()[
            [ID_COL, "_" + ID_COL, "gap_" + label, DOMAIN_COL]]

        predict_test_Y_p = fold_test_df
        predict_test_Y_p[label] = test_pred
        predict_test_Y_p = spark.createDataFrame(predict_test_Y_p)
        predict_test_Y_p = \
            get_pairwise_version(predict_test_Y_p, is_gap=True, label_only=True).toPandas()[
                [ID_COL, "_" + ID_COL, "gap_" + label, DOMAIN_COL]]

        train_accuracy = skm.accuracy_score(train_Y_p["gap_" + label] > 0.,
                                            predict_train_Y_p["gap_" + label] > 0., normalize=True)
        test_accuracy = skm.accuracy_score(test_Y_p["gap_" + label] > 0.,
                                           predict_test_Y_p["gap_" + label] > 0., normalize=True)

        best_model = {}
        best_model["params"] = "{}_{}".format(grid_model.best_estimator_.n_estimators,
                                              grid_model.best_estimator_.max_depth)
        best_model["n_estimators"] = grid_model.best_estimator_.n_estimators
        best_model["max_depth"] \
            = grid_model.best_estimator_.max_depth
        best_model["train_accuracy"] = train_accuracy
        best_model["test_accuracy"] = test_accuracy
        best_model["train_rmse"] = train_rmse
        best_model["test_rmse"] = test_rmse
        best_model["train_spearman_r"] = train_spearman.correlation
        best_model["test_spearman_r"] = test_spearman.correlation
        best_model["train_spearman_p"] = train_spearman.pvalue
        best_model["test_spearman_p"] = test_spearman.pvalue
        best_model["fold_id"] = cnt

        print("Model: {}".format(best_model["params"]))
        print("Train Accuracy: {}".format(best_model["train_accuracy"]))
        print("Test Accuracy: {}".format(best_model["test_accuracy"]))

        performance_values.append(best_model)
        pd.DataFrame(performance_values).to_csv(join(args["output_dir"], "results.csv"), index=False)

        cnt += 1


if __name__ == '__main__':
    """this script takes in the database connection as an input and creates the lecture wide engagement related values.

        eg: command to run this script:

        python scratch/generate_dataset/generate_train_test_split.py --input-filepath /cs/research/user/x5gon/input.json
        --output-filepath /cs/research/user/x5gon/output.json

    """
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--training-data-filepath', type=str, required=True,
                        help="filepath where the training data is")
    parser.add_argument('--output-dir', type=str, required=True,
                        help="output file dir where the model and result statistics should be saved")
    parser.add_argument('--n-jobs', type=int, default=8,
                        help="number of parallel jobs to run when running cv hyperparameter turning")
    parser.add_argument('--k-folds', type=int, default=5,
                        help="Number of folds to be used in k-fold cross validation")
    parser.add_argument('--label', default='median', const='all', nargs='?', choices=['median', 'mean'],
                        help="Defines what feature set should be used for training")
    parser.add_argument('--feature-cat', type=int, default=1,
                        help="which feature category")
    parser.add_argument('--is-log', action='store_true')

    args = vars(parser.parse_args())

    main(args)