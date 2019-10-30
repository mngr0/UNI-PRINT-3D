from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

from fdm.config import base


def hardware_read():
    hal.addf('stepgen.capture-position', 'servo-thread')
    hal.addf('motion-command-handler', 'servo-thread')


def hardware_write():
    hal.addf('motion-controller', 'servo-thread')
    hal.addf('addf stepgen.update-freq', 'servo-thread')
    hal.addf('debounce.funct', 'servo-thread')


def init_hardware():
    watchList = []

    # load low-level drivers
    rt.loadrt('hal_parport', cfg='0x0378')
    rt.loadrt('stepgen', step_type='0,0,0,0')
    deb = rt.newinst('debounce', 'debounce')



def setup_hardware(thread):
    # Stepper
    posSignal = hal.newsig('%spos-cmd' % "X", hal.HAL_FLOAT)
    stepSignal = hal.newsig('%sstep' % "X", hal.HAL_FLOAT)
    dirSignal = hal.newsig('%sdir' % "X", hal.HAL_FLOAT)
    hal.Pin('stepgen.%s.position-cmd' % str(0)).link(posSignal)
    hal.Pin('axis.%s.motor-pos-cmd' % str(0)).link(posSignal)
    hal.Pin('parport.0.pin-03-out')
    # link emcmot.xx.enable to stepper driver enable signals




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
