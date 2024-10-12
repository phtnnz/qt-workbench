#!/usr/bin/env python

# Copyright 2023-2024 Martin Junius
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
# Version 0.1 / 2023-11-04
#       First version of verbose module
# Version 0.2 / 2023-12-18
#       Added warning(), error() with abort
# Version 1.0 / 2024-01-06
#       Version bumped to 1.0
#
#       Usage:  from verbose import verbose, warning, error
#               verbose(print-like-args)
#               warning(print-like-args)
#               error(print-like-args)
#               .enable(flag=True)
#               .disable()
#               .set_prog(name)         global for all objects
#               .set_errno(errno)       relevant only for error()
# Version 1.0 / 2024-10-10
#       PyQt6 version of verbose module
#       New:
#               .set_widget(w)          set PyQt6 QPlainTextEdit widget for logging
#               .set_stdout(flag)       enable print() output

import sys

# The following libs must be installed with pip

# PyQt6
from PyQt6.QtWidgets import QPlainTextEdit



global VERSION, AUTHOR, NAME
VERSION = "1.0 / 2024-10-10"
AUTHOR  = "Martin Junius"
NAME    = "qverbose"



class Verbose:
    progname = None             # global program name
    stdout = False              # Use print()
    pyqt = None                 # QPlainTextEdit widget to show messages


    def __init__(self, flag : bool=False, prefix : str=None, abort : bool=False):
        self.enabled = flag
        self.prefix = prefix
        self.abort = abort
        self.errno = 1          # exit(1) for generic errors

    def __call__(self, *args):
        if not self.enabled:
            return
        txt_list = []
        if Verbose.progname:
            txt_list.append(Verbose.progname + ":")
        if self.prefix:
            txt_list.append(self.prefix + ":")
        txt_list.extend(args)
        txt = " ".join(txt_list)

        if Verbose.stdout:
            print(txt)
        if Verbose.pyqt:
            Verbose.pyqt.appendPlainText(txt)

        if self.abort:
            self._exit()

    def enable(self, flag : bool=True):
        self.enabled = flag

    def disable(self):
        self.enabled = False

    def set_prog(self, name: str):
        Verbose.progname = name

    def set_errno(self, errno: int):
        self.errno = errno

    def set_widget(self, widget: QPlainTextEdit):
        Verbose.pyqt = widget

    def set_stdout(self, flag: bool=True):
        Verbose.stdout = flag

    def _exit(self):
        if Verbose.progname:
            print(Verbose.progname + ": ", end="")
        print(f"exiting ({self.errno})")
        sys.exit(self.errno)


verbose = Verbose()
warning = Verbose(True, "WARNING")
error   = Verbose(True, "ERROR", True)
