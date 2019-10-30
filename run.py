#!/usr/bin/python

import sys
import os
import subprocess
import time
from machinekit import launcher

launcher.register_exit_handler()
launcher.set_debug_level(4)
os.chdir(os.path.dirname(os.path.realpath(__file__)))

ini_file = "UNI-PRINT-3D.ini"

try:

    launcher.check_installation()
    launcher.cleanup_session()
    launcher.ensure_mklauncher()
    # launcher.load_bbio_file('paralell_cape3.bbio')
#    launcher.start_process("configserver -n MendelMax ~/Cetus")
    launcher.start_process('linuxcnc UNI-PRINT-3D.ini')
    while True:
        launcher.check_processes()
        time.sleep(1)
except subprocess.CalledProcessError:
    launcher.end_session()
    sys.exit(1)
sys.exit(0)
