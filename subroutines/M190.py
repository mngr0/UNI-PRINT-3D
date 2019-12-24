#!/usr/bin/python
import subprocess
import sys
import time
set=float(str(sys.argv[1]).rstrip())
subprocess.check_output(["halcmd sets hbp-temp-set %s" %set], shell=True).rstrip()
act = float(subprocess.check_output("halcmd gets hbp-temp-meas", shell=True).rstrip())
print ("bl act=%s   set= %s"%(act,set))
while(act<(set*0.9)):
	set=float(subprocess.check_output("halcmd gets hbp-temp-set", shell=True).rstrip())
	act=float(subprocess.check_output("halcmd gets hbp-temp-meas", shell=True).rstrip())
	print ("il act=%s   set= %s"%(act,set))
	time.sleep(3)
