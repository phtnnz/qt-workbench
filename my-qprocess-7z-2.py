import re
import sys
from icecream import ic
ic.enable()

from PyQt6.QtCore import QProcess, QDate, Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCalendarWidget,
    QDateEdit
)

STATES = {
    QProcess.ProcessState.NotRunning: "Not running",
    QProcess.ProcessState.Starting: "Starting...",
    QProcess.ProcessState.Running: "Running...",
}

# progress_re = re.compile(r"Total complete: (\d+)%")
progress_re = re.compile(r"(\d{1,3})%")
filename_re = re.compile(r"(\d+) ([A-Z+]) (.+)$")


def extract_vars(output):
    """
    Extracts variables from lines, looking for lines
    containing an equals, and splitting into key=value.
    """
    data = {}
    for s in output.splitlines():
        if "=" in s:
            name, value = s.split("=")
            data[name] = value
    return data


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

        # Hold process reference.
        self.p = None

        self.setMinimumSize(500, 200) 

        layout = QVBoxLayout()

        self.text = QPlainTextEdit()
        layout.addWidget(self.text)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.progress.setValue(0)

        btn_run = QPushButton("Execute")
        btn_run.clicked.connect(self.start)

        layout.addWidget(btn_run)

        cal = QCalendarWidget()
        cal.setGridVisible(True)
        cal.clicked[QDate].connect(self.show_date)
        cal.setSelectedDate(QDate(2024, 10, 1))
        cal.setFocus()
        layout.addWidget(cal)

        # edit = QDateEdit()
        # edit.setDate(QDate(2024, 1, 1))
        # edit.setCalendarPopup(True)
        edit = DateEdit()
        edit.setDate(QDate(2024, 1, 1))
        layout.addWidget(edit)

        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.run_timer)
        # self.timer.start()

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)


        menu = self.menuBar()
        menu_file = menu.addMenu("&File")

        menu_quit = QAction("Quit", self)
        menu_quit.setShortcut('Ctrl+Q')
        menu_quit.triggered.connect(self.close)
        menu_file.addAction(menu_quit)

        self.statusBar().setEnabled(True)


    def run_timer(self):
        ic("run_timer")
        self.text.appendPlainText("run_timer")


    def show_date(self, date: QDate):
        ic(date)
        self.statusBar().showMessage(f"Date: {date.toString(Qt.DateFormat.ISODate)}")


    def start(self):
        if self.p is not None:
            return

        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.cleanup)

        ##### Run 7z.exe #####
        # The key option (switch) is "-bsp2" go get the progress indicator via stderr
        self.p.start("C:/Program Files/7-Zip/7z.exe",
                     [ "a", "-t7z", "-r", "-spf", "-bso1", "-bse2", "-bsp2", "tmp/test.7z", "testdata" ]
                    )

        self.progress.setValue(0)

    def handle_stderr(self):
        result = bytes(self.p.readAllStandardError()).decode("utf8")
        ic("stderr")
        ic(result)

        m1 = progress_re.search(result)
        ic(m1)
        if m1:
            self.progress.setValue(int(m1.group(1)))
        
        m2 = filename_re.search(result)
        ic(m2)
        if m2:
            ic(m2.groups())
            (n, op, file) = m2.groups()
            self.text.appendPlainText(f"#{int(n):03d} op={op} file={file}")

    def handle_stdout(self):
        result = bytes(self.p.readAllStandardOutput()).decode("utf8")
        ic("stdout")
        ic(result)
        if result:
            data = extract_vars(result)

        self.text.appendPlainText(str(data))

    def handle_state(self, state):
        self.statusBar().showMessage(STATES[state])

    def cleanup(self):
        self.progress.setValue(100)
        self.p = None


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
