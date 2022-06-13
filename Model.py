import math
import pandas as pd
from matplotlib import pyplot
from ModelForCountry import ModelForCountry
from Algorithm import linearRegressionFromSklear, svrRegression, linearCustomModel

listOfFiles = ["API_NE.CON.TOTL.CD_DS2_en_csv_v2_4151882.csv",
               "API_BX.KLT.DINV.CD.WD_DS2_en_csv_v2_4150731.csv",
               "API_BN.GSR.GNFS.CD_DS2_en_csv_v2_4151352.csv",
               "API_GC.XPN.TOTL.CN_DS2_en_csv_v2_4157167.csv",
               "API_NY.GDP.MKTP.CD_DS2_en_csv_v2_4150784.csv"]  # consumption, investments, netTrade, expenditure, GDP

listOfDataNames = ["Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP"]

exchangeFile = pd.read_csv("API_PA.NUS.FCRF_DS2_en_csv_v2_4151802.csv", skiprows=4)
exchangeFile = exchangeFile.drop(columns=["Unnamed: 66", "Country Code", "Indicator Name", "Indicator Code"])
exchangeFile = exchangeFile.set_index("Country Name")


class Model:
    def __init__(self, listSources, listDataNames, exchangeCurrencyFile):
        self.__listSources = listSources
        self.__listDataNames = listDataNames
        self.__exchangeCurrencyFile = exchangeCurrencyFile
        self.__listDataSets = self.readDataSets()
        self.__listCountries = self.createCountryList()
        self.__modelCountry = None

    def readDataSets(self):
        result = list()
        for file in self.__listSources:
            result.append(pd.read_csv(file, skiprows=4).drop(columns=[
                "Unnamed: 66", "Country Code", "Indicator Name", "Indicator Code"]))

        result[0].set_index("Country Name", inplace=True)
        result[1].set_index("Country Name", inplace=True)
        result[2].set_index("Country Name", inplace=True)
        result[3].set_index("Country Name", inplace=True)
        result[4].set_index("Country Name", inplace=True)

        # changing currency of government expenditure
        for year in range(1960, 2022):
            result[3][str(year)] = result[3][str(year)] / self.__exchangeCurrencyFile[str(year)]

        return result

    def printDataSets(self):
        for data in self.__listDataSets:
            print(data)

    # przygotowuje dane dla wybranego kraju w krotce (kraj, X i Y, numberOfYears)
    def prepareDataForCountry(self, country):
        matrixX = pd.DataFrame(index=[i for i in range(1960, 2022)])
        matrixX[self.__listDataNames[0]] = self.__listDataSets[0].loc[country].values
        matrixX[self.__listDataNames[1]] = self.__listDataSets[1].loc[country].values
        matrixX[self.__listDataNames[2]] = self.__listDataSets[2].loc[country].values
        matrixX[self.__listDataNames[3]] = self.__listDataSets[3].loc[country].values
        matrixX[self.__listDataNames[4]] = self.__listDataSets[4].loc[country].values
        matrixX.dropna(axis=0, inplace=True)

        matrixY = pd.DataFrame(index=matrixX.index.values)
        matrixY[self.__listDataNames[4]] = matrixX.pop(self.__listDataNames[4])
        years = matrixX.index.values
        return matrixX, matrixY, years

    # tworzy listę krajów, które zawierają przynajmniej jeden rok z pelnymi danymi
    def createCountryList(self):
        result = []
        for i in self.__listDataSets[0].index.values:
            if len(self.prepareDataForCountry(i)[2]) > 0:
                result.append(i)
        return result

    # zwraca listę państw
    def getCountryList(self):
        return self.__listCountries

    # zwraca słownik nazw danych: nazwa w kodzie - pełna nazwa
    def getDataNames(self):
        return {self.__listDataNames[0]: "Consumption expenditure",
                self.__listDataNames[1]: "Foreign direct investment",
                self.__listDataNames[2]: "Net trade in goods and services (export - import)",
                self.__listDataNames[3]: "Government expenditure",
                self.__listDataNames[4]: "Gross Domestic Product"}

    def getDataDescription(self):
        return {self.__listDataNames[0]: "Final consumption expenditure (formerly total consumption) is the sum of "
                                         "household final consumption expenditure (private consumption) and general "
                                         "government final consumption expenditure (general government consumption). "
                                         "Data are in current U.S. dollars.",
                self.__listDataNames[1]: "Foreign direct investment refers to direct investment equity flows in the "
                                         "reporting economy. It is the sum of equity capital, reinvestment of "
                                         "earnings, and other capital. ",
                self.__listDataNames[2]: "Net trade in goods and services is derived by offsetting imports of goods "
                                         "and services against exports of goods and services. Exports and imports of "
                                         "goods and services comprise all transactions involving a change of "
                                         "ownership of goods and services between residents of one country and the "
                                         "rest of the world.",
                self.__listDataNames[3]: "Expense is cash payments for operating activities of the government in "
                                         "providing goods and services. It includes compensation of employees (such "
                                         "as wages and salaries), interest and subsidies, grants, social benefits, "
                                         "and other expenses such as rent and dividends.",
                self.__listDataNames[4]: "GDP at purchaser's prices is the sum of gross value added by all resident "
                                         "producers in the economy plus any product taxes and minus any subsidies not "
                                         "included in the value of the products. It is calculated without making "
                                         "deductions for depreciation of fabricated assets or for depletion and "
                                         "degradation of natural resources."}

    # zwraca słownik algorytmów: skrócona nazwa - pełna nazwa
    def getAlgorithms(self):
        return {"SVR": "Support vector regression", "LCM": "Linear custom model", "LSM": "Linear Sklearn model"}

    def getAlgorithmsDescription(self):
        return {"SVR": "Support Vector Regression (SVR) is a regression function that is generalized by Support "
                       "Vector Machines - a machine learning model used for data classification on continuous data.",
                "LCM": "Linear custom model is a linear regression function based on a custom linear model and "
                       "curve_fit optimalization from sklearn module.",
                "LSM": "Linear Sklearn model is a linear regression funciton based on a linear model from sklearn "
                       "modele"}

    # tworzy model dla kraju, dopiero po jego zrobieniu, można wyświetlać dla niego wykres i dane
    def createCountryModel(self, country):
        if country not in self.__listCountries:
            raise Exception("Your Country is not in data! |", country, "|")
        self.__modelCountry = ModelForCountry(country, *self.prepareDataForCountry(country))

    # przewiduje i porównuje dane dla zadanego roku (int) i algorytmu (LCM, SVR, LSM) w modelowanym kraju,
    # zwraca krotkę dataframe: z indeksem jako rokiem, realną wartością w kolumnie Real Value GDP,
    # przewidywaną wartością w kolumnie Prediction GDP
    # krotka zawiera rówież wartości błędów
    # (mean squared error, mean absolute percentage error, coefficient of determination)
    def predictGDPFromYear(self, year, algorithm):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")

        if algorithm == "LCM":
            return self.__modelCountry.predictGDPFromYear(year, linearCustomModel)
        elif algorithm == "SVR":
            return self.__modelCountry.predictGDPFromYear(year, svrRegression)
        elif algorithm == "LSM":
            return self.__modelCountry.predictGDPFromYear(year, linearRegressionFromSklear)
        else:
            raise Exception("Wrong algorithm name!")

    # przewiduje dane dla zadanych wartości danych i algorytmu (LCM, SVR, LSM) w modelowanym kraju,
    # zwraca krotkę dataframe: realną wartością w kolumnie Real Value GDP,
    # przewidywaną wartością w kolumnie Prediction GDP
    def predictGDPFromData(self, consumption, investment, netTrade, govExpenditure, algorithm):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")

        if algorithm == "LCM":
            return self.__modelCountry.predictGDPFromData(consumption, investment, netTrade, govExpenditure,
                                                          linearCustomModel)
        elif algorithm == "SVR":
            return self.__modelCountry.predictGDPFromData(consumption, investment, netTrade, govExpenditure,
                                                          svrRegression)
        elif algorithm == "LSM":
            return self.__modelCountry.predictGDPFromData(consumption, investment, netTrade, govExpenditure,
                                                          linearRegressionFromSklear)
        else:
            raise Exception("Wrong algorithm name!")

    # przewiduje i porównuje dane dla zadanego przedziału treningowego (wartość od 0 do 1)
    # i algorytmu (LCM, SVR, LSM) w modelowanym kraju,
    # zwraca krotkę dataframe: z indeksem jako rokiem, realną wartością w kolumnie Real Value GDP,
    # przewidywaną wartością w kolumnie Prediction GDP
    # krotka zawiera rówież wartości błędów
    # (mean squared error, mean absolute percentage error, coefficient of determination)
    def predictGDPFromTrainSize(self, trainSize, algorithm):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")

        if algorithm == "LCM":
            return self.__modelCountry.predictGDPFromTrainSize(trainSize, linearCustomModel)
        elif algorithm == "SVR":
            return self.__modelCountry.predictGDPFromTrainSize(trainSize, svrRegression)
        elif algorithm == "LSM":
            return self.__modelCountry.predictGDPFromTrainSize(trainSize, linearRegressionFromSklear)
        else:
            raise Exception("Wrong algorithm name!")

    # pokazuje wykres PKB w czasie dla podanego kraju
    def showGDPGraph(self, country):
        if country not in self.__listCountries:
            raise Exception("Country is not in data!")

        data = pd.DataFrame(index=[i for i in range(1960, 2022)])
        data["GDP"] = self.__listDataSets[4].loc[country].values
        data.dropna(axis=0, inplace=True)
        data["Year"] = data.index.values
        pyplot.plot(data["Year"].values, data["GDP"].values, label="Real Value GDP [$]")
        pyplot.legend(loc="upper left")
        pyplot.title("GDP for " + country)
        pyplot.xlabel("Years from " + str(data["Year"].values[0]) + " to " + str(data["Year"].values[-1]))
        pyplot.ylabel("GDP value in e^" + str(math.floor(math.log(data["GDP"].values[-1], 10))) + "$")
        pyplot.show()

    # pokazuje wykres PKB i jego przewidywania dla istniejących danych modelowanego kraju
    # przyjmuje liste algorytmów (LCM, SVR, LSM), które mają być na wykresie oraz trainSize (od 0 do 1)
    def showPredictionGraph(self, algorithmList, trainSize):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")

        global data
        first = True
        columnNames = []

        for algorithmName in algorithmList:
            columnName = "Prediction " + algorithmName
            columnNames.append(columnName)
            if first:
                first = False
                data, _, _, _ = self.predictGDPFromTrainSize(trainSize, algorithmName)
                data.rename(columns={"Prediction GDP": columnName}, inplace=True)
            else:
                newData, _, _, _ = self.predictGDPFromTrainSize(trainSize, algorithmName)
                data[columnName] = newData["Prediction GDP"].values
        data["Year"] = data.index.values

        pyplot.plot(data["Year"].values, data["Real Value GDP"].values, label="Real Value GDP [$]")
        for columnName in columnNames:
            pyplot.plot(data["Year"].values, data[columnName].values, label=columnName + " [$]")
        pyplot.legend(loc="upper left")
        pyplot.title("GDP predictions for " + model.__modelCountry.getCountry())
        pyplot.xlabel("Years from " + str(data["Year"].values[0]) + " to " + str(data["Year"].values[-1]))
        pyplot.ylabel("GDP value in e^" + str(math.floor(math.log(data["Real Value GDP"].values[-1], 10))) + "$")
        pyplot.show()

    def showPredictionGraphWithDataX(self, trainSize, dataName):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")

        data, _, _, _ = self.predictGDPFromTrainSize(trainSize, "LCM")
        lsmData, _, _, _ = self.predictGDPFromTrainSize(trainSize, "LSM")
        svrData, _, _, _ = self.predictGDPFromTrainSize(trainSize, "SVR")
        data.rename(columns={"Prediction GDP": "Prediction Linear Sklearn Model"}, inplace=True)
        data["Prediction Linear Custom Model"] = lsmData["Prediction GDP"].values
        data["Prediction Support Vector Reggresion"] = svrData["Prediction GDP"].values
        xList = []
        for year in data.index.values:
            xList.append(self.__listDataSets[listOfDataNames.index(dataName)].loc[self.__modelCountry.getCountry(), str(year)])
        xList.sort()

        pyplot.plot(xList, data["Real Value GDP"], label="Real Value GDP")
        pyplot.plot(xList, data["Prediction Linear Sklearn Model"], label="Prediction Linear Sklearn Model")
        pyplot.plot(xList, data["Prediction Linear Custom Model"], label="Prediction Linear Custom Model")
        pyplot.plot(xList, data["Prediction Support Vector Reggresion"], label="Prediction Support Vector Reggresion")

        pyplot.legend(loc="upper left")
        pyplot.title("Prediction GDP of " + self.__modelCountry.getCountry() + " with " + dataName)
        pyplot.xlabel(dataName)
        pyplot.xticks(rotation='vertical')
        pyplot.ylabel("Value of GDP")
        pyplot.show()

    # przyjmuje kraj który musi być z listy oraz rok (string)
    # zwraca krotkę z wartościami: ("Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP")
    def showDataFromYear(self, country, year):
        if country not in self.__listCountries or not year.isnumeric() or int(year) < 1960 or int(year) > 2021:
            raise Exception(str("Wrong input to show data! |" + country + "|" + year + "|"))

        return self.__listDataSets[0].loc[country, year], self.__listDataSets[1].loc[country, year], \
               self.__listDataSets[2].loc[country, year], self.__listDataSets[3].loc[country, year], \
               self.__listDataSets[4].loc[country, year]

    # pokazuje wartości w poszczególnych krajach dla zadanej danej:
    # ["Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP"]
    # zwraca dataframe z indeksem jako rokiem danej oraz daną w kolumnie pod nazwą danej
    def showOneData(self, country, dataName):
        if country not in self.__listCountries:
            raise Exception(str("Wrong input to show data! |" + country))

        data = pd.DataFrame(index=[i for i in range(1960, 2022)])

        if dataName == "Consumption":
            data[dataName] = self.__listDataSets[0].loc[country].values
        elif dataName == "Investments":
            data[dataName] = self.__listDataSets[1].loc[country].values
        elif dataName == "Net_Trade":
            data[dataName] = self.__listDataSets[2].loc[country].values
        elif dataName == "Gov_Expenditure":
            data[dataName] = self.__listDataSets[3].loc[country].values
        elif dataName == "GDP":
            data[dataName] = self.__listDataSets[4].loc[country].values
        else:
            raise Exception("Wrong data name!")

        data.dropna(axis=0, inplace=True)
        return data

    # zwraca czy kraj jest w liście wszystkich krajów
    def isInData(self, country):
        return country in self.__listCountries

    # pokazuje wszystkie dane modelowanego kraju
    def showCountryData(self):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")
        return self.__modelCountry.showData()

    # zwraca modelowany kraj
    def getModel(self):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")
        return self.__modelCountry

    # zwraca krotkę z ostatnich danych w modelowanym kraju
    # ("Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP")
    def getLastModelData(self):
        if self.__modelCountry is None:
            raise Exception("No country is modeling!")
        return self.__modelCountry.getLastData()


