#!/usr/bin/env python

# Copyright 2024 Martin Junius
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ChangeLog
# Version 0.0 / 2024-xx-xx
#       TEXT

import sys

# The following libs must be installed with pip

# Local modules
from qverbose import verbose, warning, error

# PyQt6 must be installed with pip
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QAction, QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox
)


VERSION = "0.0 / 2024-xx-xx"
AUTHOR  = "Martin Junius"
NAME    = "qtemplate"



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Size
        self.setMinimumSize(500, 200) 
        self.setWindowTitle(f"{NAME} {VERSION}")

        # Central widget
        layout = QVBoxLayout()

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        verbose.set_widget(self.text)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        btn_run = QPushButton("Button")
        btn_run.clicked.connect(self.click_button)
        layout.addWidget(btn_run)

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
    def click_button(self):
        verbose("button clicked")


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



def main():
    verbose.set_prog(NAME)
    verbose.enable()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()



if __name__ == "__main__":
    main()
