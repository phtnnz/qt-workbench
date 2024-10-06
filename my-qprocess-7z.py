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

# progress_re = re.compile(r"Total complete: (\d+)%")
progress_re = re.compile(r"(\d{1,3})%")
filename_re = re.compile(r"(\d+) ([A-Z+]) (.+)$")


def simple_percent_parser(output):
    """
    Matches lines using the progress_re regex,
    returning a single integer for the % progress.
    """
    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        return int(pc_complete)


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

        ##### Run 7z.exe #####

        # 7-Zip 24.08 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-08-11
        # Usage: 7z <command> [<switches>...] <archive_name> [<file_names>...] [@listfile]
        # <Commands>
        #   a : Add files to archive
        #   b : Benchmark
        #   d : Delete files from archive
        #   e : Extract files from archive (without using directory names)
        #   h : Calculate hash values for files
        #   i : Show information about supported formats
        #   l : List contents of archive
        #   rn : Rename files in archive
        #   t : Test integrity of archive
        #   u : Update files to archive
        #   x : eXtract files with full paths
        # <Switches>
        #   -- : Stop switches and @listfile parsing
        #   -ai[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : Include archives
        #   -ax[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : eXclude archives
        #   -ao{a|s|t|u} : set Overwrite mode
        #   -an : disable archive_name field
        #   -bb[0-3] : set output log level
        #   -bd : disable progress indicator
        #   -bs{o|e|p}{0|1|2} : set output stream for output/error/progress line
        #   -bt : show execution time statistics
        #   -i[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : Include filenames
        #   -m{Parameters} : set compression Method
        #     -mmt[N] : set number of CPU threads
        #     -mx[N] : set compression level: -mx1 (fastest) ... -mx9 (ultra)
        #   -o{Directory} : set Output directory
        #   -p{Password} : set Password
        #   -r[-|0] : Recurse subdirectories for name search
        #   -sa{a|e|s} : set Archive name mode
        #   -scc{UTF-8|WIN|DOS} : set charset for console input/output
        #   -scs{UTF-8|UTF-16LE|UTF-16BE|WIN|DOS|{id}} : set charset for list files
        #   -scrc[CRC32|CRC64|SHA256|SHA1|XXH64|*] : set hash function for x, e, h commands
        #   -sdel : delete files after compression
        #   -seml[.] : send archive by email
        #   -sfx[{name}] : Create SFX archive
        #   -si[{name}] : read data from stdin
        #   -slp : set Large Pages mode
        #   -slt : show technical information for l (List) command
        #   -snh : store hard links as links
        #   -snl : store symbolic links as links
        #   -sni : store NT security information
        #   -sns[-] : store NTFS alternate streams
        #   -so : write data to stdout
        #   -spd : disable wildcard matching for file names
        #   -spe : eliminate duplication of root folder for extract command
        #   -spf[2] : use fully qualified file paths
        #   -ssc[-] : set sensitive case mode
        #   -sse : stop archive creating, if it can't open some input file
        #   -ssp : do not change Last Access Time of source files while archiving
        #   -ssw : compress shared files
        #   -stl : set archive timestamp from the most recently modified file
        #   -stm{HexMask} : set CPU thread affinity mask (hexadecimal number)
        #   -stx{Type} : exclude archive type
        #   -t{Type} : Set type of archive
        #   -u[-][p#][q#][r#][x#][y#][z#][!newArchiveName] : Update options
        #   -v{Size}[b|k|m|g] : Create volumes
        #   -w[{path}] : assign Work directory. Empty path means a temporary directory
        #   -x[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : eXclude filenames
        #   -y : assume Yes on all queries

        # The key option (switch) is "-bsp2" go get the progress indicator via stderr
        self.p.start("C:/Program Files/7-Zip/7z.exe",
                     [ "a", "-t7z", "-r", "-spf", "-bso1", "-bse2", "-bsp2", "tmp/test.7z", "testdata" ]
                    )

        self.progress.setValue(0)

    def handle_stderr(self):
        result = bytes(self.p.readAllStandardError()).decode("utf8")
        ic("stderr")
        ic(result)

        #FIXME: doesn't work???
        # m = re.match(r'(\d{1,3})%', result)
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