if __name__ == '__main__':
    model = Model(listOfFiles, listOfDataNames, exchangeFile)
    model.createCountryModel("United States")
    print(model.predictGDPFromTrainSize(0.8, "LCM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromTrainSize(0.8, "LSM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromTrainSize(0.8, "SVR"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromYear(2010, "LCM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromYear(2010, "LSM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromYear(2010, "SVR"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromData(17125555000000.0, 211298000000.0, -676679000000.0, 6911981800000.0, "LCM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromData(17125555000000.0, 211298000000.0, -676679000000.0, 6911981800000.0, "LSM"))
    print("------------------------------------------------------------------------------------------")
    print(model.predictGDPFromData(17125555000000.0, 211298000000.0, -676679000000.0, 6911981800000.0, "SVR"))
    print("------------------------------------------------------------------------------------------")
    print(["Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP"])
    print(model.getLastModelData())
    model.showPredictionGraph(["LCM", "LSM", "SVR"], 0.8)
    model.showGDPGraph("United States")
    model.showPredictionGraphWithDataX(0.8, "Consumption")
    model.showPredictionGraphWithDataX(0.8, "Investments")
    model.showPredictionGraphWithDataX(0.8, "Net_Trade")
    model.showPredictionGraphWithDataX(0.8, "Gov_Expenditure")


