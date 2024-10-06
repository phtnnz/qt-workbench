import re
import sys
from icecream import ic
ic.enable()

from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STATES = {
    QProcess.ProcessState.NotRunning: "Not running",
    QProcess.ProcessState.Starting: "Starting...",
    QProcess.ProcessState.Running: "Running...",
}



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

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def start(self):
        if self.p is not None:
            return

        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.cleanup)

        ##### Run rclone.exe #####

        self.p.start("C:/Tools/rclone/rclone.exe",
                     [ "copy", "tmp/test.7z", "iasdata:test-upload/tmp", "-v", "-P", "-I" ]
                    )

        self.progress.setValue(0)

    def handle_stderr(self):
        result = bytes(self.p.readAllStandardError()).decode("utf8")
        ic("stderr")
        ic(result)

        self.text.appendPlainText(result.strip())

    def handle_stdout(self):
        result = bytes(self.p.readAllStandardOutput()).decode("utf8")
        ic("stdout")
        ic(result)

        m = re.search(r"(\d{1,3})%", result)
        ic(m)
        if m:
            self.progress.setValue(int(m.group(1)))

        m = re.search(r"(.*INFO.*)", result)
        ic(m)
        if m:
            self.text.appendPlainText(m.group(1))
        
    def handle_state(self, state):
        self.statusBar().showMessage(STATES[state])

    def cleanup(self):
        self.progress.setValue(100)
        self.p = None


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
