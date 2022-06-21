from szablon_gui import BazoweGui
import pandas as pd
from pandastable import Table
import tkinter as tk


import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Model import Model
from TextFileReader import *

listOfFiles = ["API_NE.CON.TOTL.CD_DS2_en_csv_v2_4151882.csv",
               "API_BX.KLT.DINV.CD.WD_DS2_en_csv_v2_4150731.csv",
               "API_BN.GSR.GNFS.CD_DS2_en_csv_v2_4151352.csv",
               "API_GC.XPN.TOTL.CN_DS2_en_csv_v2_4157167.csv",
               "API_NY.GDP.MKTP.CD_DS2_en_csv_v2_4150784.csv"]  # consumption, investments, netTrade, expenditure, GDP

listOfDataNames = ["Consumption", "Investments", "Net_Trade", "Gov_Expenditure", "GDP"]

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "API_PA.NUS.FCRF_DS2_en_csv_v2_4151802.csv")
exchangeFile = pd.read_csv(filename, skiprows=4)
exchangeFile = exchangeFile.drop(columns=["Unnamed: 66", "Country Code", "Indicator Name", "Indicator Code"])
exchangeFile = exchangeFile.set_index("Country Name")


class guiForModel(BazoweGui):

    def __init__(self, master=None):
        super().__init__(master)
        self.model = Model(listOfFiles, listOfDataNames, exchangeFile)

        self.chosen_country = ''
        self.bg_color = 'white'

        self.create_start_menu()

    # tworzenie menu startowego
    def create_start_menu(self):
        self.robocze['bg'] = self.bg_color

        try:
            self.shown_frame.destroy()
        except:
            pass
        self.shown_frame = Frame(self.robocze, width=2000, height=400)
        frame = self.shown_frame
        Label(frame, text='Aplikacja przewidywania PKB', height=4, pady=2, font=('arial', 40)).pack(fill=BOTH)
        Label(frame, text='Wybierz tryb:', pady=2, font=('arial', 20)).pack(fill=BOTH)

        Button(frame, text='Modelowanie przewidywania', font=('arial', 20), command=self.tryb_model, width=50, height=3).pack(fill=BOTH)
        Button(frame, text='Wyświetlanie danych', font=('arial', 20), command=self.tryb_dane, width=50, height=3).pack(fill=BOTH)
        Button(frame, text='Instrukcje', font=('arial', 20), command=self.tryb_tlumacz, width=50, height=3).pack(fill=BOTH)

        frame.pack(fill=BOTH, expand=True)

    # Tworzenie modelu dla danego kraju, po przejściu dalej można wybrać kilka opcji:
    def create_model_selector(self):
        try:
            self.shown_frame.destroy()
        except:
            pass
        self.robocze["bg"] = self.bg_color

        self.shown_frame = Frame(self.robocze, width=2000, height=400)
        frame = self.shown_frame
        Label(frame, text=("Podaj kraj do modelowania przewidywania"), font=('arial', 20)).pack(fill=BOTH)
        Label(frame, text='Podaj kraj:').pack()
        self.text_box = tk.Text(frame, width=50, height=3)
        self.text_box.pack()

        def chosen_country_button_func():
            text_from_textBox = self.text_box.get("1.0", "end-1c")
            try:
                self.model.createCountryModel(text_from_textBox)
                self.statusbar.config(text=("Utworzono model dla: " + text_from_textBox))
                self.chosen_country = text_from_textBox
                self.create_model_menu()
            except:
                self.statusbar.config(text=("Nie znaleziono kraju, możliwe że chodziło Ci o: "
                                            + str(self.possibleCountry(text_from_textBox))))  # levanstein

        self.choose_country_button = Button(frame, text='Stwórz model', command=chosen_country_button_func, width=50,
                                            height=3)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        count = 1
        mylist = Listbox(frame, yscrollcommand=scrollbar.set)
        for country in self.model.getCountryList():
            mylist.insert(END, str(count) + ": " + str(country))
            count += 1

        def selected_item(evt):
            for i in mylist.curselection():
                w = evt.widget
                index = int(w.curselection()[0])

                self.text_box.delete(1.0, "end")
                text_to_put = mylist.get(index)
                text_to_put = text_to_put[text_to_put.find(':') + 2:]
                self.text_box.insert(1.0, text_to_put)

        mylist.bind('<<ListboxSelect>>', selected_item)
        mylist.pack(fill=BOTH)
        self.choose_country_button.pack(fill=BOTH)
        scrollbar.config(command=mylist.yview)

        frame.pack(fill=BOTH, expand=True)
        pass

    # Pokazanie przewidywania dla danego roku i porównanie go do danych z tego roku, wyświetlenie przy tym informacji o błędach
    # Pokazanie przewidywania po wpisanych przez użytkownika danych, pod miejscami gdzie można wpisać dane należy wyświetlić ostatnie pełne dane w systemie
    # Pokazanie przewidywania przy określonym trainsizie, określonym algorytmem
    # Wyświetlenie wykresu przewidywanego pkb przy określonym trainsizie, gdzie w checkboxach można zaznaczyć jaki algorytm chcemy, aby był na wykresie
    def create_model_menu(self):
        try:
            self.shown_frame.destroy()
        except:
            pass

        # tworzenie lewego okna opcji, prawego okna wynikowego
        self.shown_frame = Frame(self.robocze, width=800, height=400)
        self.left_frame = Frame(self.shown_frame, width=200, height=400)
        self.right_frame = Frame(self.shown_frame, width=600, height=400, highlightbackground="red",
                                 highlightthickness=2)

        Label(self.right_frame, text='Wynik:', font=('arial', 20), width=600).pack(fill=BOTH)

        frame = self.shown_frame
        left_frame = self.left_frame
        right_frame = self.right_frame

        left_box_frame = Frame(left_frame, width=200, height=400, highlightbackground="black", highlightthickness=1)

        # tworzenie frame, który będzie opcjami tworzenia wykresu przewidywania
        frame_1 = Frame(left_box_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
        Label(frame_1, text='Twórz wykres przewidywania PKB', font=('arial', 20)).pack(fill=BOTH)

        var1 = IntVar()
        var2 = IntVar()
        var3 = IntVar()

        var21 = IntVar()
        var22 = IntVar()
        var23 = IntVar()

        var31 = IntVar()
        var32 = IntVar()
        var33 = IntVar()

        var41 = IntVar()
        var42 = IntVar()
        var43 = IntVar()

        def show_prediction_graph_button_func():
            alg_list = []
            if (var1.get() == 1):
                alg_list.append('LCM')
            if (var2.get() == 1):
                alg_list.append('LSM')
            if (var3.get() == 1):
                alg_list.append('SVR')

            if len(alg_list) == 0:
                self.statusbar['text'] = ('Nie wybrano algorytmu')
            else:
                trainsSize = w.get() / 100
                try:
                    self.model.showPredictionGraph(alg_list, w.get() / 100)
                except:
                    if trainsSize < 0.5:
                        self.statusbar.config(text='Zwiększ train size w celu dopasowania danych!')
                    else:
                        self.statusbar.config(text='Zmniejsz train size w celu dopasowania danych!')

        show_prediction_graph_button = Button(frame_1, text='Pokaż przewidywanie',
                                              command=show_prediction_graph_button_func)

        R1 = Checkbutton(frame_1, text="LCM", variable=var1, onvalue=1, offvalue=0)
        R2 = Checkbutton(frame_1, text="LSM", variable=var2, onvalue=1, offvalue=0)
        R3 = Checkbutton(frame_1, text="SVR", variable=var3, onvalue=1, offvalue=0)

        Label(frame_1, text='Algorytmy:').pack(fill=BOTH)
        R1.pack()
        R2.pack()
        R3.pack()

        w = Scale(frame_1, from_=1, to=100, orient=HORIZONTAL, label='train size in %')
        w.pack(fill=BOTH)

        show_prediction_graph_button.pack(fill=BOTH)

        frame_1.grid(column=0, row=0, sticky=N + E + W + S)

        # tworzenie framea, który będzie opcjami przewidywania po roku
        frame_2 = Frame(left_box_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
        Label(frame_2, text='Przewiduj i porównuj PKB po roku', font=('arial', 20)).pack(fill=BOTH)

        scrollbar = Scrollbar(frame_2)
        scrollbar.pack(side=RIGHT, fill=Y)
        mylist = Listbox(frame_2, yscrollcommand=scrollbar.set)
        for year in self.model.getModel().getYears():
            mylist.insert(END, str(year))

        def selected_item(evt):
            try:
                self.frame_to_show_data.destroy()
            except:
                pass

            for i in mylist.curselection():
                w = evt.widget
                index = int(w.curselection()[0])

                text_to_put = mylist.get(index)
                self.frame_to_show_data = Frame(right_frame, width=600, height=400, highlightbackground="red",
                                                highlightthickness=2)
                tempFrame = Frame(self.frame_to_show_data)

                alg = ''
                if (var21.get() == 1):
                    alg = 'LCM'
                if (var22.get() == 1):
                    alg = 'LSM'
                if (var23.get() == 1):
                    alg = 'SVR'

                if alg == '':
                    self.statusbar['text'] = ('Nie wybrano algorytmu')

                df, error1, error2, error3 = self.model.predictGDPFromYear(int(text_to_put), alg)
                error1 = "Mean squared error: " + str(error1)
                error2 = "\nMean absolute percentage error: " + str(error2)
                if error3 != error3:
                    error3 = "\nCoefficient of determination: Brak danych!"
                else:
                    error3 = "\ncoefficient of determination: " + str(error3)
                pt = Table(tempFrame, dataframe=df, showtoolbar=True, showstatusbar=True)
                Label(self.frame_to_show_data, text=("Przewiduj i porównuj PKB po roku: " + text_to_put),
                      font=('arial', 20)).pack(fill=BOTH)
                Label(self.frame_to_show_data, text=(error1 + error2 + error3)).pack(fill=BOTH)
                tempFrame.pack()
                self.frame_to_show_data.pack(fill=BOTH)
                pt.show()

        mylist.bind('<<ListboxSelect>>', selected_item)
        mylist.pack(fill=BOTH)
        scrollbar.config(command=mylist.yview)

        R21 = Checkbutton(frame_2, text="LCM", variable=var21, onvalue=1, offvalue=0)
        R22 = Checkbutton(frame_2, text="LSM", variable=var22, onvalue=1, offvalue=0)
        R23 = Checkbutton(frame_2, text="SVR", variable=var23, onvalue=1, offvalue=0)

        # make it so that checkoxes uncheck each other
        def checkbox_func1(evt):
            var22.set(0)
            R22.deselect()
            var23.set(0)
            R23.deselect()

        def checkbox_func2(evt):
            var21.set(0)
            R21.deselect()
            var23.set(0)
            R23.deselect()

        def checkbox_func3(evt):
            var21.set(0)
            R21.deselect()
            var22.set(0)
            R22.deselect()

        R21.bind('<Button-1>', checkbox_func1)
        R22.bind('<Button-1>', checkbox_func2)
        R23.bind('<Button-1>', checkbox_func3)

        Label(frame_2, text='Algorytmy:').pack(fill=BOTH)
        R21.pack()
        R22.pack()
        R23.pack()

        frame_2.grid(column=0, row=1, sticky=N + E + W + S)

        # tworzenie framea, kótry będzie opcjami przewidywania po nazwie danej
        frame_3 = Frame(left_box_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)

        Label(frame_3, text='Przewiduj PKB po danych', font=('arial', 20)).pack(fill=BOTH)
        Label(frame_3, text='Lista danych:').pack(fill=BOTH)
        Label(frame_3, text=listOfDataNames).pack(fill=BOTH)
        Label(frame_3, text='Dane z ubieglego roku:').pack(fill=BOTH)
        Label(frame_3, text=self.model.getLastModelData()).pack(fill=BOTH)

        # create five text inputs named from d1 to d5
        d1 = Entry(frame_3, width=20)
        d2 = Entry(frame_3, width=20)
        d3 = Entry(frame_3, width=20)
        d4 = Entry(frame_3, width=20)

        d1.pack()
        d2.pack()
        d3.pack()
        d4.pack()

        def show_prediction_graph_button_func():
            try:
                self.frame_to_show_data.destroy()
            except:
                pass

            alg = ''
            if (var31.get() == 1):
                alg = 'LCM'
            if (var32.get() == 1):
                alg = 'LSM'
            if (var33.get() == 1):
                alg = 'SVR'
            if alg == '':
                self.statusbar['text'] = ('Nie wybrano algorytmu')

            d1_value_s = d1.get()
            d2_value_s = d2.get()
            d3_value_s = d3.get()
            d4_value_s = d4.get()

            try:
                d1_value = float(d1_value_s)
                d2_value = float(d2_value_s)
                d3_value = float(d3_value_s)
                d4_value = float(d4_value_s)
            except:
                self.statusbar['text'] = ('Dane muszą być liczbowe!')

            if d1_value == '' or d2_value == '' or d3_value == '' or d4_value == '':
                self.statusbar['text'] = ('Nie wybrano danych')
                return

            df = self.model.predictGDPFromData(d1_value, d2_value, d3_value, d4_value, alg)
            self.frame_to_show_data = Frame(right_frame, width=600, height=400, highlightbackground="red",
                                            highlightthickness=2)
            tempFrame = Frame(self.frame_to_show_data)
            pt = Table(tempFrame, dataframe=df, showtoolbar=True, showstatusbar=True)
            Label(self.frame_to_show_data, text="Przewiduj PKB po danych: ", font=('arial', 20)).pack(fill=BOTH)
            Label(self.frame_to_show_data,
                  text=(d1_value_s + " " + d2_value_s + " " + d3_value_s + " " + d4_value_s)).pack(fill=BOTH)
            tempFrame.pack(fill=BOTH)
            self.frame_to_show_data.pack(fill=BOTH)
            pt.show()

        algorytmy = Label(frame_3, text='Algorytmy:')
        R31 = Checkbutton(frame_3, text="LCM", variable=var31, onvalue=1, offvalue=0)
        R32 = Checkbutton(frame_3, text="LSM", variable=var32, onvalue=1, offvalue=0)
        R33 = Checkbutton(frame_3, text="SVR", variable=var33, onvalue=1, offvalue=0)

        def checkbox_func7(evt):
            var32.set(0)
            R32.deselect()
            var33.set(0)
            R33.deselect()

        def checkbox_func8(evt):
            var31.set(0)
            R31.deselect()
            var33.set(0)
            R33.deselect()

        def checkbox_func9(evt):
            var31.set(0)
            R31.deselect()
            var32.set(0)
            R32.deselect()

        R31.bind('<Button-1>', checkbox_func7)
        R32.bind('<Button-1>', checkbox_func8)
        R33.bind('<Button-1>', checkbox_func9)

        algorytmy.pack(fill=BOTH)
        R33.pack()
        R32.pack()
        R31.pack()
        Button(frame_3, text='Pokaż przewidywania', command=show_prediction_graph_button_func).pack(fill=BOTH)

        frame_3.grid(column=1, row=0, sticky=N + E + W + S)

        # tworzenie framea, kótry będzie opcjami przewidywania po roku
        def create_frame_4():

            frame_4 = Frame(left_box_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_4, text='Przewiduj PKB po train size', font=('arial', 20)).pack(fill=BOTH)
            Label(frame_4, text='Algorytmy:').pack(fill=BOTH)
            R41 = Checkbutton(frame_4, text="LCM", variable=var41, onvalue=1, offvalue=0)
            R42 = Checkbutton(frame_4, text="LSM", variable=var42, onvalue=1, offvalue=0)
            R43 = Checkbutton(frame_4, text="SVR", variable=var43, onvalue=1, offvalue=0)
            R41.pack(fill=BOTH)
            R42.pack(fill=BOTH)
            R43.pack(fill=BOTH)

            def checkbox_func4(evt):
                var42.set(0)
                R42.deselect()
                var43.set(0)
                R43.deselect()

            def checkbox_func5(evt):
                var41.set(0)
                R41.deselect()
                var43.set(0)
                R43.deselect()

            def checkbox_func6(evt):
                var41.set(0)
                R41.deselect()
                var42.set(0)
                R42.deselect()

            R41.bind('<Button-1>', checkbox_func4)
            R42.bind('<Button-1>', checkbox_func5)
            R43.bind('<Button-1>', checkbox_func6)

            slider_trainSize = Scale(frame_4, from_=1, to=100, orient=HORIZONTAL, label='train size in %')
            slider_trainSize.pack(fill=BOTH)

            def predict_from_trainSize():
                trainsSize = slider_trainSize.get() / 100

                try:
                    self.frame_to_show_data.destroy()
                except:
                    pass

                self.frame_to_show_data = Frame(right_frame, width=600, height=400, highlightbackground="red",
                                                highlightthickness=2)
                frame_for_prediction = Frame(self.frame_to_show_data)

                if var41.get() == 0 and var42.get() == 0 and var42.get() == 0:
                    self.statusbar.config(text='Nie wybrano algorytmu')
                else:
                    try:
                        if var41.get() == 1:
                            df, err1, err2, err3 = self.model.predictGDPFromTrainSize(trainsSize, 'LCM')
                        elif var42.get() == 1:
                            df, err1, err2, err3 = self.model.predictGDPFromTrainSize(trainsSize, 'LSM')
                        elif var43.get() == 1:
                            df, err1, err2, err3 = self.model.predictGDPFromTrainSize(trainsSize, 'SVR')

                        df["Years"] = df.index.values
                        pt = Table(frame_for_prediction, dataframe=df, showtoolbar=True, showstatusbar=True)
                        Label(self.frame_to_show_data, text=("Przewidywane PKB po train_size=" + str(trainsSize)),
                              font=('arial', 20)).pack(fill=BOTH)
                        Label(self.frame_to_show_data, text='errors:').pack(fill=BOTH)
                        Label(self.frame_to_show_data, text=err1).pack(fill=BOTH)
                        Label(self.frame_to_show_data, text=err2).pack(fill=BOTH)
                        Label(self.frame_to_show_data, text=err3).pack(fill=BOTH)
                        frame_for_prediction.pack(fill=BOTH)
                        self.frame_to_show_data.pack(fill=BOTH)
                        pt.show()

                    except:
                        if trainsSize < 0.5:
                            self.statusbar.config(text='Zwiększ train size w celu dopasowania danych!')
                        else:
                            self.statusbar.config(text='Zmniejsz train size w celu dopasowania danych!')

            Button(frame_4, text='Pokaż przewidywanie', command=predict_from_trainSize).pack(fill=BOTH)

            frame_4.grid(column=1, row=1, sticky=N + E + W + S)
            pass

        create_frame_4()

        left_box_frame.pack(fill=BOTH)
        left_frame.pack(side=LEFT, fill=BOTH)
        right_frame.pack(side=RIGHT, fill=BOTH)
        frame.pack(expand=True)
        pass

    # Wyświetlanie danych z konkretnego roku dla danego państwa
    # Wyświetlania wskazanej danej z listy danych dla danego państwa
    # Wyświetlanie wykresu pkb dla danego państwa
    # Pokazanie listy państw
    def create_data_menu(self):
        try:
            self.shown_frame.destroy()
        except:
            pass

        self.shown_frame = Frame(self.robocze, width=800, height=400)
        self.left_frame = Frame(self.shown_frame, width=200, height=400)
        self.right_frame = Frame(self.shown_frame, width=600, height=400, highlightbackground="red",
                                 highlightthickness=2)

        frame = self.shown_frame
        left_frame = self.left_frame
        right_frame = self.right_frame

        # frame dotyczący danych z danego roku dla danego kraju
        def create_frame1():
            frame_1 = Frame(left_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_1, text='Wyświetl dane z roku', font=('arial', 20)).pack(fill=BOTH)
            Label(frame_1, text='Podaj kraj: ').pack()
            country = Text(frame_1, height=2)
            country.pack(fill=BOTH)
            Label(frame_1, text='Podaj rok: ').pack()
            year = Text(frame_1, height=2)
            year.pack(fill=BOTH)

            def show_data_from_year():
                try:
                    text_country = country.get("1.0", "end-1c")
                    text_year = year.get("1.0", "end-1c")

                    if text_country in self.model.getCountryList():
                        try:
                            try:
                                self.frame_to_show_data.destroy()
                            except:
                                pass

                            self.frame_to_show_data = Frame(right_frame, width=600, height=400,
                                                            highlightbackground="red", highlightthickness=2)
                            frame_for_data = Frame(self.frame_to_show_data)
                            data = [self.model.showDataFromYear(text_country, text_year)]
                            df = pd.DataFrame(data, columns=listOfDataNames)
                            pt = Table(frame_for_data, dataframe=df, showtoolbar=True, showstatusbar=True)
                            Label(self.frame_to_show_data, text=("Dane dla: " + text_country + " | " + text_year),
                                  font=('arial', 20)).pack(fill=BOTH)
                            frame_for_data.pack(fill=BOTH)
                            self.frame_to_show_data.pack(fill=BOTH)
                            pt.show()
                        except:
                            self.statusbar.config(text='Błędnie wprowadzona data!')
                    else:
                        self.statusbar.config(text=("Nie znaleziono kraju, możliwe że chodziło Ci o: "
                                                    + str(self.possibleCountry(text_country))))  # levanstein
                except:
                    print('wrong input')

            Button(frame_1, text='Wyświetl', command=show_data_from_year).pack(fill=BOTH)
            frame_1.pack(fill=BOTH)

        # frame dotyczący danych z danej kategorii dla danego kraju
        def create_frame2():
            frame_2 = Frame(left_frame, width=200, height=200, highlightbackground="gray", highlightthickness=2)
            Label(frame_2, text='Wyświetl dane z jednej kategorii', font=('arial', 20)).pack(fill=BOTH)
            Label(frame_2, text='Podaj kraj: ').pack()
            country = Text(frame_2, height=2)
            country.pack(fill=BOTH)
            Label(frame_2, text='Wybierz daną do pokazania:').pack()

            scrollbar = Scrollbar(frame_2)
            scrollbar.pack(side=RIGHT, fill=Y)
            mylist = Listbox(frame_2, yscrollcommand=scrollbar.set)
            for data in listOfDataNames:
                mylist.insert(END, data)

            def show_specific_data(evt):
                try:
                    text_country = country.get("1.0", "end-1c")

                    if text_country in self.model.getCountryList():
                        try:
                            self.frame_to_show_data.destroy()
                        except:
                            pass

                        for i in mylist.curselection():
                            w = evt.widget
                            index = int(w.curselection()[0])

                            text_to_put = mylist.get(index)
                            self.frame_to_show_data = Frame(right_frame, width=600, height=400,
                                                            highlightbackground="red", highlightthickness=2)
                            frame_for_data = Frame(self.frame_to_show_data)
                            df = self.model.showOneData(text_country, text_to_put)
                            df["Years"] = df.index.values
                            pt = Table(frame_for_data, dataframe=df, showtoolbar=True, showstatusbar=True)
                            Label(self.frame_to_show_data, text=("Dane dla: " + text_country + " | " + text_to_put),
                                  font=('arial', 20)).pack(fill=BOTH)
                            frame_for_data.pack(fill=BOTH, expand=True)
                            self.frame_to_show_data.pack(fill=BOTH, expand=True)
                            pt.show()
                    else:
                        self.statusbar.config(text=("Nie znaleziono kraju, możliwe że chodziło Ci o: "
                                                    + str(self.possibleCountry(text_country))))  # levanstein
                except:
                    self.statusbar.config(text='Wrong input!')

            mylist.bind('<<ListboxSelect>>', show_specific_data)
            mylist.pack(fill=X)
            scrollbar.config(command=mylist.yview)
            frame_2.pack(fill=BOTH)

        # frame dotyczący tworzenia wykresu pkb dla wybranego państwa
        def create_frame3():
            frame_3 = Frame(left_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_3, text='Wyświetl wykres PKB kraju', font=('arial', 20)).pack(fill=BOTH)
            Label(frame_3, text='Podaj kraj: ').pack()
            country = Text(frame_3, height=2)
            country.pack(fill=BOTH)

            def show_GDP_graph():
                try:
                    text_country = country.get("1.0", "end-1c")
                    if text_country in self.model.getCountryList():
                        self.model.showGDPGraph(text_country)
                    else:
                        self.statusbar.config(text=("Nie znaleziono kraju, możliwe że chodziło Ci o: "
                                                    + str(self.possibleCountry(text_country))))  # levanstein
                except:
                    self.statusbar.config(text='Wrong input!')

            Button(frame_3, text='Wyświetl wykres', command=show_GDP_graph).pack(fill=BOTH)
            frame_3.pack(fill=BOTH)

        # frame dotyczący wyświetlania listy dostępnych państw
        def create_frame4():
            frame_4 = Frame(left_frame, width=200, height=100, highlightbackground="gray", highlightthickness=2)
            tempFrame = Frame(frame_4)
            Label(frame_4, text='Lista państw w bazie danych', font=('arial', 20)).pack(fill=BOTH)
            scrollbarCountry = Scrollbar(frame_4)
            scrollbarCountry.pack(side=RIGHT, fill=Y)
            count = 1
            mycountrylist = Listbox(frame_4, yscrollcommand=scrollbarCountry.set)
            for country in self.model.getCountryList():
                mycountrylist.insert(END, str(count) + ": " + str(country))
                count += 1
            mycountrylist.pack(fill=BOTH)
            frame_4.pack(fill=BOTH)

        create_frame1()
        create_frame2()
        create_frame3()
        create_frame4()

        left_frame.pack(side=LEFT, fill=BOTH)
        right_frame.pack(side=RIGHT, fill=BOTH)
        frame.pack(expand=True)

    # Pokazanie listy danych wraz z ich opisem
    # Pokazanie listy algorytmów wraz z ich opisem
    def create_help_menu(self):
        try:
            self.shown_frame.destroy()
        except:
            pass

        self.shown_frame = Frame(self.robocze, width=800, height=400)
        self.left_frame = Frame(self.shown_frame, width=200, height=400)
        self.right_frame = Frame(self.shown_frame, width=600, height=400, highlightbackground="red",
                                 highlightthickness=2)

        frame = self.shown_frame
        left_frame = self.left_frame
        right_frame = self.right_frame

        Label(frame, text='Instrukcja', font=('arial', 20)).pack(fill=BOTH)

        # Wyświetlanie instrukcji algorytmów
        def create_frame1():
            frame_1 = Frame(left_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_1, text='Instrukcja algorytmów i terminów', font=('arial', 20)).pack(fill=BOTH, pady=10)

            def show_instruction():
                try:
                    self.frame_to_show_data.destroy()
                except:
                    pass
                self.frame_to_show_data = Frame(right_frame, width=600, height=400,
                                                highlightbackground="red", highlightthickness=2)
                Label(self.frame_to_show_data, text='Instrukcja algorytmów i terminów', font=('arial', 20)).pack(fill=BOTH)
                text = openFile(self.frame_to_show_data, 'instrukcjaAlgorytmy.txt', 'utf-8')
                text.pack()
                self.frame_to_show_data.pack(fill=BOTH)
                pass

            Button(frame_1, text='Wyświetl', command=show_instruction).pack(fill=BOTH)
            frame_1.pack(fill=BOTH, expand=True)

        # Wyświetlanie instrukcji algorytmów
        def create_frame2():
            frame_2 = Frame(left_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_2, text='Instrukcja danych i ich znaczeń', font=('arial', 20)).pack(fill=BOTH, pady=10)

            def show_instruction():
                try:
                    self.frame_to_show_data.destroy()
                except:
                    pass
                self.frame_to_show_data = Frame(right_frame, width=600, height=400,
                                                highlightbackground="red", highlightthickness=2)
                Label(self.frame_to_show_data, text='Instrukcja danych i ich znaczeń', font=('arial', 20)).pack(
                    fill=BOTH)
                text = openFile(self.frame_to_show_data, 'instrukcjaDane.txt', 'utf-8')
                text.pack()
                self.frame_to_show_data.pack(fill=BOTH)
                pass

            Button(frame_2, text='Wyświetl', command=show_instruction).pack(fill=BOTH)
            frame_2.pack(fill=BOTH, expand=True)

        # Wyświetlanie instrukcji obsługi
        def create_frame3():
            frame_3 = Frame(left_frame, width=200, height=400, highlightbackground="gray", highlightthickness=2)
            Label(frame_3, text='Instrukcja obsługi', font=('arial', 20)).pack(fill=BOTH, pady=10)

            def show_instruction():
                try:
                    self.frame_to_show_data.destroy()
                except:
                    pass
                self.frame_to_show_data = Frame(right_frame, width=600, height=400,
                                                highlightbackground="red", highlightthickness=2)
                Label(self.frame_to_show_data, text='Instrukcja obsługi', font=('arial', 20)).pack(fill=BOTH)
                text = openFile(self.frame_to_show_data, 'instrukcjaObslugi.txt', 'utf-8')
                text.pack()
                self.frame_to_show_data.pack(fill=BOTH, expand=True)
                pass

            Button(frame_3, text='Wyświetl', command=show_instruction).pack(fill=BOTH)
            frame_3.pack(fill=BOTH)

        create_frame1()
        create_frame2()
        create_frame3()

        left_frame.pack(side=LEFT, fill=BOTH)
        right_frame.pack(side=RIGHT, fill=BOTH)
        frame.pack(expand=True)

    # tworzy pasek narzędzi
    def utworz_bazowe_menu(self):
        self.menubar = Menu(self.parent)
        self.parent["menu"] = self.menubar

        plikMenu = tk.Menu(self.menubar)
        widokMenu = tk.Menu(self.menubar)
        narzedziaMenu = tk.Menu(self.menubar)

        # plik
        for label, command, shortcut_text, shortcut in (  # todo2
                ("Start", self.tryb_start, "Ctrl+1", "<Control-1>"),
                ("Modelowanie", self.tryb_model, "Ctrl+2", "<Control-2>")
        ):
            if label is None:
                plikMenu.add_separator()
            else:
                plikMenu.add_command(label=label, underline=0,
                                     command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)

        # narzedzia
        for label, command, shortcut_text, shortcut in (
                ("Instrukcja", self.tryb_tlumacz, "Ctrl+3", "<Control-3>"),
                ("Przegladanie danych", self.tryb_dane, "Ctrl+4", "<Control-4>")
        ):
            if label is None:
                narzedziaMenu.add_separator()
            else:
                narzedziaMenu.add_command(label=label, underline=0,
                                          command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        # widok
        for label, command, shortcut_text, shortcut in (
                ("Maksymalizuj", self.maksymalizuj, "Ctrl+5", "<Control-5>"),
                ("Minimalizuj", self.minimalizuj, "Ctrl+6", "<Control-6>")
        ):
            if label is None:
                widokMenu.add_separator()
            else:
                widokMenu.add_command(label=label, underline=0,
                                      command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)

        self.menubar.add_cascade(label="Plik", menu=plikMenu)
        self.menubar.add_cascade(label="Widok", menu=widokMenu)
        self.menubar.add_cascade(label="Narzedzia", menu=narzedziaMenu)

        # return super().utworz_bazowe_menu()

    def dodaj_menu_help(self):
        pass

    def utworz_pasek_narzedzi(self):
        pass

    def maksymalizuj(self):
        self.parent.state("zoomed")
        self.parent.update()

    def minimalizuj(self):
        self.parent.state("normal")
        self.parent.update()

    def tryb_start(self):
        self.create_start_menu()

    def tryb_model(self):
        self.create_model_selector()

    def tryb_dane(self):
        self.create_data_menu()

    def tryb_tlumacz(self):
        self.create_help_menu()

    @staticmethod
    def levSim(word1, word2):
        len1 = len(word1)
        len2 = len(word2)
        distances = [[0 for i in range(len2 + 1)] for j in range(len1 + 1)]

        for t1 in range(len1 + 1):
            distances[t1][0] = t1

        for t2 in range(len2 + 1):
            distances[0][t2] = t2

        for t1 in range(1, len1 + 1):
            for t2 in range(1, len2 + 1):
                if word1[t1 - 1] == word2[t2 - 1]:
                    cost = 0
                else:
                    cost = 1
                distances[t1][t2] = min(distances[t1 - 1][t2] + 1,
                                        distances[t1][t2 - 1] + 1,
                                        distances[t1 - 1][t2 - 1] + cost)
        return distances[len1][len2]

    def possibleCountry(self, text):
        result = []
        for country in self.model.getCountryList():
            if self.levSim(text, country) < 2:
                result.append(country)
        return result



if __name__ == '__main__':
    root = Tk()
    root.title("Aplikacja przewidywania PKB")
    app = guiForModel(root)
    app.mainloop()
