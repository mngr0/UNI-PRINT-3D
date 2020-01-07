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
#ve.velocity_extrusion(extruders=numExtruders, thread='servo-thread')
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

base.setup_stepper(section='AXIS_3', axisIndex=3, stepgenIndex=3, stepgenType="stepgen")

#base.setup_stepper(section='EXTRUDER_0', axisIndex=3, stepgenIndex=3, velocitySignal='ve-extrude-vel', stepgenType="stepgen")


def assign_param(name,signal,val):
  import subprocess
  subprocess.call("halcmd setp %s.%s %s"%(name,signal,str(val)), shell=True )

#sigBase='stepgen.3'
#assign_param(sigBase,"position-scale",c.find("ABP", 'SCALE'))
#assign_param(sigBase,"maxaccel",c.find("ABP", 'STEPGEN_MAXACC'))
#hal.net('ve-extrude-vel','stepgen.3.velocity-cmd')
#stepgen3en = hal.newsig('is-running',hal.HAL_BIT)
#stepgen3en.link('halui.program.is-running')
#stepgen3en.link('stepgen.3.enable')




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


"""
hal.loadusr('xhc-whb04b-6', H="-pu", wait_name="xhc-whb04b-6", wait_timeout=30)


print("loaded")

axes_list = ["x","y","z","a"]


sign = hal.newsig("pdnt-machine-is-on",hal.HAL_BIT)
hal.Pin("whb.halui.machine.is-on").link(sign)
hal.Pin("halui.machine.is-on").link(sign)

sign2 = hal.newsig("pdnt-machine-on",hal.HAL_BIT)
hal.Pin("whb.halui.machine.on").link(sign2)
hal.Pin("halui.machine.on").link(sign2)

sign3 = hal.newsig("pdnt-machine-off",hal.HAL_BIT)
hal.Pin("whb.halui.machine.off").link(sign3)
hal.Pin("halui.machine.off").link(sign3)


for index, axes in enumerate(axes_list):
    print("i am in loop")
    sig = hal.newsig("pdnt-joint-%s-select"%str(index),hal.HAL_BIT)
    hal.Pin("whb.halui.joint.%s.select"%axes).link(sig)
    hal.Pin("halui.joint.%s.select"%str(index)).link(sig)

    sig2 = hal.newsig("pdnt-joint-%s-scale"%axes,hal.HAL_FLOAT)
    hal.Pin("whb.axis.%s.jog-scale"%str(index)).link(sig2)
    hal.Pin("axis.%s.jog-scale"%str(index)).link(sig2)

    sig3 = hal.newsig("pdnt-ilowpass-joint-%s-jog-count"%axes,hal.HAL_S32)
    hal.Pin("whb.axis.%s.jog-counts"%str(index)).link(sig3)
    hal.Pin("ilowpass.jog.%s.in"%axes).link(sig3)

    sig4 = hal.newsig("pdnt-joint-%s-jog-enable"%axes,hal.HAL_BIT)
    hal.Pin("whb.axis.%s.jog-enable"%str(index)).link(sig4)
    hal.Pin("axis.%s.jog-enable"%str(index)).link(sig4)

    sig5 = hal.newsig("pdnt-joint-%s-pos-feedback"%axes,hal.HAL_FLOAT)
    hal.Pin("whb.halui.axis.%s.pos-feedback"%str(index)).link(sig5)
    hal.Pin("halui.axis.%s.pos-feedback"%str(index)).link(sig5)

    sig6 = hal.newsig("pdnt-joint-%s-jog-count"%axes,hal.HAL_S32)
    hal.Pin("ilowpass.jog.%s.out"%axes).link(sig6)
    hal.Pin("axis.%s.jog-counts"%str(index)).link(sig6)

"""

#hpg.stepgen.00.maxvel              whb.stepgen.00.maxvel

#.stepgen.00.position-scale      whb.stepgen.00.position-scale

hal.loadusr('haltalk', wait=True)
