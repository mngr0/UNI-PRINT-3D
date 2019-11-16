from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

import rcomps
import storage
import motion

def assign_param(name,signal,val):
    import subprocess
    subprocess.call("halcmd setp %s.%s %s"%(name,signal,str(val)), shell=True )



def usrcomp_status(compname, signame, thread, resetSignal='estop-reset'):
    sigIn = hal.newsig('%s-error-in' % signame, hal.HAL_BIT)
    sigOut = hal.newsig('%s-error' % signame, hal.HAL_BIT)
    sigOk = hal.newsig('%s-ok' % signame, hal.HAL_BIT)

    sigIn.link('%s.error' % compname)

    safetyLatch = rt.newinst('safety_latch', 'safety-latch.%s-error' % signame)
    hal.addf(safetyLatch.name, thread)
    safetyLatch.pin('error-in').link(sigIn)
    safetyLatch.pin('error-out').link(sigOut)
    safetyLatch.pin('reset').link(resetSignal)
    safetyLatch.pin('threshold').set(500)  # 500ms error
    safetyLatch.pin('latching').set(True)

    notComp = rt.newinst('not', 'not.%s-no-error' % signame)
    hal.addf(notComp.name, thread)
    notComp.pin('in').link(sigOut)
    notComp.pin('out').link(sigOk)


def usrcomp_watchdog(comps, enableSignal, thread,
                     okSignal=None, errorSignal=None):
    count = len(comps)
    watchdog = rt.loadrt('watchdog', num_inputs=count)
    hal.addf('watchdog.set-timeouts', thread)
    hal.addf('watchdog.process', thread)
    for n, comp in enumerate(comps):
        compname = comp[0]
        comptime = comp[1]
        sigIn = hal.newsig('%s-watchdog' % compname, hal.HAL_BIT)
        hal.Pin('%s.watchdog' % compname).link(sigIn)
        watchdog.pin('input-%i' % n).link(sigIn)
        watchdog.pin('timeout-%i' % n).set(comptime)
    watchdog.pin('enable-in').link(enableSignal)

    if not okSignal:
        okSignal = hal.newsig('watchdog-ok', hal.HAL_BIT)
    watchdog.pin('ok-out').link(okSignal)

    if errorSignal:
        notComp = rt.newinst('not', 'not.watchdog-error')
        hal.addf(notComp.name, thread)
        notComp.pin('in').link(okSignal)
        notComp.pin('out').link(errorSignal)


def setup_stepper(stepgenIndex, section, axisIndex=None,
                  stepgenType='hpg.stepgen', gantry=False,
                  gantryJoint=0, velocitySignal=None, thread=None):
    stepgen = '%s.%01i' % (stepgenType, stepgenIndex)
    if axisIndex is not None:
        axis = 'axis.%i' % axisIndex
    hasMotionAxis = (axisIndex is not None) and (not gantry or gantryJoint == 0)
    velocityControlled = velocitySignal is not None

    # axis enable chain
    enableIndex = axisIndex
    if axisIndex is None:
        enableIndex = 0  # use motor enable signal
    enable = hal.Signal('emcmot-%i-enable' % enableIndex, hal.HAL_BIT)
    if hasMotionAxis:
        enable.link('%s.amp-enable-out' % axis)
    enable.link('%s.enable' % stepgen)

    # expose timing parameters so we can multiplex them later
    sigBase = 'stepgen.%i' % stepgenIndex

    assign_param(sigBase,"position-scale",c.find("ABP", 'SCALE'))
    assign_param(sigBase,"maxaccel",c.find("ABP", 'STEPGEN_MAXACC'))
    #assign_param(sigBase,"maxvel",c.find("ABP", 'STEPGEN_MAXVEL'))

    # position command and feedback
    limitHome = hal.newsig('limit-%i-home' % axisIndex, hal.HAL_BIT)
    limitMin = hal.newsig('limit-%i-min' % axisIndex, hal.HAL_BIT)
    limitMax = hal.newsig('limit-%i-max' % axisIndex, hal.HAL_BIT)
    limitHome.link('%s.home-sw-in' % axis)
    limitMin.link('%s.neg-lim-sw-in' % axis)
    limitMax.link('%s.pos-lim-sw-in' % axis)

    if velocityControlled:
        hal.net(velocitySignal, '%s.velocity-cmd' % stepgen)

