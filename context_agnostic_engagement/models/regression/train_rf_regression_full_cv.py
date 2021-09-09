from pyspark.sql import SparkSession

import pandas as pd
import numpy as np

from os.path import join
from sklearn.ensemble import RandomForestRegressor
import joblib

from sklearn.model_selection import GridSearchCV

from context_agnostic_engagement.helper_tools.evaluation_metrics import get_rmse, get_spearman_r, get_pairwise_accuracy
from context_agnostic_engagement.helper_tools.io_utils import load_lecture_dataset, get_fold_from_dataset, \
    get_label_from_dataset, get_features_from_dataset


def main(args):
    spark = (SparkSession.
             builder.
             config("spark.driver.memory", "20g").
             config("spark.executor.memory", "20g").
             config("spark.driver.maxResultSize", "20g").
             config("spark.rpc.lookupTimeout", "300s").
             config("spark.rpc.lookupTimeout", "300s").
             config("spark.master", "local[{}]".format(args["k_folds"]))).getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    performance_values = []

    folds = args["k_folds"]
    jobs = args["n_jobs"]
    col_cat = args['feature_cat']

    lectures = load_lecture_dataset(args["training_data_filepath"], col_version=col_cat)

    label = get_label_from_dataset(args["label"])

    columns, lectures = get_features_from_dataset(col_cat, lectures)
    print(columns)
    cnt = 1
    # make pairwise observations
    for i in range(folds):
        fold_train_df, fold_test_df = get_fold_from_dataset(lectures, cnt)

        X_train, Y_train = fold_train_df[columns], np.array(fold_train_df[label])
        X_test, Y_test = fold_test_df[columns], np.array(fold_test_df[label])

        if args["is_log"]:
            # log transformation of the data
            Y_train = np.log(Y_train)
            Y_test = np.log(Y_test)

        params = {'n_estimators': [100, 500, 750, 1000, 2000, 5000],
                  'max_depth': [3, 5, 10, 25]}

        print("\n\n\n ========== dataset {} created !!! ===========\n\n".format(cnt))
        print("no. of features: {}".format(X_train.shape[1]))
        print("training data size: {}".format(len(X_train)))
        print("testing data size: {}\n\n".format(len(X_test)))
        
        grid_model = GridSearchCV(RandomForestRegressor(), params, cv=folds, n_jobs=jobs, refit=True)
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

        train_rmse, test_rmse = get_rmse(Y_train, Y_test, train_pred, test_pred)

        train_spearman, test_spearman = get_spearman_r(Y_train, Y_test, train_pred, test_pred)
     
        best_model = {}
        best_model["params"] = "{}_{}".format(grid_model.best_estimator_.n_estimators,
                                              grid_model.best_estimator_.max_depth)
        best_model["n_estimators"] = grid_model.best_estimator_.n_estimators
        best_model["max_depth"] \
            = grid_model.best_estimator_.max_depth

        best_model["train_rmse"] = train_rmse
        best_model["test_rmse"] = test_rmse
        best_model["train_spearman_r"] = train_spearman.correlation
        best_model["test_spearman_r"] = test_spearman.correlation
        best_model["train_spearman_p"] = train_spearman.pvalue
        best_model["test_spearman_p"] = test_spearman.pvalue
        best_model["fold_id"] = cnt

        print("Model: {}".format(best_model["params"]))

        performance_values.append(best_model)
        pd.DataFrame(performance_values).to_csv(join(args["output_dir"], "results.csv"), index=False)

        cnt += 1


if __name__ == '__main__':
    """this script takes in the relevant parameters to train a context-agnostic engagement prediction model using a 
    Random Forests Regressor (RF). The script outputs a "results.csv" with the evaluation metrics and k model 
    files in joblib pickle format to the output directory.

    eg: command to run this script:

        python context_agnostic_engagement/models/regression/train_rf_regression_full_cv.py 
        --training-data-filepath /path/to/12k/VLEngagement_dataset.csv --output-dir path/to/output/directory --n-jobs 8 
        --is-log --feature-cat 1 --k-folds 5 --label median

    """
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--training-data-filepath', type=str, required=True,
                        help="filepath where the training data is. Should be a CSV in the right format")
    parser.add_argument('--output-dir', type=str, required=True,
                        help="output file dir where the models and the results are saved")
    parser.add_argument('--n-jobs', type=int, default=8,
                        help="number of parallel jobs to run")
    parser.add_argument('--k-folds', type=int, default=5,
                        help="Number of folds to be used in k-fold cross validation")
    parser.add_argument('--label', default='median', const='all', nargs='?', choices=['median', 'mean'],
                        help="Defines what label should be used for training")
    parser.add_argument('--feature-cat', type=int, default=1,
                        help="defines what label set should be used for training")
    parser.add_argument('--is-log', action='store_true', help="Defines if the label should be log transformed.")

    args = vars(parser.parse_args())

    main(args)
