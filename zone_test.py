import sys
import math
import linuxcnc
c = linuxcnc.command()
s = linuxcnc.stat()
#assure mdi
s.poll()
if s.task_mode != linuxcnc.MODE_MDI:
  c.mode(linuxcnc.MODE_MDI)
  c.wait_complete()

np=6
angle=math.pi/3
lung=200

points=[]
for i in range(np):
  x=lung*math.cos(math.pi/6+angle*i)
  y=lung*math.sin(math.pi/6+angle*i)
  points.append( ["point "+str(i),"x"+str(int(x))+"y"+str(int(y))] )


c.mdi("G0 Z2")

i=0
while 1:

  cmd=raw_input('next is:')
  if(cmd==""):
    i=i+1
  elif(cmd=="b"):
    i=i-1
  else:
    try:
      i=int(cmd)
    except:
      print("non ho capito")
  i=i%np
  c.mdi("G0Z1")
  c.mdi("G0"+points[i][1])
  c.mdi("G0Z0.3")

  print("going "+ str(points[i]))

#  a=raw_input('next is Z near')
#  c.mdi("G0 x150 y-90")
#  a=raw_input('next is Y near')
#  c.mdi("G0 x-170 y-140")

#c.home(1)
#c.home(2)



#y210 near tower X
#y-210 far tower x
#x150 y-90 near tower z

#x-200 y-200 near tower y
#x160 y110 far tower y