def setup_stepper_multiplexer(stepgenIndex, sections, selSignal, thread):
    num = len(sections)
    sigBase = 'stepgen-%i' % stepgenIndex

    unsignedSignals = [['dirsetup', 'DIRSETUP'],
                       ['dirhold', 'DIRHOLD'],
                       ['steplen', 'STEPLEN'],
                       ['stepspace', 'STEPSPACE']]

    floatSignals = [['scale', 'SCALE'],
                    ['max-vel', 'STEPGEN_MAX_VEL'],
                    ['max-acc', 'STEPGEN_MAX_ACC']]

    for item in unsignedSignals:
        signal = hal.Signal('%s-%s' % (sigBase, item[0]), hal.HAL_U32)
        mux = rt.newinst('muxn_u32', 'mux%i.%s' % (num, signal.name), pincount=num)
        hal.addf(mux.name, thread)
        for n, section in enumerate(sections):
            mux.pin('in%i' % n).set(c.find(section, item[1]))
        mux.pin('sel').link(selSignal)
        mux.pin('out').link(signal)

    for item in floatSignals:
        signal = hal.Signal('%s-%s' % (sigBase, item[0]), hal.HAL_FLOAT)
        mux = rt.newinst('muxn', 'mux%i.%s' % (num, signal.name), pincount=num)
        hal.addf(mux.name, thread)
        for n, section in enumerate(sections):
            mux.pin('in%i' % n).set(c.find(section, item[1]))
        mux.pin('sel').link(selSignal)
        mux.pin('out').link(signal)


def setup_probe(thread):
    probeEnable = hal.newsig('probe-enable', hal.HAL_BIT)
    probeInput = hal.newsig('probe-input', hal.HAL_BIT)
    probeSignal = hal.newsig('probe-signal', hal.HAL_BIT)

    and2 = rt.newinst('and2', 'and2.probe-input')
    hal.addf(and2.name, thread)
    and2.pin('in0').link(probeSignal)
    and2.pin('in1').link(probeEnable)
    and2.pin('out').link(probeInput)

    probeInput += 'motion.probe-input'

    motion.setup_probe_io()

def setup_tclab():
    #import hal_tclab
    # from hal_tclab import prepare
    # prepare()
    hal.loadusr("hal_tclab",name="hal_tclab",wait_name="hal_tclab",wait_timeout=15)
    hal.Pin("hal_tclab.enable").link(hal.Signal("ALLenable"))



