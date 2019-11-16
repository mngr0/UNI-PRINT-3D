# HAL file for BeagleBone + TCT paralell port cape with 5 steppers and 3D printer board
import os

from machinekit import rtapi as rt
from machinekit import hal
from machinekit import config as c

from fdm.config import velocity_extrusion as ve
from fdm.config import base
from fdm.config import storage
from fdm.config import motion
import hardware



# initialize the RTAPI command client
rt.init_RTAPI()
# loads the ini file passed by linuxcnc
c.load_ini(os.environ['INI_FILE_NAME'])

#for name, value in c.items("AXIS"):
#    print("AXIS %s is %s"%(name,value))
#    for i in range(c.find("TRAJ","AXES")):
#        sec="AXIS_%s"%i
#        if not c.has_section(sec):
#            c.add_section(sec)
#        c.set(sec,name,value)
#c.save_changes()
        # hal.Pin('ini.%s.%s'%(i,"max_velocity")).set(value)

motion.setup_motion("lineardeltakins")
hardware.init_hardware()
storage.init_storage('storage.ini')

# Gantry component for Z Axis
#base.init_gantry(axisIndex=2)

# reading functions
hardware.hardware_read()
#base.gantry_read(gantryAxis=2, thread='servo-thread')


numFans = 0 #c.find('FDM', 'NUM_FANS')
numExtruders = 1 # c.find('FDM', 'NUM_EXTRUDERS')
numLights = 0 #c.find('FDM', 'NUM_LIGHTS')
withAbp = 1 #c.find('FDM', 'ABP', False)

# Axis-of-motion Specific Configs (not the GUI)
ve.velocity_extrusion(extruders=numExtruders, thread='servo-thread')
# X [0] Axis
base.setup_stepper(section='AXIS_0', axisIndex=0, stepgenIndex=0, stepgenType="stepgen")
# Y [1] Axis
base.setup_stepper(section='AXIS_1', axisIndex=1, stepgenIndex=1, stepgenType="stepgen")
# Z [2] Axis
base.setup_stepper(section='AXIS_2', axisIndex=2, stepgenIndex=2, stepgenType="stepgen")
#              thread='servo-thread', gantry=True, gantryJoint=0)
#base.setup_stepper(section='AXIS_2', axisIndex=2, stepgenIndex=3,
#            gantry=True, gantryJoint=1)
# Extruder, velocity controlled

#base.setup_stepper(section='AXIS_3', axisIndex=3, stepgenIndex=3, stepgenType="stepgen")

base.setup_stepper(section='EXTRUDER_0', axisIndex=3, stepgenIndex=3, velocitySignal='ve-extrude-vel', stepgenType="stepgen")

# Setup Hardware
hardware.setup_hardware(thread='servo-thread')




base.setup_tclab()

# Temperature Signals
base.create_temperature_control(name='e0', section='EXTRUDER_0', thread='servo-thread',tclab_index=0)

base.create_temperature_control(name='hbp', section='HBP', thread='servo-thread',tclab_index=1)

# LEDs
#for i in range(0, numLights):
#    base.setup_light('l%i' % i, thread='servo-thread')
# HB LED
# hardware.setup_hbp_led(thread='servo-thread')

# Standard I/O - EStop, Enables, Limit Switches, Etc
# errorSignals = ['gpio-hw-error', 'pwm-hw-error', 'temp-hw-error',
                # 'watchdog-error', 'hbp-error']
errorSignals = [  ]
for i in range(0, numExtruders):
    errorSignals.append('e%i-error' % i)
base.setup_estop_loopback()#([],thread='servo-thread')#_loopback()
base.setup_tool_loopback()
# Probe
#base.setup_probe(thread='servo-thread')

# write out functions
base.setup_delta()

hardware.hardware_write()

# Storage
storage.read_storage()
print("fine")
# start haltalk server after everything is initialized
# else binding the remote components on the UI might fail
hal.loadusr('haltalk', wait=True)
