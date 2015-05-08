#!/usr/bin/python
'''
Created on 1 Apr 2015

@author: Jamie Hall
'''
if __name__ == "__main__":
    # NOTE: This *has* to be here and in the `__name__ == "__main__"` clause
    # to run XGBoost in parallel, if XGBoost was built with OpenMP support.
    # Otherwise, you can use fork, which is the default backend for joblib,
    # and omit this.
    from multiprocessing import set_start_method
    set_start_method("forkserver")

    import pickle
    import os
    import xgboost as xgb

    import numpy as np
    from sklearn.cross_validation import KFold
    from sklearn.grid_search import GridSearchCV
    from sklearn.metrics import confusion_matrix, mean_squared_error
    from sklearn.datasets import load_iris, load_digits, load_boston

    rng = np.random.RandomState(31337)

    print("Zeros and Ones from the Digits dataset: binary classification")
    digits = load_digits(2)
    y = digits['target']
    X = digits['data']
    kf = KFold(y.shape[0], n_folds=2, shuffle=True, random_state=rng)
    for train_index, test_index in kf:
        xgb_model = xgb.XGBClassifier().fit(X[train_index],y[train_index])
        predictions = xgb_model.predict(X[test_index])
        actuals = y[test_index]
        print(confusion_matrix(actuals, predictions))

    print("Iris: multiclass classification")
    iris = load_iris()
    y = iris['target']
    X = iris['data']
    kf = KFold(y.shape[0], n_folds=2, shuffle=True, random_state=rng)
    for train_index, test_index in kf:
        xgb_model = xgb.XGBClassifier().fit(X[train_index],y[train_index])
        predictions = xgb_model.predict(X[test_index])
        actuals = y[test_index]
        print(confusion_matrix(actuals, predictions))

    print("Boston Housing: regression")
    boston = load_boston()
    y = boston['target']
    X = boston['data']
    kf = KFold(y.shape[0], n_folds=2, shuffle=True, random_state=rng)
    for train_index, test_index in kf:
        xgb_model = xgb.XGBRegressor().fit(X[train_index],y[train_index])
        predictions = xgb_model.predict(X[test_index])
        actuals = y[test_index]
        print(mean_squared_error(actuals, predictions))

    print("Parameter optimization")
    y = boston['target']
    X = boston['data']
    xgb_model = xgb.XGBRegressor()
    clf = GridSearchCV(xgb_model,
                       {'max_depth': [2,4,6],
                        'n_estimators': [50,100,200]}, verbose=1)
    clf.fit(X,y)
    print(clf.best_score_)
    print(clf.best_params_)

    # The sklearn API models are picklable
    print("Pickling sklearn API models")
    # must open in binary format to pickle
    pickle.dump(clf, open("best_boston.pkl", "wb"))
    clf2 = pickle.load(open("best_boston.pkl", "rb"))
    print(np.allclose(clf.predict(X), clf2.predict(X)))

    print("Parallel Parameter optimization")
    os.environ["OMP_NUM_THREADS"] = "1"
    y = boston['target']
    X = boston['data']
    xgb_model = xgb.XGBRegressor()
    clf = GridSearchCV(xgb_model,
                       {'max_depth': [2,4,6],
                        'n_estimators': [50,100,200]}, verbose=1,
                       n_jobs=2)
    clf.fit(X, y)
    print(clf.best_score_)
    print(clf.best_params_)
