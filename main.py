#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QFont
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QCompleter, QLineEdit, QMainWindow, QMessageBox
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from Maincgchart import Ui_MainWindow
from addacft import Ui_Dialog
import math

def lerp(x: float, v: tuple) -> float:
    return (1.0 - x)*v[0] + x*v[1]


class AddAcftWindow(QtWidgets.QDialog):
    def __init__(self, db, model):
        super(AddAcftWindow, self).__init__()
        self.acft = Ui_Dialog()
        self.acft.setupUi(self)
        self.acft.buttonBox.accepted.connect(self.newacft)
        self.db = db
        self.model = model

    def setDatabase(self, db):
        self.db = db

    #Добавляем новый самолет в бд
    def newacft(self):
        acftid = self.acft.RegAcftLineEdit.text()
        emptyweight = int(self.acft.EmptyWLineEdit.text())
        emptycg = float(self.acft.DefCGLineEdit.text())
        equipmentwt = int(self.acft.EqupWLineEdit.text())
        equipmentcg = float(self.acft.CGEquipLineEdit.text())
        equipedweight = emptyweight + equipmentwt
        equipedcg = emptycg + equipmentcg
        query = QSqlQuery()
        query.prepare("INSERT INTO acfts ('ACFT_ID', 'EMPTY_WEIGHT', 'EMPTY_CG', 'W_EQUIPMENT', 'CG_EQUIPMENT', 'EQUIPED_WEIGHT', 'EQUIPED_CG') VALUES (:acftid, :emptyweight, :emptycg, :equipmentwt, :equipmentcg, :equipedweight, :equipedcg)")
        query.bindValue(":acftid", acftid)
        query.bindValue(":emptyweight", emptyweight)
        query.bindValue(":emptycg", emptycg)
        query.bindValue(":equipmentwt", equipmentwt)
        query.bindValue(":equipmentcg", equipmentcg)
        query.bindValue(":equipedweight", equipedweight)
        query.bindValue(":equipedcg", equipedcg)
        if not query.exec_():
            QtWidgets.QMessageBox.warning(None, "Database Error", query.lastError().text())
            return
        self.db.commit()
        self.model.setQuery("SELECT ACFT_ID FROM acfts")

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.steps = [0] * 13
        self.step_labels = [self.ui.Pl1label, self.ui.Pl2label, self.ui.Pl3label, self.ui.Pl4label, self.ui.Pl5label,
                    self.ui.Pl6label, self.ui.Pl7label, self.ui.Pl8label, self.ui.Pl9label, self.ui.Pl10label,
                    self.ui.Pl11label, self.ui.Pl12label, self.ui.Pl13label]

        for i in range(1, 14):
            del_button = getattr(self.ui, f"Del{i}pushButton")
            add_button = getattr(self.ui, f"Add{i}pushButton")
            label = self.step_labels[i-1]
            del_button.clicked.connect(self.get_subtract_step_method(i))
            add_button.clicked.connect(self.get_add_step_method(i))

        # инициировать рассчет масс и центровок
        self.ui.WeightCalcPB.clicked.connect(self.calculate)

        # вывод на принтер
        self.ui.PrintPushButton.clicked.connect(self.print_chart)

        # Устанавливаем соединение с базой данных
        self.set_database_connection()

        # устанавливаем модель в combobox
        self.update_model()

    def set_database_connection(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("data.db")
        if not self.db.open():
            print('Ошибка подключения к базе данных')

    def update_model(self):
        # создаем запрос на выборку данных из таблицы
        self.query = QSqlQuery()
        self.query.exec("SELECT ACFT_ID FROM acfts")
        # создаем модель для хранения результата запроса
        self.model = QSqlQueryModel()
        self.model.setQuery(self.query)
        self.ui.AcftIDComboBox.setModel(self.model)

        # Вызов далога добавления нового ВС
        self.ui.AddAcftIDPushButton.clicked.connect(self.addacftdialog)

        crew = ['3+1', '4+1', '5+1', '3+2', '4+2', '5+2']
        crewCBox = self.ui.CrewComboBox
        crewCBox.addItems(crew)



    def addacftdialog(self):
        self.AddAcftWindow = AddAcftWindow(self.db, self.model)
        self.AddAcftWindow.show()

    #рассчет масс и центровок
    def calculate(self):
            # Retrieve EQUIPED_WEIGHT and EQUIPED_CG values from database
        def get_acft_value(acft_id, value_name):
            query = QSqlQuery()
            query.prepare("SELECT {} FROM acfts WHERE ACFT_ID = :acft_id".format(value_name))
            query.bindValue(":acft_id", acft_id)
            if not query.exec_() or not query.first():
                raise ValueError("Could not retrieve {} for ACFT_ID {}".format(value_name, acft_id))
            return query.value(0)
    #получаем массу пустого ВС
        acft_id = self.ui.AcftIDComboBox.currentText()
        emptyweight = 0
        creweit = 0
        zfw = 0
        self.alw = 0
        self.pld = 0
        QTO = 0
        Qtrip = 0

        self.emptyweight = get_acft_value(acft_id, "EQUIPED_WEIGHT")
        self.EMPTY_CG = get_acft_value(acft_id, "EMPTY_CG")
        self.CG_FACTOR = get_acft_value(acft_id, "CG_EQUIPMENT")
        self.CG_EQUIPED = get_acft_value(acft_id, "EQUIPED_CG")
        self.W_EQUIPMENT = get_acft_value(acft_id, "W_EQUIPMENT")


    #считаем вес экипажа
        crewcbox_value = self.ui.CrewComboBox.currentText()
        crew_weights = {'3+1': 320, '4+1': 400, '5+1': 480, '3+2': 400, '4+2': 480, '5+2': 560}
        self.creweight = crew_weights.get(crewcbox_value, 0)

        try:
            #коммерческая загрузка
            self.pld = int(self.ui.CargoLineEdit.text())
            #топливо на взлете
            QTO = int(self.ui.TOFuelLineEdit.text())
            #расход топлива
            Qtrip = int(self.ui.TripFuelLineEdit.text())
        except ValueError:
            QMessageBox.critical(self, "Внимание", "Введены не все значения!")

        #zero fuel weight
        zfw = self.creweight + self.emptyweight
        #cвободная загрузка
        self.alw = 25000 - zfw
        #взлетная масса
        self.tow = zfw + self.pld + QTO
        if self.tow > 25000:
            QMessageBox.critical(self, "Ошибка", "Взлетная масса превышает допустимый лимит (25000 кг)")
            return
        #посадочная масса
        self.ldgw = self.tow - Qtrip

    #вычисляем положение центровки и массы пустого ВС для рисования

        #CGSTART_LEFT_AXIS_ANGLE = 8.28  # Угол оси 15% в градусах
        #CGSTART_LEFT_AXIS_ANGLE_RAD = math.radians(CGSTART_LEFT_AXIS_ANGLE) # Преобразование угла из градусов в радианы
        #CGSTART_LEN_FACTOR = math.tan(CGSTART_LEFT_AXIS_ANGLE_RAD) # Вычисление тангенса угла
        CGSTART_LEN_FACTOR = 0 #временное решение из-за несовершенства графика

        CGSTART_X_AXIS = 1679 # ось 27%
        CGSTART_MIN = (1183, 1220) # ось 15%
        CGSTART_MASS = (16000, 15000)
        CGSTART_Y = (557, 811) # верхняя и нижняя ось в пикселях
        CGSTART_HIGHT = CGSTART_Y[1] - CGSTART_Y[0] # высота в пикселях
        CGSTART_FACTOR = CGSTART_HIGHT / (CGSTART_MASS[0] - CGSTART_MASS[1]) # коофициент для перевода кг в пиксели
        CGSTART_KG_HIGHT = (self.emptyweight - CGSTART_MASS[1]) #высота в килограммах
        CGSTART_X_DELTA = (CGSTART_KG_HIGHT * CGSTART_FACTOR) * CGSTART_LEN_FACTOR # Удлиннение по Х на высоте массы в пикселях
        CGSART_LEN_X = CGSTART_X_AXIS - CGSTART_MIN[1] - CGSTART_X_DELTA # длинна шкалы по массе

        CGSTART_PCT_EMPTY = get_acft_value(acft_id, "EQUIPED_CG")
        CGSTART_PCT_DELTA = 27 - CGSTART_PCT_EMPTY
        CGSTART_X_PIXEL = CGSTART_X_AXIS - ((CGSART_LEN_X / 12) * CGSTART_PCT_DELTA) # позиция по Х
        self.cgstart = int(CGSTART_X_PIXEL)

        CGSTART_Y_PIXEL = CGSTART_Y[1] - (CGSTART_KG_HIGHT * CGSTART_FACTOR) # позиция по Y
        self.wstart = int(CGSTART_Y_PIXEL)

        #расчитываем кол-во делений на экипаж

        if self.creweight <= 400:
            self.GridCrew = self.cgstart - int(self.creweight * 46 / 80)
            self.cabincrew = 0
        elif self.creweight == 480:
            self.GridCrew = self.cgstart - 230
            self.cabincrew = 33
        elif self.creweight == 560:
            self.GridCrew = self.cgstart - 230
            self.cabincrew = 67

        self.draw_chart()

    def get_subtract_step_method(self, step_num):
        return lambda: self.subtract_step(step_num)

    def get_add_step_method(self, step_num):
        return lambda: self.add_step(step_num)

    def subtract_step(self, step_num):
        index = step_num - 1
        if self.steps[index] > 0:
            remainder = self.steps[index] % 100  # вычисляем остаток
            if remainder > 0:
                self.steps[index] -= remainder  # отнимаем остаток
            else:
                self.steps[index] -= 100
            self.step_labels[index].setText(str(self.steps[index]))
            self.calculate()

        #self.draw_chart()

    def add_step(self, step_num):
        index = step_num - 1
        new_step_value = self.steps[index] + 100
        remainder = new_step_value % 100  # вычисляем остаток
        if sum(self.steps) + 100 <= self.pld:
            self.steps[index] = new_step_value
            self.step_labels[index].setText(str(new_step_value))
            self.calculate()
        else:
            remainder = self.pld - sum(self.steps)
            self.steps[index] += remainder
            self.step_labels[index].setText(str(self.steps[index]))
            self.calculate()

        #self.draw_chart()

    def draw_chart(self):
        # создаём новый pixmap
        self.canvas = QPixmap("cgchart.big.png")

        # создаём QPainter для рисования на pixmap
        painter = QtGui.QPainter(self.canvas)
        painter.setPen(QPen(Qt.red, 10))
        #опускаем на линию кол-ва экипажа
        painter.drawLine(self.cgstart, self.wstart, self.cgstart, 930)
        #рисуем экипаж
        painter.drawLine(self.cgstart, 930, self.GridCrew, 930)
        painter.drawLine(self.GridCrew, 930, self.GridCrew, 1140)
        painter.drawLine(self.GridCrew, 1140, self.GridCrew - self.cabincrew, 1140)


        WELL_MASS = (25000, 15000) #пределы шкалы массы в кг
        WELL_Y = (2834, 3116) #пределы шкалы массы в px
        WELL_X_AXIS = 1796 # координаты по X вертикальной оси 30%
        WELL_X_CGMIN_TB = (836, 1206) # координаты по X оси левый край 15%
        #WELL_X_CGMAX_TB = (?, ?)
        WELL_PCT_TOP = (0.15, 0.30, 0.33)

        GEAR_CURVE_PCT100 = (4.0, 3.7, 3.35, 2.94, 2.6)
        GEAR_CURVE_MASS = (15000, 16000, 18000, 21100, 24500)

        WELL_WIDTH_TOP = WELL_X_AXIS - WELL_X_CGMIN_TB[0]
        WELL_WIDTH_BOTTOM = WELL_X_AXIS - WELL_X_CGMIN_TB[1]
        WELL_PCT_RANGE = WELL_PCT_TOP[1] - WELL_PCT_TOP[0]
        WELL_PCT_BOTTOM = (WELL_PCT_TOP[0] / WELL_WIDTH_TOP * WELL_WIDTH_BOTTOM, WELL_PCT_TOP[1])
        WELL_HEIGHT = WELL_Y[1] - WELL_Y[0]
        WELL_FACTOR = WELL_HEIGHT / (WELL_MASS[0] - WELL_MASS[1])

        y_tow = int(WELL_Y[1] - (self.tow - WELL_MASS[1]) * WELL_FACTOR)
        y_ldgw = int(WELL_Y[1] - (self.ldgw - WELL_MASS[1]) * WELL_FACTOR)
        # TOW
        painter.setPen(QPen(Qt.blue, 10))
        painter.drawLine(840, y_tow, 1990, y_tow)
        # LDGW
        painter.setPen(QPen(Qt.green, 10))
        painter.drawLine(840, y_ldgw, 1990, y_ldgw)
        # Загрузка по метрам
        painter.setPen(QPen(Qt.red, 10))
        l = self.GridCrew - self.cabincrew
        factors = [1300 / 28, 1300 / 39, 1300 / 54, 1300 / 86, 1300 / 225, -1300 / 375, -1300 / 105, -1300 / 60, -1300 / 44, -1300 / 34, -1300 / 27, -1300 / 23, -1300 / 19]
        heights = [1140, 1270, 1410, 1540, 1680, 1810, 1940, 2080, 2220, 2360, 2480, 2620, 2760, 3115]
        for i in range(len(factors)):
            l -= (self.steps[i] / 100) * factors[i]
            self.last_x = l #получаем значение X для рассчета взлетной и посаддочной центровок
            painter.drawLine(int(l), heights[i], int(l), heights[i+1])

        font = QFont()
        font.setPointSize(30)
        painter.setFont(font)
        painter.setPen(QPen(Qt.black, 10))

        FLIGHTNO = self.ui.FlightNoLineEdit.text()
        EMPTY_CG = str(self.EMPTY_CG)
        DEPARTURE_AP = self.ui.DepAptLineEdit.text()
        DEST_AP = self.ui.ArrAtpLineEdit.text()
        CG_FACTOR = str(self.CG_FACTOR)
        DATE = self.ui.DepartureDateTimeEdit.date()
        DATE_TEXT = DATE.toString("dd.MM.yyyy")
        TIME = self.ui.DepartureDateTimeEdit.dateTime()
        TIME_TEXT = TIME.toString("hh:mm")
        CG_EQUIPED = str(self.CG_EQUIPED)
        ACFT_ID = self.ui.AcftIDComboBox.currentText()
        EMPTYWEIGHT = str(self.emptyweight)
        W_EQUIPMENT = str(self.W_EQUIPMENT)
        EQUIPED_WEIGHT = str(self.emptyweight + self.W_EQUIPMENT)
        CREW_TOTAL = self.creweight / 80
        if CREW_TOTAL > 5:
            CREW = '5'
            CREW_EXTRA = str(int(CREW_TOTAL - 5))
        else:
            CREW = str(int(CREW_TOTAL))
            CREW_EXTRA = ''
        TO_FUEL = self.ui.TOFuelLineEdit.text()
        PL1 = self.ui.Pl1label.text()
        PL2 = self.ui.Pl2label.text()
        PL3 = self.ui.Pl3label.text()
        PL4 = self.ui.Pl4label.text()
        PL5 = self.ui.Pl5label.text()
        PL6 = self.ui.Pl6label.text()
        PL7 = self.ui.Pl7label.text()
        PL8 = self.ui.Pl8label.text()
        PL9 = self.ui.Pl9label.text()
        PL10 = self.ui.Pl10label.text()
        PL11 = self.ui.Pl11label.text()
        PL12 = self.ui.Pl12label.text()
        PL13 = self.ui.Pl13label.text()
        TOTAL_LOAD = str(self.creweight + int(TO_FUEL) + self.pld)
        TOW = str(self.tow)
                # рассчет взлетной и посадочной центровок
        px1 = (self.last_x - WELL_X_AXIS) / WELL_WIDTH_TOP
        px2 = (self.last_x - WELL_X_AXIS) / WELL_WIDTH_BOTTOM
        py1 = (y_tow - WELL_Y[0]) / WELL_HEIGHT
        py2 = (y_ldgw - WELL_Y[0]) / WELL_HEIGHT
        print("py1: % .3f py2: % .3f px1: % .3f px2: % .3f\tlast_x: %.2f" % (py1, py2, px1, px2, self.last_x))
        to_cg = lerp(py1, (px1, px2)) * WELL_PCT_RANGE + WELL_PCT_TOP[1]
        ldgw_cg = lerp(py2, (px1, px2)) * WELL_PCT_RANGE + WELL_PCT_TOP[1]
        print("\tto_cg: %.2f%% ldgw_cg: %.2f%%" % (to_cg * 100, ldgw_cg * 100))

        CG_TO = str(round(to_cg * 100, 2))
        CG_TO_INT_PART = CG_TO.split('.')[0]
        CG_TO_FRACT_PART = CG_TO.split('.')[1]
        TRIP_FUEL = self.ui.TripFuelLineEdit.text()
        LDGW = str(self.ldgw)
        CG_LDG = str(round(ldgw_cg * 100, 2))
        CG_LDG_INT_PART = CG_LDG.split('.')[0]
        CG_LDG_FRACT_PART = CG_LDG.split('.')[1]

        painter.drawText(305, 315, FLIGHTNO)
        painter.drawText(2130, 315, EMPTY_CG)
        painter.drawText(444, 366, DEPARTURE_AP)
        painter.drawText(1208, 366, DEST_AP)
        painter.drawText(2130, 366, CG_FACTOR)
        painter.drawText(224, 423, DATE_TEXT)
        painter.drawText(1000, 423, TIME_TEXT)
        painter.drawText(2130, 423, CG_EQUIPED)
        painter.drawText(347, 481, ACFT_ID)

        font.setPointSize(40)
        font.setLetterSpacing(QFont.PercentageSpacing, 220)
        painter.setFont(font)

        painter.drawText(2060, 543, EMPTYWEIGHT)
        painter.drawText(2190, 625, W_EQUIPMENT)
        painter.drawText(2060, 741, EQUIPED_WEIGHT)
        painter.drawText(2060, 920, CREW)
        painter.drawText(2115, 985, TO_FUEL)
        painter.drawText(2060, 1100, CREW_EXTRA + 'Э')
        painter.drawText(2190, 1100, PL1)
        painter.drawText(2190, 1247, PL2)
        painter.drawText(2190, 1370, PL3)
        painter.drawText(2190, 1510, PL4)
        painter.drawText(2190, 1650, PL5)
        painter.drawText(2190, 1780, PL6)
        painter.drawText(2190, 1910, PL7)
        painter.drawText(2190, 2040, PL8)
        painter.drawText(2190, 2170, PL9)
        painter.drawText(2190, 2300, PL10)
        painter.drawText(2190, 2430, PL11)
        painter.drawText(2190, 2560, PL12)
        painter.drawText(2190, 2690, PL13)
        painter.drawText(2115, 2815, TOTAL_LOAD)

        font.setLetterSpacing(QFont.PercentageSpacing, 180)
        painter.setFont(font)

        painter.drawText(370, 2900, TOW)
        painter.drawText(370, 2990, CG_TO_INT_PART + '. ' + CG_TO_FRACT_PART)
        painter.drawText(370, 3090, TRIP_FUEL)
        painter.drawText(370, 3180, LDGW)
        painter.drawText(370, 3280, CG_LDG_INT_PART + '. ' + CG_LDG_FRACT_PART)



        painter.end()
        # устанавливаем pixmap с нарисованной линией в качестве изображения для cgchartLable
        self.ui.cgchartLable.setPixmap(self.canvas)
        self.ui.cgchartLable.setScaledContents(True)
        self.ui.cgchartLable.setObjectName("self.ui.cgchartLable")



        # Выводим текстом данные
        self.ui.weight.setText("Cвободная\nзагрузка: {}\nВзлетная\nмасса: {}\nПосадочная\nмасса: {}\nВзлетная\nцентровка: {:.2f}\nПосадочная\nцентровка: {:.2f}".format(self.alw, self.tow, self.ldgw, to_cg * 100, ldgw_cg * 100))






    def print_chart(self):
        # получаем QPixmap из QLabel
        pixmap = self.ui.cgchartLable.pixmap()

        # создаём QPrinter
        printer = QPrinter(QPrinter.HighResolution)

        # устанавливаем параметры печати (например, формат бумаги)
        printer.setPageSize(QPrinter.A4)

        # Создаем диалог печати
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            pixmap = self.ui.cgchartLable.pixmap()
            # создаём QPainter для рисования на принтере
            painter = QtGui.QPainter(printer)
            painter.drawPixmap(printer.pageRect(), pixmap)
            painter.end()

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
