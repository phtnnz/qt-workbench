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
#       New test script, run 7z.exe

import sys
import re

# The following libs must be installed with pip
from icecream import ic
ic.disable()

# Local modules
from qverbose import verbose, warning, error

# PyQt6 must be installed with pip
from PyQt6.QtCore    import QProcess
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


VERSION = "0.0 / 2024-10-12"
AUTHOR  = "Martin Junius"
NAME    = "qrun-7z"



STATES = {
    QProcess.ProcessState.NotRunning: "Not running",
    QProcess.ProcessState.Starting: "Starting...",
    QProcess.ProcessState.Running: "Running...",
}



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hold process reference
        self.p = None

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

        btn_run = QPushButton("Execute 7z")
        btn_run.clicked.connect(self.start)
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
        if option_d:
            ic.enable()
        else:
            ic.disable()


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


    ##### Run external program using QProcess #####
    def start(self):
        if self.p is not None:
            return

        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.cleanup)

        # Run 7z.exe
        # The key option (switch) is "-bsp2" go get the progress indicator via stderr
        self.p.start("C:/Program Files/7-Zip/7z.exe",
                     [ "a", "-t7z", "-r", "-spf", "-bso1", "-bse2", "-bsp2", "tmp/test.7z", "testdata" ]
                    )
        self.progress.setValue(0)


    def handle_stderr(self):
        result = bytes(self.p.readAllStandardError()).decode("utf8")
        ic("stderr")
        ic(result)

        m = re.search(r"(\d{1,3})%", result)
        ic(m)
        if m:
            self.progress.setValue(int(m.group(1)))

        m = re.search(r"(\d+) ([A-Z+]) (.+)$", result)
        ic(m)
        if m:
            ic(m.groups())
            (n, op, file) = m.groups()
            self.print_text(f"#{int(n):03d} op={op} file={file}")


    def handle_stdout(self):
        result = bytes(self.p.readAllStandardOutput()).decode("utf8")
        ic("stdout")
        ic(result)
        for line in result.splitlines():
            line = line.strip()
            if line:
                self.print_text(line)


    def handle_state(self, state: QProcess.ProcessState):
        ic(state)
        self.statusBar().showMessage(STATES[state])


    def cleanup(self):
        self.progress.setValue(100)
        self.p = None



def main():
    verbose.set_prog(NAME)
    verbose.enable()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()



if __name__ == "__main__":
    main()
