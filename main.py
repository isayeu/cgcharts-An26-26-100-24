from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QCompleter, QLineEdit, QMainWindow, QMessageBox
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from Maincgchart import Ui_MainWindow
from addacft import Ui_Dialog


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
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO acfts ('ACFT_ID', 'EMPTY_WEIGHT', 'EMPTY_CG', 'EQUIPED_WEIGHT', 'EQUIPED_CG') VALUES (:acftid, :emptyweight, :emptycg, :equipedweight, :equipedcg)")
        query.bindValue(":acftid", acftid)
        query.bindValue(":emptyweight", emptyweight)
        query.bindValue(":emptycg", emptycg)
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
        alw = 0
        self.pld = 0
        QTO = 0
        Qtrip = 0

        emptyweight = get_acft_value(acft_id, "EQUIPED_WEIGHT")


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
        zfw = self.creweight + emptyweight
        #cвободная загрузка
        alw = 25000 - zfw
        #взлетная масса
        tow = zfw + self.pld + QTO
        if tow > 25000:
            QMessageBox.critical(self, "Ошибка", "Взлетная масса превышает допустимый лимит (25000 кг)")
            return
        #посадочная масса
        ldgw = tow - Qtrip

        self.ui.weight.setText("Cвободная\nзагрузка: {}\nВзлетная\nмасса: {}\nПосадочная\nмасса: {}".format(alw, tow, ldgw))

    #вычисляем положение массы пустого ВС для рисования
        self.wstart = int(810 - (((emptyweight - 15000) * 2.5) / 10) )

    #вычисляем положение центровки пустого ВС для рисования
        #находим коэфициент удлиннения на уклон центровки по графику
        Kcg = (emptyweight - 15000) / 1000
        DeltaXcg = int(20 * Kcg)
        emptycg = get_acft_value(acft_id, "EQUIPED_CG")
        self.cgstart = int(1170 + DeltaXcg + (((emptycg - 15) / 12) * 100) * 5.1)
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

        self.draw_chart()

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

    def add_step(self, step_num):
        index = step_num - 1
        new_step_value = self.steps[index] + 100
        remainder = new_step_value % 100  # вычисляем остаток
        print (remainder)
        if sum(self.steps) + 100 <= self.pld:
            self.steps[index] = new_step_value
            self.step_labels[index].setText(str(new_step_value))
            self.calculate()
        else:
            remainder = self.pld - sum(self.steps)
            self.steps[index] += remainder
            self.step_labels[index].setText(str(self.steps[index]))
            self.calculate()

        self.draw_chart()

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


        # Загрузка по метрам
        l = self.GridCrew - self.cabincrew
        factors = [1300 / 28, 1300 / 39, 1300 / 54, 1300 / 86, 1300 / 225, -1300 / 375, -1300 / 105, -1300 / 60, -1300 / 44, -1300 / 34, -1300 / 27, -1300 / 23, -1300 / 19]
        heights = [1140, 1270, 1410, 1540, 1680, 1810, 1940, 2080, 2220, 2360, 2480, 2620, 2760, 3100]
        for i in range(13):
            l -= (self.steps[i] / 100) * factors[i]
            painter.drawLine(int(l), heights[i], int(l), heights[i+1])

        painter.end()
        # устанавливаем pixmap с нарисованной линией в качестве изображения для метки
        self.ui.cgchartLable.setPixmap(self.canvas)
        self.ui.cgchartLable.setScaledContents(True)
        self.ui.cgchartLable.setObjectName("self.ui.cgchartLable")

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
