from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

from fdm.config import base

def assign_param(name,signal,val):
    import subprocess
    subprocess.call("halcmd setp %s.%s %s"%(name,signal,str(val)), shell=True )
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
    hal.addf('switches-check.funct',"servo-thread")
    hal.addf('pause-home.funct',"servo-thread")
    hal.addf('ilowpass.jog.x','servo-thread')
    hal.addf('ilowpass.jog.y','servo-thread')
    hal.addf('ilowpass.jog.z','servo-thread')
    hal.addf('ilowpass.jog.a','servo-thread')



def init_hardware():
    watchList = []

    # load low-level drivers
    rt.loadrt('hal_parport', cfg='0x0378')
    rt.loadrt('stepgen', step_type='0,0,0,0',ctrl_type="p,p,p,p")
    #rt.loadrt("ilowpass", names="ilowpass.jog.x")
    deb = rt.newinst('debounce', 'debounce')
    # witches-check=
    rt.newinst("orn","switches-check", pincount="4")
    # pause-check=
    rt.newinst("andn","pause-home", pincount="2")


def setup_hardware(thread):
    # Stepper
    checkFiloRawSignal = hal.newsig("filo_raw", hal.HAL_BIT)
    checkFiloSignal = hal.newsig("filo", hal.HAL_BIT)
    hal.Pin("parport.0.pin-13-in-not" ).link(checkFiloRawSignal)
    hal.Pin("debounce.%s.in"%str(6)).link(checkFiloRawSignal)
    hal.Pin("debounce.%s.out"%str(6)).link(checkFiloSignal)
    hal.Pin("switches-check.in3").link(checkFiloSignal)
    pinout={
        "step":{ "X":"03",
                 "Y":"05",
                 "Z":"07",
                 "A":"09"
        },

        "dir":{ "X":"02",
                "Y":"04",
                "Z":"06",
                "A":"08"
        },
        "home":{"X":"10",
                "Y":"11",
                "Z":"12",

        }
    }
    for i,a in enumerate(["X","Y","Z"]):
        posSignal = hal.newsig('%spos-cmd' % a, hal.HAL_FLOAT)
        fbSignal = hal.newsig('%spos-fb' % a, hal.HAL_FLOAT)
        stepSignal = hal.newsig('%sstep' % a, hal.HAL_BIT)
        dirSignal = hal.newsig('%sdir' % a, hal.HAL_BIT)

        checkSignal = hal.newsig("%sswitch_check"%a, hal.HAL_BIT)
        #enSignal = hal.newsig('%senable' % a, hal.HAL_BIT)
        hal.Pin('stepgen.%s.position-cmd' % str(i)).link(posSignal)
        hal.Pin('axis.%s.motor-pos-cmd' % str(i)).link(posSignal)
        hal.Pin('parport.0.pin-%s-out' % pinout["step"][a]).link(stepSignal)
        hal.Pin('parport.0.pin-%s-out' % pinout["dir"][a]).link(dirSignal)
        hal.Pin("stepgen.%s.dir"%str(i)).link(dirSignal)
        hal.Pin("stepgen.%s.step"%str(i)).link(stepSignal)
        hal.Pin("stepgen.%s.position-fb"%str(i)).link(fbSignal)
        hal.Pin("axis.%s.motor-pos-fb"%str(i)).link(fbSignal)

        homeRawSignal = hal.newsig("%shome_raw"%a, hal.HAL_BIT)
        homeNotRawSignal = hal.newsig("%shome_raw_not"%a, hal.HAL_BIT)
        hal.Pin("parport.0.pin-%s-in-not" % pinout["home"][a]).link(homeRawSignal)
        hal.Pin("debounce.%s.in"%str(i)).link(homeRawSignal)
        hal.Pin("debounce.%s.out"%str(i)).link(hal.Signal("limit-%s-home"%str(i)))

        hal.Pin("parport.0.pin-%s-in" % pinout["home"][a]).link(homeNotRawSignal)
        hal.Pin("debounce.%s.in"%str(i+3)).link(homeNotRawSignal)
        hal.Pin("debounce.%s.out"%str(i+3)).link(checkSignal)
        hal.Pin("switches-check.in%s"%str(i)).link(checkSignal)




    i,a = 3, "A"
    #only if not VE
    posSignal = hal.newsig('%spos-cmd' % a, hal.HAL_FLOAT)
    
    
    fbSignal = hal.newsig('%spos-fb' % a, hal.HAL_FLOAT)
    stepSignal = hal.newsig('%sstep' % a, hal.HAL_BIT)
    dirSignal = hal.newsig('%sdir' % a, hal.HAL_BIT)

    # checkSignal = hal.newsig("%sswitch_check"%a, hal.HAL_BIT)
    # #enSignal = hal.newsig('%senable' % a, hal.HAL_BIT)
    
    
    
    #only if not VE
    hal.Pin('stepgen.%s.position-cmd' % str(i)).link(posSignal)
    hal.Pin('axis.%s.motor-pos-cmd' % str(i)).link(posSignal)
    
    
    
    hal.Pin('parport.0.pin-%s-out' % pinout["step"][a]).link(stepSignal)
    hal.Pin('parport.0.pin-%s-out' % pinout["dir"][a]).link(dirSignal)
    hal.Pin("stepgen.%s.dir"%str(i)).link(dirSignal)
    hal.Pin("stepgen.%s.step"%str(i)).link(stepSignal)
    hal.Pin("stepgen.%s.position-fb"%str(i)).link(fbSignal)

    #only if not VE
    hal.Pin("axis.%s.motor-pos-fb"%str(i)).link(fbSignal)
    
    
    assign_param("parport.0","pin-08-out-invert",1)
    ##### END A AXES


    switchOut = hal.newsig("switches-out",hal.HAL_BIT)
    hal.Pin("switches-check.out").link(switchOut)
    hal.Pin("pause-home.in0").link(switchOut)


    enableSignal = hal.newsig("ALLenable",hal.HAL_BIT)
    hal.Pin('motion.motion-enabled').link(enableSignal)
    hal.Pin('parport.0.pin-01-out').link(enableSignal)
    # link emcmot.xx.enable to stepper driver enable signals

    motionOn = hal.Signal("is-running",hal.HAL_BIT)
    # hal.Pin("halui.program.is-running").link(motionOn)
    hal.Pin("pause-home.in1").link(motionOn)

    doPause = hal.newsig("do-pause",hal.HAL_BIT)
    hal.Pin("pause-home.out").link(doPause)
    hal.Pin("halui.program.pause")

def setup_hbp_led(thread):
    pass

def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-enable' % name, hal.HAL_BIT, init=False)
