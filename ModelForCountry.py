import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class ModelForCountry:
    def __init__(self, countryName, matrixX, matrixY, numberOfYears):
        self.__country = countryName
        self.__matrixX = matrixX
        self.__matrixY = matrixY
        self.__listOfYears = numberOfYears

    def getLastData(self):
        return *self.__matrixX.loc[self.__listOfYears[-1]].values, *self.__matrixY.loc[self.__listOfYears[-1]].values

    def getCountry(self):
        return self.__country

    def getYears(self):
        return self.__listOfYears

    def showData(self):
        return self.__country, self.__matrixX, self.__matrixY, self.__listOfYears

    def predictGDPFromTrainSize(self, trainSize, algorithm):
        X_train, X_test, Y_train, Y_test = train_test_split(self.__matrixX, self.__matrixY, test_size=trainSize,
                                                            random_state=42)

        X_train = X_train.values.reshape(-1, 4)
        X_test = X_test.values.reshape(-1, 4)

        Y_train = Y_train.values

        return algorithm(X_train, X_test, Y_train, Y_test)

    def predictGDPFromYear(self, year, algorithm):
        if year not in self.__listOfYears:
            raise Exception("Year is not in data for this country |", year, "|", self.__country, "|")

        X_train = self.__matrixX.drop(year)
        X_train = X_train.values.reshape(-1, 4)
        X_test = [self.__matrixX.loc[year]]

        Y_train = self.__matrixY.drop(year)
        Y_train = Y_train.values.reshape(-1, 1)
        Y_test = pd.DataFrame({"GDP": self.__matrixY.loc[year].values}, index=[year])

        return algorithm(X_train, X_test, Y_train, Y_test)

    def predictGDPFromData(self, consumption, investments, netTrade, govExpenditure, algorithm):
        X_test = np.array([[consumption, investments, netTrade, govExpenditure]])
        Y_test = pd.DataFrame({"GDP": [0.0]}, index=[(consumption, investments, netTrade, govExpenditure)])

        result, _, _, _ = algorithm(self.__matrixX.values, X_test, self.__matrixY.values, Y_test)
        return result
