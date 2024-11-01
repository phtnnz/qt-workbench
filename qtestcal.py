#!/usr/bin/env python

# Copyright 2024 Martin Junius
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License 
# for more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>. 

# ChangeLog
# Version 0.0 / 2024-10-12
#       Test calendar widgets

import sys

# The following libs must be installed with pip
from icecream import ic
ic.disable()

# Local modules
from qverbose import verbose, warning, error

# PyQt6 must be installed with pip
from PyQt6.QtCore    import QProcess, QDate, Qt, pyqtSlot, QTimer
from PyQt6.QtGui     import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QCalendarWidget,
    QDateEdit,
    QLabel,
    QCheckBox,
    QComboBox
)


VERSION = "0.0 / 2024-10-12"
AUTHOR  = "Martin Junius"
NAME    = "qtestcal"



# Extend QDateEdit with "Today" button
class DateEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent, calendarPopup=True)
        self._today_button = QPushButton(self.tr("Today"))
        self._today_button.clicked.connect(self._update_today)
        self.calendarWidget().layout().addWidget(self._today_button)

    @pyqtSlot()
    def _update_today(self):
        self._today_button.clearFocus()
        today = QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)
        self.calendarWidget().setFocus()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Size
        self.setMinimumSize(500, 200) 
        self.setWindowTitle(f"{NAME} {VERSION}")

        # Central widget
        layout = QVBoxLayout()
        
        # Calendar to select date, default currentDate()
        self.date = QCalendarWidget()
        self.date.setGridVisible(True)
        self.date.clicked[QDate].connect(self.show_date)
        self.date.setSelectedDate(QDate.currentDate())
        self.date.setFocus()
        layout.addWidget(self.date)

        # Subdirectory and target selector
        grid = QGridLayout()
        enable_subdir = QCheckBox()
        enable_subdir.stateChanged.connect(self.enable_subdir_changed)
        grid.addWidget(enable_subdir, 0, 0)
        grid.addWidget(QLabel("Subdirectory"), 0, 1)
        self.subdir = QComboBox()
        self.subdir.addItems(["_asteroids", "_vars"])
        self.subdir.setEditable(True)
        self.subdir.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.subdir.currentIndexChanged.connect(self.subdir_changed)
        self.subdir.setEnabled(False)
        grid.addWidget(self.subdir, 0, 2)
        self.date_label = QLabel(f"_{self.date.selectedDate().toString(Qt.DateFormat.ISODate)}")
        self.date_label.setEnabled(False)
        grid.addWidget(self.date_label, 0, 3)
        enable_target = QCheckBox()
        enable_target.stateChanged.connect(self.enable_target_changed)
        grid.addWidget(enable_target, 1, 0)
        grid.addWidget(QLabel("Target(s)"), 1, 1)
        self.target = QLineEdit()
        self.target.setEnabled(False)
        grid.addWidget(self.target, 1, 2)
        grid.addWidget(QLabel("Comma-separated list of targets"), 2, 2)
        layout.addLayout(grid)

        # Buttons to start the action
        run_last = QPushButton("Zip all data for selected date")
        run_last.clicked.connect(self.click_run_last)
        layout.addWidget(run_last)
        run_ready = QPushButton("Wait for and zip ready data")
        run_ready.clicked.connect(self.click_run_ready)
        layout.addWidget(run_ready)

        # TextEdit for log output, used also by verbose()
        layout.addWidget(QLabel("Log:"))
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        verbose.set_widget(self.text)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # edit = QDateEdit()
        # edit.setDate(QDate(2024, 1, 1))
        # edit.setCalendarPopup(True)
        # edit = DateEdit()
        # edit.setDate(QDate(2024, 1, 1))
        # layout.addWidget(edit)

        self.timer = QTimer()
        self.timer.setInterval(10000) # 10s
        self.timer.timeout.connect(self.run_timer)
        self.timer.start()

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # Menu bar
        menu = self.menuBar()

        menu_file = menu.addMenu("&File")

        menu_open = QAction('Open', self)
        menu_open.setShortcut('Ctrl+O')
        menu_open.triggered.connect(self.open_file)
        menu_file.addAction(menu_open)

        menu_dir = QAction('Select directory', self)
        menu_dir.triggered.connect(self.select_dir)
        menu_file.addAction(menu_dir)



        menu_quit = QAction("Quit", self)
        menu_quit.setShortcut('Ctrl+Q')
        menu_quit.triggered.connect(self.close)
        menu_file.addAction(menu_quit)

        menu_options = menu.addMenu("&Options")

        menu_verbose = QAction("Verbose", self, checkable=True, checked=verbose.enabled)
        menu_verbose.triggered.connect(self.toggle_verbose)
        menu_options.addAction(menu_verbose)
        menu_debug = QAction("Debug", self, checkable=True)
        menu_debug.triggered.connect(self.toggle_debug)
        menu_options.addAction(menu_debug)
        menu_options.addSeparator()

        settings_group = QActionGroup(menu_options)
        settings_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.Exclusive)
        a_1 = settings_group.addAction("abc")
        a_1.setCheckable(True)
        a_1.setChecked(True)
        a_2 = settings_group.addAction("def")
        a_2.setCheckable(True)
        menu_options.addActions([a_1, a_2])

        # Status bar
        self.statusBar().setEnabled(True)

        verbose("READY.")


    # Catch closeEvent
    def closeEvent(self, event: QCloseEvent):
        warning("quit?")
        if self.yes_no_dialog("Really quit?"):
            event.accept()
        else:
            event.ignore()
            self.print_status("Quit cancelled.")


    # Handler for buttons and menu items
    def show_date(self, date: QDate):
        ic(date)
        isodate = date.toString(Qt.DateFormat.ISODate)
        self.print_status(f"Date: {isodate}")
        self.date_label.setText(f"_{isodate}")

    def subdir_changed(self, i: int):
        d = self.subdir.currentText()
        verbose(f"subdir index={i} text={d}")

    def enable_subdir_changed(self, state: Qt.CheckState):
        enabled = Qt.CheckState(state) == Qt.CheckState.Checked
        verbose(f"subdir {enabled=}")
        self.subdir.setEnabled(enabled)
        self.date_label.setEnabled(enabled)

    def enable_target_changed(self, state: Qt.CheckState):
        enabled = Qt.CheckState(state) == Qt.CheckState.Checked
        verbose(f"target {enabled=}")
        self.target.setEnabled(enabled)

    def click_run_last(self):
        verbose("run_last button clicked")

    def click_run_ready(self):
        verbose("run_ready button clicked")


    def open_file(self):
        # Open a file dialog to select a text file
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '.', 'Text Files (*.txt)')
        if filename:
            verbose(f"open {filename}")

    def select_dir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Destination Directory')

        if directory:
            verbose(f"select dir {directory}")


    def toggle_verbose(self):
        option_v = self.sender().isChecked()
        self.print_status("Verbose", "enabled" if option_v else "disabled")
        verbose.enable(option_v)

    def toggle_debug(self):
        option_d = self.sender().isChecked()
        self.print_status("Debug", "enabled" if option_d else "disabled")


    # Dialogs
    def yes_no_dialog(self, question: str):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(f"{NAME}")
        dlg.setText(question)
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        # Look up the button enum entry for the result.
        button = QMessageBox.StandardButton(button)
        return button == QMessageBox.StandardButton.Yes


    # Helper methods
    def print_text(self, *args):
        self.text.appendPlainText(" ".join(args))

    def print_status(self, *args):
        self.statusBar().showMessage(" ".join(args))


    # Testing widgets
    def run_timer(self):
        ic("run_timer")
        # self.print_text("run_timer")



def main():
    verbose.set_prog(NAME)
    verbose.enable()

    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    app.exec()



if __name__ == "__main__":
    main()
