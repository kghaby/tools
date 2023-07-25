#!/usr/bin/python3
import numpy as np
import sys
import math
import os
if os.path.exists("data.dat"):
  os.remove("data.dat")
if os.path.exists("xtal.dat"):
  os.remove("xtal.dat")


reffile='prextal.dat' #file that contains coords of xtal
datafile='predata.dat' #file of coords of sim

def calculateDistance(x1,y1,z1,x2,y2,z2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return dist

ref=np.loadtxt(reffile)
data=np.loadtxt(datafile)

refx=float(ref[1])
refy=float(ref[2])
refz=float(ref[3])
with open('data.dat','w') as dist_fh:
	dist_fh.write('#Frame\t\tDistance\n')
	for line in data:
		#print(line.T)
		datat=float(line[0])
		datax=float(line[1])
		datay=float(line[2])
		dataz=float(line[3])
		dist=calculateDistance(refx,refy,refz,datax,datay,dataz)
		dist_fh.write(str(datat)+'\t\t'+str(dist)+'\n')
with open('xtal.dat','w') as xdist_fh:
        xdist_fh.write('#Frame\t\tDistance\n')
        datat=float(ref[0])
        datax=float(ref[1])
        datay=float(ref[2])
        dataz=float(ref[3])
        dist=calculateDistance(refx,refy,refz,datax,datay,dataz)
        xdist_fh.write(str(datat)+'\t\t'+str(dist)+'\n')


