#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sys
import glob
import os

#specify 1 experimental data file in this dir and 1 analysis dir with a histo
#script will calculate overlap between U and L of that histo as a percentage
#will make a dir for the pair 

analysis_dirname='rmsd_from_xtal'
#print('=======================================')

system='*'
predir='/beagle3/roux/kyleghaby/kininhibs/main/'+system+'/md/13/'#+state+'/prod/analysis/'

fn='overlap.dat'

dir_l=glob.glob(predir)
with open(fn, 'w') as overlap_fh:
	overlap_fh.write("System"+'\t\t'+"Fraction Overlap"+'\n')
	for d in dir_l:
		system=d.split('/')[6]
		L_datafile='/beagle3/roux/kyleghaby/kininhibs/main/'+system+'/md/13/'+'linked/prod/analysis/'+analysis_dirname+'/data.dat'
		U_datafile='/beagle3/roux/kyleghaby/kininhibs/main/'+system+'/md/13/'+'unlinked/prod/analysis/'+analysis_dirname+'/data.dat'
	
		L_data=np.loadtxt(L_datafile)
		U_data=np.loadtxt(U_datafile)
		
		bin_edges = np.histogram_bin_edges(np.concatenate([L_data.T[1], U_data.T[1]]), bins=10)
		hist1, _ = np.histogram(L_data.T[1], bins=bin_edges, density=False)
		hist2, _ = np.histogram(U_data.T[1], bins=bin_edges, density=False)
		area=np.minimum(hist1, hist2).sum()
		fraction=area/len(U_data.T[1])
		percent=(area/len(U_data.T[1])*100)
		print(system,':\t',area,'/',len(U_data.T[1]),'=',percent,"%")
		overlap_fh.write(system+'\t\t'+str(fraction)+'\n')	
