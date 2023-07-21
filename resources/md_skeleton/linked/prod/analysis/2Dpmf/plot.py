#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sys

x_dir_name='linkdist'
y_dir_name='o-hn_dist'

fi=x_dir_name+'-'+y_dir_name+'.png'
ti=x_dir_name+'-'+y_dir_name

datax=np.loadtxt('../'+x_dir_name+'/data.dat')
datay=np.loadtxt('../'+y_dir_name+'/data.dat')
xtalx=np.loadtxt('../'+x_dir_name+'/xtal.dat')
xtaly=np.loadtxt('../'+y_dir_name+'/xtal.dat')

x=datax[0:,1]
y=datay[0:,1]
xtalx=xtalx[1]
xtaly=xtaly[1]
# Plot data
#fig1 = plt.figure()
#plt.plot(x,y,'.r')
#plt.xlabel('x')
#plt.ylabel('y')

nbins=100
H, xedges, yedges = np.histogram2d(x,y,bins=nbins)
# H needs to be rotated and flipped
H = np.rot90(H)
H = np.flipud(H)
G=-0.0019872041*310*np.log(H/np.sum(H))
G=G-np.min(G)
# Mask zeros
#Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
Gmasked = np.ma.masked_where(G=='inf',G) # Mask pixels with a value of zero

# Plot 2D histogram using pcolor
plt.rcParams.update({'font.size': 24})
my_dpi=96
fig2 = plt.figure(figsize=(1280/my_dpi, 960/my_dpi), dpi=my_dpi)
#ax1=fig2.add_subplot(111)
#plt.pcolormesh(xedges,yedges,Gmasked,cmap ='rainbow_r')
plt.pcolormesh(xedges,yedges,Gmasked,cmap ='jet_r')
plt.title(ti)
plt.xlim(0,3)
plt.ylim(0,9)
plt.xlabel(x_dir_name)
plt.ylabel(y_dir_name)
cbar = plt.colorbar()
cbar.ax.set_ylabel('kcal/mol')
plt.scatter(xtalx,xtaly,s=100,marker="d",label="Xtal", color="xkcd:maroon")
plt.legend(loc='upper right')
plt.show()
fig2.savefig(fi)

