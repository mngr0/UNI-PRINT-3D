#!/usr/bin/python2

#from machinekit import hal
import hal
import time
import tclab

tc= None

def prepare():
  print("prepare")
  global tc
  tc=tclab.TCLab()
  print("arduino tclab ready")


class hal_tclab:
  def __init__(self, name="hal_tclab"):
    print("HERE IS HAL_TCLAB STARITNG")
    self.h = hal.component(name)
#a input pin for every setpoint
#a output pin for every temp
    self.setpoints=[0,0,0,0,0]
    for i in range(4):
      self.h.newpin("setpoint-"+str(i), hal.HAL_FLOAT, hal.HAL_IN)
      self.h.newpin("temperature-"+str(i), hal.HAL_FLOAT, hal.HAL_OUT)
      self.h.newpin("enable-"+str(i),hal.HAL_BIT, hal.HAL_IN)
      self.h.newpin("error-"+str(i), hal.HAL_BIT, hal.HAL_OUT)
      self.h["temperature-"+str(i)] = 0
      self.h["setpoint-"+str(i)] = 0
      self.h["enable-"+str(i)] = 0
      global tc
      if tc is None:
        prepare()
      self.tc=tc
    self.h.newpin("enable",hal.HAL_BIT, hal.HAL_IN)
    self.h.newpin("error", hal.HAL_BIT, hal.HAL_OUT)


    for i in range(4):
      self.setpoints[i] = self.tc.getsetpoint(i)
      self.h["error-"+str(i)]= False
    self.h["error"] = 0

    self.h.ready()

    print("HERE IS HAL_TCLAB READY")


  def take(self):
    return self.h

  def routine(self):
    try:
      self.h["error"]=False
      while 1:
        self.h["error"]=False
        try:
          for i in range(4):
            self.h["temperature-"+str(i)]=self.tc.temperature(i)
            tmp_set =  self.h["setpoint-"+str(i)]
            if tmp_set != self.setpoints[i]:
              self.tc.setsetpoint(i,tmp_set)
              self.setpoints[i] = tmp_set
            if self.h["enable"] and self.h["enable-"+str(i)]:
              if self.h["temperature-"+str(i)] > -20 :
                self.tc.enable(i)
                self.h["error-"+str(i)] = False
              else:
                self.tc.disable(i)
                self.h["error-"+str(i)] = True
            else:
              self.tc.disable(i)
        except Exception as e:
          self.h["error"] = True
          print (str(e))
    except Exception as e:
      print( str(e))
      raise SystemExit


print("HERE IS HAL_TCLAB MAIN")
comp= hal_tclab()

try:
  while 1:
    comp.routine()
    time.sleep(0.01)
except Exception as e:
  print (str(e))
  raise SystemExit
