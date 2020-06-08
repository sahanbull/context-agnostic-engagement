from sklearn import metrics as skm
from scipy.stats import spearmanr
import numpy as np

from context_agnostic_engagement.utils.io_utils import get_pairwise_version, ID_COL, DOMAIN_COL


def get_rmse(Y_train, Y_test, train_pred, test_pred):
    train_rmse = np.sqrt(skm.mean_squared_error(Y_train, train_pred))
    test_rmse = np.sqrt(skm.mean_squared_error(Y_test, test_pred))

    return train_rmse, test_rmse


def get_spearman_r(Y_train, Y_test, train_pred, test_pred):
    train_spearman = spearmanr(Y_train, train_pred)
    test_spearman = spearmanr(Y_test, test_pred)

    return train_spearman, test_spearman


def get_pairwise_accuracy(spark, label, fold_train_df, fold_test_df, train_pred, test_pred):
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

    return train_accuracy, test_accuracy
