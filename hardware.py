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

def setup_hbp_led(thread):
    pass

def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-enable' % name, hal.HAL_BIT, init=False)
