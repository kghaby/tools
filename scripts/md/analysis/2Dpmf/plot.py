#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sys
import glob
import os

y_analysis_name='dist_com2xtalcom'
x_analysis_name='linkdist'

os.mkdir(x_analysis_name+'-'+y_analysis_name)
os.chdir(x_analysis_name+'-'+y_analysis_name)

system='*'
state='unlinked'
predir='/beagle3/roux/kyleghaby/kininhibs/main/'+system+'/md/13/'+state+'/prod/analysis/'

dir_l=glob.glob(predir)
for d in dir_l:
	system=d.split('/')[6]
	state=d.split('/')[9]

	print(system)
	x_dir_name=d+x_analysis_name
	y_dir_name=d+y_analysis_name

	fi=system+'-'+state+'_'+x_analysis_name+'-'+y_analysis_name+'.png'
	ti=system+' '+state

	datax=np.loadtxt(x_dir_name+'/data.dat')
	datay=np.loadtxt(y_dir_name+'/data.dat')
	xtalx=np.loadtxt(x_dir_name+'/xtal.dat')
	xtaly=np.loadtxt(y_dir_name+'/xtal.dat')

	x=datax[0:,1]
	y=datay[0:,1]
	xtalx=xtalx[1]
	xtaly=xtaly[1]
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
	plt.rcParams.update({'font.size': 32})
	my_dpi=96
	fig = plt.figure(figsize=(1920/my_dpi,1920/my_dpi), dpi=my_dpi)
	#ax1=fig2.add_subplot(111)
	#plt.pcolormesh(xedges,yedges,Gmasked,cmap ='rainbow_r')
	plt.pcolormesh(xedges,yedges,Gmasked,cmap ='jet_r')
	title=plt.title(ti,y=1.05, transform=plt.gca().transAxes)
	plt.xlim(0,8)
	plt.ylim(0,2)
	plt.xlabel(x_analysis_name)
	plt.ylabel(y_analysis_name)
	cbar = plt.colorbar()
	cbar.ax.set_ylabel('kcal/mol')
	#plt.scatter(xtalx,xtaly,s=100,marker="d",label="Xtal", color="xkcd:maroon")
	#plt.legend(loc='upper right')
#	plt.show()
	fig.savefig(fi)

