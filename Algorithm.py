import pandas as pd
from scipy.optimize import curve_fit
from sklearn import svm
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression


def linearRegressionFromSklear(X_train, X_test, Y_train, Y_test):
    model_lin = LinearRegression()
    model_lin.fit(X_train, Y_train)
    Y_pred = model_lin.predict(X_test)

    ms_err = mean_squared_error(Y_test, Y_pred)
    map_err = mean_absolute_percentage_error(Y_test, Y_pred)
    r2sc = r2_score(Y_test, Y_pred)

    Y_test["Prediction GDP"] = Y_pred
    Y_test.rename(columns={"GDP": "Real Value GDP"}, inplace=True)
    Y_test = Y_test.sort_index()

    return Y_test, ms_err, map_err, r2sc


def svrRegression(X_train, X_test, Y_train, Y_test):
    model = svm.SVR()
    model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)

    ms_err = mean_squared_error(Y_test, Y_pred)
    map_err = mean_absolute_percentage_error(Y_test, Y_pred)
    r2sc = r2_score(Y_test, Y_pred)

    Y_test["Prediction GDP"] = Y_pred
    Y_test.rename(columns={"GDP": "Real Value GDP"}, inplace=True)
    Y_test = Y_test.sort_index()

    return Y_test, ms_err, map_err, r2sc


def linearCustomModel(X_train, X_test, Y_train, Y_test):
    X_train = pd.DataFrame(X_train, columns=["Consumption", "Investments", "Net_Trade", "Gov_Expenditure"])
    X_test = pd.DataFrame(X_test, columns=["Consumption", "Investments", "Net_Trade", "Gov_Expenditure"])
    # zmiana X_train i X_test na dataframe, żeby posiadały kolumny z nazwami atrybutów, co jest wymagane w func

    params, _ = curve_fit(func, xdata=X_train, ydata=Y_train.ravel())
    model = CustomModel(func, params)
    Y_pred = model.predict(X_test)

    ms_err = mean_squared_error(Y_test, Y_pred)
    map_err = mean_absolute_percentage_error(Y_test, Y_pred)
    r2sc = r2_score(Y_test, Y_pred)

    Y_test["Prediction GDP"] = Y_pred.values
    Y_test.rename(columns={"GDP": "Real Value GDP"}, inplace=True)
    Y_test = Y_test.sort_index()

    return Y_test, ms_err, map_err, r2sc


def func(x, a1, a2, a3, a4, b):
    return a1 * x["Consumption"] + a2 * x["Investments"] + a3 * x["Net_Trade"] + a4 * x["Gov_Expenditure"] + b


class CustomModel:
    def __init__(self, pred_fun, params):
        self.pred_fun = pred_fun
        self.params = params

    def predict(self, x):
        return self.pred_fun(x, *self.params)
