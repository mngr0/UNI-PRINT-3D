from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

from fdm.config import base


def hardware_read():
    pass
    #hal.addf('hpg.capture-position', 'servo-thread')
    #hal.addf('bb_gpio.read', 'servo-thread')


def hardware_write():
    pass
    #hal.addf('hpg.update', 'servo-thread')
    #hal.addf('bb_gpio.write', 'servo-thread')


def init_hardware():
    watchList = []

    # load low-level drivers
    rt.loadrt('hal_parport', cfg='0x0378')
    rt.loadrt('stepgen', step_type='0,0,0,0')
    deb = rt.newinst('debounce', 'debounce.%s' % "ciao")
    # rt.loadrt('debounce')


def setup_hardware(thread):
    # Stepper
    hal.Pin('hpg.stepgen.00.steppin').set(812)  # XStep
    hal.Pin('hpg.stepgen.00.dirpin').set(811)   # XDir
    hal.Pin('hpg.stepgen.01.steppin').set(816)  # YStep
    hal.Pin('hpg.stepgen.01.dirpin').set(815)   # YDir
    hal.Pin('hpg.stepgen.02.steppin').set(922)  # AStep - ZL
    hal.Pin('hpg.stepgen.02.dirpin').set(921)   # ADir
    hal.Pin('hpg.stepgen.03.steppin').set(913)  # ZStep - ZR
    hal.Pin('hpg.stepgen.03.dirpin').set(925)   # ZDir
    hal.Pin('hpg.stepgen.04.steppin').set(911)  # BStep
    hal.Pin('hpg.stepgen.04.dirpin').set(942)   # BDir

    # link emcmot.xx.enable to stepper driver enable signals

addf stepgen.capture-position servo-thread
addf motion-command-handler servo-thread
addf motion-controller servo-thread
addf stepgen.update-freq servo-thread
addf debounce.0.funct servo-thread

# connect position commands from motion module to step generator
net Xpos-cmd axis.0.motor-pos-cmd => stepgen.0.position-cmd
net Ypos-cmd axis.1.motor-pos-cmd => stepgen.1.position-cmd
net Zpos-cmd axis.2.motor-pos-cmd => stepgen.2.position-cmd
net Apos-cmd axis.3.motor-pos-cmd => stepgen.3.position-cmd

# connect position feedback from step generators
# to motion module
net Xpos-fb stepgen.0.position-fb => axis.0.motor-pos-fb
net Ypos-fb stepgen.1.position-fb => axis.1.motor-pos-fb
net Zpos-fb stepgen.2.position-fb => axis.2.motor-pos-fb
net Apos-fb stepgen.3.position-fb => axis.3.motor-pos-fb

# connect enable signals for step generators
net Xen axis.0.amp-enable-out => stepgen.0.enable
net Yen axis.1.amp-enable-out => stepgen.1.enable
net Zen axis.2.amp-enable-out => stepgen.2.enable
net Aen axis.3.amp-enable-out => stepgen.3.enable

# connect signals to step pulse generator outputs
net Xstep <= stepgen.0.step
net Xdir  <= stepgen.0.dir
net Ystep <= stepgen.1.step
net Ydir  <= stepgen.1.dir
net Zstep <= stepgen.2.step
net Zdir  <= stepgen.2.dir
net Astep <= stepgen.3.step
net Adir  <= stepgen.3.dir

# set stepgen module scaling - get values from ini file
setp stepgen.0.position-scale [AXIS_0]SCALE
setp stepgen.1.position-scale [AXIS_1]SCALE
setp stepgen.2.position-scale [AXIS_2]SCALE
setp stepgen.3.position-scale [AXIS_3]SCALE

# set stepgen module accel limits - get values from ini file
setp stepgen.0.maxaccel [AXIS_0]STEPGEN_MAXACCEL
setp stepgen.1.maxaccel [AXIS_1]STEPGEN_MAXACCEL
setp stepgen.2.maxaccel [AXIS_2]STEPGEN_MAXACCEL
setp stepgen.3.maxaccel [AXIS_3]STEPGEN_MAXACCEL





net Xstep => parport.0.pin-03-out
net Xdir  => parport.0.pin-02-out
net Ystep => parport.0.pin-05-out
net Ydir  => parport.0.pin-04-out
net Zstep => parport.0.pin-07-out
net Zdir  => parport.0.pin-06-out
net Astep => parport.0.pin-09-out
net Adir => parport.0.pin-08-out


newsig Xhome-debounced bit
newsig Yhome-debounced bit
newsig Zhome-debounced bit

newsig Xhome-not bit
newsig Yhome-not bit
newsig Zhome-not bit


newsig Xhome-not-debounced bit
newsig Yhome-not-debounced bit
newsig Zhome-not-debounced bit
newsig FILOend-debounced bit

net Xhome => parport.0.pin-10-in-not
net Yhome => parport.0.pin-11-in-not
net Zhome => parport.0.pin-12-in-not

net Xhome-not => parport.0.pin-10-in
net Yhome-not => parport.0.pin-11-in
net Zhome-not => parport.0.pin-12-in


net Xhome => debounce.0.0.in
net Xhome-debounced => debounce.0.0.out
net Yhome => debounce.0.1.in
net Yhome-debounced => debounce.0.1.out
net Zhome => debounce.0.2.in
net Zhome-debounced => debounce.0.2.out

net Xhome-not => debounce.0.4.in
net Xhome-not-debounced => debounce.0.4.out
net Yhome-not => debounce.0.5.in
net Yhome-not-debounced => debounce.0.5.out
net Zhome-not => debounce.0.6.in
net Zhome-not-debounced => debounce.0.6.out

net FILOend => parport.0.pin-13-in-not
net FILOend => debounce.0.3.in
net FILOend-debounced => debounce.0.3.out

net ALLenable => parport.0.pin-01-out

#setp parport.0.pin-12-in-invert 1
#setp parport.0.pin-11-in-invert 1
#setp parport.0.pin-10-in-invert 1

net Xhome-debounced => axis.0.home-sw-in
net Yhome-debounced => axis.1.home-sw-in
net Zhome-debounced => axis.2.home-sw-in
net ALLenable => motion.motion-enabled

net estop-loop iocontrol.0.user-enable-out iocontrol.0.emc-enable-in

setp lineardeltakins.R 295.4
setp lineardeltakins.L 654

net FILOend-debounced => switches-check.in0
net Xhome-not-debounced => switches-check.in1
net Yhome-not-debounced => switches-check.in2
net Zhome-not-debounced => switches-check.in3

newsig check-pause bit
net check-pause => switches-check.out

newsig check-is-running bit
net check-is-running halui.program.is-running

#net homing0 => axis.0.homing

net check-pause => and-pause-home.in0
net check-is-running and-pause-home.in1

newsig check-pause-home bit

net check-pause-home => and-pause-home.out
net check-pause-home => halui.program.pause

def setup_hbp_led(thread):
    pass

def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-enable' % name, hal.HAL_BIT, init=False)
