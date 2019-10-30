from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

from fdm.config import base


def hardware_read():
    hal.addf('stepgen.capture-position', 'servo-thread')
    hal.addf('motion-command-handler', 'servo-thread')
    hal.addf('parport.0.read','base-thread') #must be base-thread


def hardware_write():
    hal.addf('motion-controller', 'servo-thread')
    hal.addf('stepgen.update-freq', 'servo-thread')
    hal.addf('debounce.funct', 'servo-thread')
    hal.addf('stepgen.make-pulses','base-thread') #must be base-thread
    hal.addf('parport.0.write','base-thread') #must be base-thread
def init_hardware():
    watchList = []

    # load low-level drivers
    rt.loadrt('hal_parport', cfg='0x0378')
    rt.loadrt('stepgen', step_type='0,0,0,0',ctrl_type="p,p,p,v")
    deb = rt.newinst('debounce', 'debounce')


def setup_hardware(thread):
    # Stepper
    pinout={
        "step":{ "X":"03",
                 "Y":"05",
                 "Z":"07"
        },

        "dir":{ "X":"02",
                "Y":"04",
                "Z":"06"
        },
        "home":{"X":"10",
                "Y":"11",
                "Z":"12"
        }
    }
    for i,a in enumerate(["X","Y","Z"]):
        posSignal = hal.newsig('%spos-cmd' % a, hal.HAL_FLOAT)
        fbSignal = hal.newsig('%spos-fb' % a, hal.HAL_FLOAT)
        stepSignal = hal.newsig('%sstep' % a, hal.HAL_BIT)
        dirSignal = hal.newsig('%sdir' % a, hal.HAL_BIT)
        homeRawSignal = hal.newsig("%shome_raw"%a, hal.HAL_BIT)

        #enSignal = hal.newsig('%senable' % a, hal.HAL_BIT)
        hal.Pin('stepgen.%s.position-cmd' % str(i)).link(posSignal)
        hal.Pin('axis.%s.motor-pos-cmd' % str(i)).link(posSignal)
        hal.Pin('parport.0.pin-%s-out' % pinout["step"][a]).link(stepSignal)
        hal.Pin('parport.0.pin-%s-out' % pinout["dir"][a]).link(dirSignal)
        hal.Pin("stepgen.%s.dir"%str(i)).link(dirSignal)
        hal.Pin("stepgen.%s.step"%str(i)).link(stepSignal)
        hal.Pin("stepgen.%s.position-fb"%str(i)).link(fbSignal)
        hal.Pin("axis.%s.motor-pos-fb"%str(i)).link(fbSignal)

        hal.Pin("parport.0.pin-%s-in-not" % pinout["home"][a]).link(homeRawSignal)
        hal.Pin("debounce.%s.in"%str(i)).link(homeRawSignal)
        hal.Pin("debounce.%s.out"%str(i)).link(hal.Signal("limit-%s-home"%str(i)))
        #hal.Pin("stepgen.%s.enable"%str(i)).link(enSignal)
        #hal.Pin("axis.%s.amp-enable-out"%str(i)).link(enSignal)
    enableSignal = hal.newsig("ALLenable",hal.HAL_BIT)
    hal.Pin('motion.motion-enabled').link(enableSignal)
    hal.Pin('parport.0.pin-01-out').link(enableSignal)
    # link emcmot.xx.enable to stepper driver enable signals





def setup_hbp_led(thread):
    pass

def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-enable' % name, hal.HAL_BIT, init=False)
