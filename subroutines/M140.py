#!/bin/sh

# M140: Bed Temperature (Fast)
# Example: M140 S55
# Set the temperature of the build bed to 55oC and return control
# to the host immediately (i.e. before that temperature has been
# reached by the bed). 

halcmd sets hpb-temp-set $1

exit 0
