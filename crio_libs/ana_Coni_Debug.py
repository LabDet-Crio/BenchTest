import os
import time
import subprocess
import math
import fileinput
import sys
from astropy.io import fits 
import numpy as np
import matplotlib.pyplot as plt
import re
from dateutil.parser import parse
import datetime
from scipy.optimize import curve_fit
from scipy import ndimage

import ana_connie_lib as ana

plt.rcParams.update({
    "image.origin": "lower",
    "image.aspect": 1,
    #"text.usetex": True,
    "grid.alpha": .5,
    }) 

# def comp2regions(data_1,data_2,range_1=(-300,850), range_2=(-300,850),default_1=[0,13,1000,50,200],default_2=[0,8,1000,75,200]):
#     fig, (hist_1, hist_2) = plt.subplots(ncols=2, figsize=(12, 4))# plt.subplots(2,1)

#     #ansamp=int(OHDU_File[1].header['ANSAMP'])
#     limits_1=range_1
#     histogram_1, bins_edges_1 = np.histogram(data_1,bins='fd',range=limits_1)
#     class_marks_1 = (bins_edges_1[:-1]+bins_edges_1[1:])/2
#     popt,pcov=curve_fit(ana.gaussian2,class_marks_1,histogram_1,p0=default_1)

#     left = hist_1.bar(class_marks_1,histogram_1)
#     left = hist_1.plot(class_marks_1,ana.gaussian2(class_marks_1,*popt),linewidth=1,c='r', label=r'$\sigma$={:.2f}  gain={:.2f}'.format(abs(popt[1]),abs(popt[3])))        
#     left = hist_1.grid(True)
#     left = hist_1.set_ylim(1,25e3)  
#     left = hist_1.legend()
#     left = hist_1.set_yscale('log')
#     left = hist_1.grid(True)

#     limits_2=range_2
#     histogram_2, bins_edges_2 = np.histogram(data_2,bins='fd',range=limits_2)
#     class_marks_2 = (bins_edges_2[:-1]+bins_edges_2[1:])/2
#     popt_2,pcov_2=curve_fit(ana.gaussian2,class_marks_2,histogram_2,p0=default_2)

#     right = hist_2.bar(class_marks_2,histogram_2)
#     right = hist_2.plot(class_marks_2,ana.gaussian2(class_marks_2,*popt_2),linewidth=1,c='r', label=r'$\sigma$={:.2f}  gain={:.2f}'.format(abs(popt_2[1]),abs(popt_2[3])))        
#     right = hist_2.grid(True)
#     right = hist_2.set_ylim(1,25e3)  
#     right = hist_2.legend()
#     right = hist_2.set_yscale('log')
#     right = hist_2.grid(True)
#     plt.show()
#     return limits_1

nCCDs=16
MCMNro=1
# define active and overscan masks
active_mask = np.s_[:, 10:1057] # 
overscan_mask = np.s_[:, -91:-1] 

ohdusOK = np.zeros((16,), dtype=int)

# fileFits=fits.open('/home/oem/datosFits/mcm_data/ansamp/MCM1_Demuxed_barrido_ANSAMP_exp_1s_ignorando_2muestras_ANSAMP1_18.fits')
# dataCopy=np.copy(fileFits)

# for ext in range(1, len(fileFits)):
#     dataCopy[ext].data=fileFits[ext].data-np.median(fileFits[ext].data[active_mask])

# mediana=ana.Baseline(fileFits, active_mask, 1, nCCDs, doPlot=True,pdfname='None.pdf')

# Noise_list=ana.Noise(fileFits, active_mask, MCMNro, nCCDs, ohdusOK, doPlot=True, pdfname='noise.pdf')

file_1="/home/oem/datosFits/mcm_data/ansamp/fits/MCM1_Demuxed_Test_barrido_ANSAMP_exp_1s_ignorando_2muestras_ANSAMP1_18.fits"
OHDU_File_1 = fits.open(file_1)

file_2="/home/oem/datosFits/mcm_data/ansamp/fits/MCM1_Demuxed_Test_barrido_ANSAMP_exp_1s_ignorando_2muestras_ANSAMP20_20.fits"
OHDU_File_2 = fits.open(file_2)

ext_1=16
ext_2=3

try:
    ANSAMP_1 = int(OHDU_File_1[1].header["ANSAMP"])
except:
    print("Not ANSAMP card detected on File 1")
    ANSAMP_1=1
try:
    ANSAMP_2 = int(OHDU_File_2[1].header["ANSAMP"])
except:
    print("Not ANSAMP card detected on File 1")
    ANSAMP_2=1


dataFits_1=(OHDU_File_1[ext_1].data[active_mask])-np.median(OHDU_File_1[ext_1].data[active_mask])/ANSAMP_1
dataFits_10=((OHDU_File_2[ext_2].data[active_mask])-np.median(OHDU_File_2[ext_2].data[active_mask]))/ANSAMP_2



ana.comp2regions(dataFits_1, dataFits_10,range_1=(-50,180), range_2=(-50,100),default_2=[0,8,1000,40,200])

