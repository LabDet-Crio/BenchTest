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

nCCDs=16
MCMNro=1
# define active and overscan masks
active_mask = np.s_[:, 10:1057] # 
overscan_mask = np.s_[:, -91:-1] 

ohdusOK = np.zeros((16,), dtype=int)

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

#------------------------------ comp2Regions------------------------------

# dataFits_1=(OHDU_File_1[ext_1].data[active_mask])-np.median(OHDU_File_1[ext_1].data[active_mask])/ANSAMP_1
# dataFits_10=((OHDU_File_2[ext_2].data[active_mask])-np.median(OHDU_File_2[ext_2].data[active_mask]))/ANSAMP_2

# ana.comp2regions(dataFits_1, dataFits_10,range_1=(-50,180), range_2=(-50,100),default_2=[0,8,1000,40,200])
#-------------------------------------------------------------------------

#----------------------------plot2images----------------------------------
ana.Plot2Images_v2(OHDU_File_1[ext_1].data,OHDU_File_2[ext_2].data,MinRange=None,MaxRange=None, colorBar_1=True, colorBar_2=True, saveFig=False)


#-------------------------------------------------------------------------
