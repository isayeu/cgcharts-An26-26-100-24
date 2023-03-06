from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(194, 249)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 210, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.RegAcftLineEdit = QtWidgets.QLineEdit(Dialog)
        self.RegAcftLineEdit.setGeometry(QtCore.QRect(10, 10, 171, 31))
        self.RegAcftLineEdit.setObjectName("RegAcftLineEdit")

        self.EmptyWLineEdit = QtWidgets.QLineEdit(Dialog)
        self.EmptyWLineEdit.setGeometry(QtCore.QRect(10, 50, 171, 31))
        self.EmptyWLineEdit.setObjectName("EmptyWLineEdit")

        self.DefCGLineEdit = QtWidgets.QLineEdit(Dialog)
        self.DefCGLineEdit.setGeometry(QtCore.QRect(10, 130, 171, 31))
        self.DefCGLineEdit.setObjectName("DefCGLineEdit")

        self.EqupWLineEdit = QtWidgets.QLineEdit(Dialog)
        self.EqupWLineEdit.setGeometry(QtCore.QRect(10, 90, 171, 31))
        self.EqupWLineEdit.setObjectName("EqupWLineEdit")

        self.CGEquipLineEdit = QtWidgets.QLineEdit(Dialog)
        self.CGEquipLineEdit.setGeometry(QtCore.QRect(10, 170, 171, 31))
        self.CGEquipLineEdit.setObjectName("CGEquipLineEdit")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        Dialog.setToolTip(_translate("Dialog", "в колограммах с десятыми через точку, например 15533.7"))
        self.RegAcftLineEdit.setToolTip(_translate("Dialog", "Бортовой Номер самолета"))
        self.RegAcftLineEdit.setPlaceholderText(_translate("Dialog", "Боротовой номер"))
        self.EmptyWLineEdit.setToolTip(_translate("Dialog", "Масса пустого самолета"))
        self.EmptyWLineEdit.setPlaceholderText(_translate("Dialog", "Масса пустого ВС"))
        self.DefCGLineEdit.setToolTip(_translate("Dialog", "Центровка пустого самолета"))
        self.DefCGLineEdit.setPlaceholderText(_translate("Dialog", "Центровка пустого ВС"))
        self.EqupWLineEdit.setToolTip(_translate("Dialog", "Масса перевозимого снаряжения"))
        self.EqupWLineEdit.setPlaceholderText(_translate("Dialog", "Масса снаряжения"))
        self.CGEquipLineEdit.setToolTip(_translate("Dialog", "Влияние перевозимого снаряжения на центровку самолета"))
        self.CGEquipLineEdit.setPlaceholderText(_translate("Dialog", "Влиян. снар. на центровку"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
