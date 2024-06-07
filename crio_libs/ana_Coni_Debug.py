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

fileFits=fits.open('/home/oem/datosFits/mcm_data/ansamp/MCM1_Demuxed_barrido_ANSAMP_exp_1s_ignorando_2muestras_ANSAMP1_18.fits')
dataCopy=np.copy(fileFits)

for ext in range(1, len(fileFits)):
    dataCopy[ext].data=fileFits[ext].data-np.median(fileFits[ext].data[active_mask])

mediana=ana.Baseline(fileFits, active_mask, 1, nCCDs, doPlot=True,pdfname='None.pdf')

Noise_list=ana.Noise(fileFits, active_mask, MCMNro, nCCDs, ohdusOK, doPlot=True, pdfname='noise.pdf')