def create_temperature_control(name, section, thread, hardwareOkSignal=None,
                               coolingFan=None, hotendFan=None, tclab_index=0):

    tempSet = hal.newsig('%s-temp-set' % name, hal.HAL_FLOAT)
    tempMeas = hal.newsig('%s-temp-meas' % name, hal.HAL_FLOAT)
    tempInRange = hal.newsig('%s-temp-in-range' % name, hal.HAL_BIT)
    active = hal.newsig('%s-active' % name, hal.HAL_BIT)
    tempLimitMin = hal.newsig('%s-temp-limit-min' % name, hal.HAL_FLOAT)
    tempLimitMax = hal.newsig('%s-temp-limit-max' % name, hal.HAL_FLOAT)

    hal.Pin("hal_tclab.temperature-%s"%str(tclab_index)).link(tempMeas)
    hal.Pin("hal_tclab.setpoint-%s"%str(tclab_index)).link(tempSet)
    hal.Pin("hal_tclab.enable-%s"%str(tclab_index)).link(active)

    tempInLimit = hal.newsig('%s-temp-in-limit' % name, hal.HAL_BIT)
    tempThermOk = hal.newsig('%s-temp-therm-ok' % name, hal.HAL_BIT)
    error = hal.newsig('%s-error' % name, hal.HAL_BIT)


    tempPidPgain = hal.newsig('%s-temp-pid-Pgain' % name, hal.HAL_FLOAT)
    tempPidIgain = hal.newsig('%s-temp-pid-Igain' % name, hal.HAL_FLOAT)
    tempPidDgain = hal.newsig('%s-temp-pid-Dgain' % name, hal.HAL_FLOAT)
    tempPidMaxerrorI = hal.newsig('%s-temp-pid-maxerrorI' % name, hal.HAL_FLOAT)
    tempPidOut = hal.newsig('%s-temp-pid-out' % name, hal.HAL_FLOAT)
    tempPidBias = hal.newsig('%s-temp-pid-bias' % name, hal.HAL_FLOAT)
    tempRangeMin = hal.newsig('%s-temp-range-min' % name, hal.HAL_FLOAT)
    tempRangeMax = hal.newsig('%s-temp-range-max' % name, hal.HAL_FLOAT)
    noErrorIn = hal.newsig('%s-no-error-in' % name, hal.HAL_BIT)
    errorIn = hal.newsig('%s-error-in' % name, hal.HAL_BIT)

    sum2 = rt.newinst('sum2', 'sum2.%s-temp-range-pos' % name)
    hal.addf(sum2.name, thread)
    sum2.pin('in0').link(tempSet)
    sum2.pin('in1').set(c.find(section, 'TEMP_RANGE_POS_ERROR'))
    sum2.pin('out').link(tempRangeMax)

    sum2 = rt.newinst('sum2', 'sum2.%s-temp-range-neg' % name)
    hal.addf(sum2.name, thread)
    sum2.pin('in0').link(tempSet)
    sum2.pin('in1').set(c.find(section, 'TEMP_RANGE_NEG_ERROR'))
    sum2.pin('out').link(tempRangeMin)

    #the output of this component will say if measured temperature is in range of set value
    wcomp = rt.newinst('wcomp', 'wcomp.%s-temp-in-range' % name)
    hal.addf(wcomp.name, thread)
    wcomp.pin('min').link(tempRangeMin)
    wcomp.pin('max').link(tempRangeMax)
    wcomp.pin('in').link(tempMeas)
    wcomp.pin('out').link(tempInRange)

    # limit the output temperature to prevent damage when thermistor is broken/removed
    wcomp = rt.newinst('wcomp', 'wcomp.%s-temp-in-limit' % name)
    hal.addf(wcomp.name, thread)
    wcomp.pin('min').link(tempLimitMin)
    wcomp.pin('max').link(tempLimitMax)
    wcomp.pin('in').link(tempMeas)
    wcomp.pin('out').link(tempInLimit)

    rcomps.create_temperature_rcomp(name)
    motion.setup_temperature_io(name)


def setup_estop(errorSignals, thread):
    # Create estop signal chain
    estopTest = hal.Signal('estop-test', hal.HAL_BIT)
    estopUser = hal.Signal('estop-user', hal.HAL_BIT)
    estopReset = hal.Signal('estop-reset', hal.HAL_BIT)
    estopOut = hal.Signal('estop-out', hal.HAL_BIT)
    estopIn = hal.Signal('estop-in', hal.HAL_BIT)
    estopError = hal.Signal('estop-error', hal.HAL_BIT)

    #num = len(errorSignals)
    #orComp = rt.newinst('orn', 'or%i.estop-error' % num, pincount=num)
    #hal.addf(orComp.name, thread)
    #for n, sig in enumerate(errorSignals):
    #    orComp.pin('in%i' % n).link(sig)
    #orComp.pin('out').link(estopError)
    estopError.set(0)
    estopLatch = rt.newinst('estop_latch', 'estop-latch')
    hal.addf(estopLatch.name, thread)
    estopLatch.pin('ok-in').link(estopUser)
    estopLatch.pin('fault-in').link(estopError)
    estopLatch.pin('reset').link(estopReset)
    estopLatch.pin('ok-out').link(estopOut)


    estopReset.link('iocontrol.0.user-request-enable')
    estopUser.link('iocontrol.0.user-enable-out')


    # Monitor estop input from hardware
    estopIn.link('iocontrol.0.emc-enable-in')
#    hal.net('iocontrol.0.user-enable-out', 'iocontrol.0.emc-enable-in')

def setup_estop_loopback():
    # create signal for estop loopback
    hal.net('iocontrol.0.user-enable-out', 'iocontrol.0.emc-enable-in')

def setup_tool_loopback():
    hal.net('iocontrol.0.tool-prepare', 'iocontrol.0.tool-prepared')
    hal.net('iocontrol.0.tool-change', 'iocontrol.0.tool-changed')

def setup_delta():
    assign_param("lineardeltakins","R","295.4")
    assign_param("lineardeltakins","L","654")
