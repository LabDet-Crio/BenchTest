import os
import glob
import sys
import numpy as np
import math
import argparse
from scipy.stats import norm
from astropy.stats import median_absolute_deviation as mad
from astropy.io import fits
from matplotlib import pyplot as plt
import matplotlib as mb
from scipy.optimize import curve_fit
import pandas as pd

def gaussian(x, a, mean, sigma):
    return a * np.exp(-((x - mean)**2 / (2 * sigma**2)))

def sqrt(x, sigma0):
    return sigma0 / np.sqrt(x)

def varsort(item):
	return int(item.split("_SSAMP")[1].split("_")[0])

def hist_and_DataFr(files, optionFlag = 0, graphicFlag = 0):
    list_var=[]				# List to store the computed variable

    imgDict={}
    list_StandarDev = []
    list_Noises = []
    list_Names = []
    list_Temp = []
    list_Exposure = []
    list_VoltageFile = []
    nSamp=[]

    # Define active and overscan areas
    active_mask = np.s_[:, 9:538]		#   9 <= x < 538
    overscan_mask = np.s_[:, 538:]		# 538 <= x
    mask=np.s_[:, :]			# Area where variable will be computed
    expgain = [191, 191, 193, 158]

    fig_all, axs_all = plt.subplots(1, 4, figsize=(20, 5))	# Define figure to stack histograms of all images

    for image in files:
        hdul=fits.open(image)
#		hdul.info()
        img=os.path.basename(image)				# Get basename of image

        j=files.index(image)
        figctr=0

        var=[]
        var_fit=[]

        for i in range(0, len(hdul)):

			# Load data and header
            data=hdul[i].data
            header=hdul[i].header

            if data is not None:				# Check if data is not empty

#				data = data - np.median(data, axis=0, keepdims=True)			# Subtract median per column
#				data = data - np.median(data[overscan_mask], axis=1, keepdims=True)	# Subtract OS median per row

				# Extract info from header
                string='RUNID'
                stringval=header[string]
                nsamp=float(header['RUNID'])
                exposure = float(header['EXPOSURE'])
    

#				hlabel = string+" "+stringval			# Define label of histogram
                hlabel = img

				#Plot histogram of data to obtain offset
                hist, bin_edges = np.histogram(data[mask].flatten(), bins=1000000)
                offset = bin_edges[np.argmax(hist)]
#				print(offset)
                data = data-offset		# Subtract offset from data
#				offset = 0
				
                bin_heights, bin_borders, _ = axs_all[figctr].hist(data[mask].flatten(), range=[offset-1500, offset+1500], bins=100, histtype='step', label=hlabel)
                offset_fit = bin_borders[np.argmax(bin_heights)]
                axs_all[figctr].set_title('ext '+str(figctr+1))
                handles_all, labels_all = axs_all[figctr].get_legend_handles_labels()
                bin_centers=np.zeros(len(bin_heights), dtype=float)			# Compute centers of each bin

                for p in range(len(bin_heights)):
                    bin_centers[p]=(bin_borders[p+1]+bin_borders[p])/2

                xmin_fit, xmax_fit = offset_fit-(10*expgain[figctr])/math.sqrt(nsamp), offset_fit+(10*expgain[figctr])/math.sqrt(nsamp)			# Define fit range
                bin_heights = bin_heights[(bin_centers>xmin_fit) & (bin_centers<xmax_fit)]
                bin_centers = bin_centers[(bin_centers>xmin_fit) & (bin_centers<xmax_fit)]

#				popt, pcov = curve_fit(gaussian, bin_centers, bin_heights, p0=[np.max(bin_heights), 0, var[figctr]], maxfev=100000)	# Fit histogram with gaussian
                popt, pcov = curve_fit(gaussian, bin_centers, bin_heights, p0=[np.max(bin_heights), 0, expgain[figctr]], maxfev=100000)		# Fit histogram with gaussian
                axs_all[figctr].plot(bin_centers, gaussian(bin_centers, *popt))								# Plot gaussian fit
#				print(popt)

#				var_fit.append(abs(popt[2])/float(stringval))
                var_fit.append(round(abs(popt[2])/float(expgain[figctr]),5)) 

#				var.append(np.std(data[mask])/float(stringval))		# Standard deviation
                var.append(round(np.std(data[mask])/float(expgain[figctr]),5))	# Standard deviation
#				var.append(np.mean(data[mask]))		# Mean
#				var.append(np.median(data[mask]))	# Median

                figctr=figctr+1
                
                # plt.legend()
        # plt.show()			# Show histogram per image
        ImgName=str(image)
        Tempt = ImgName.split('_')
        list_Temp.append(Tempt[6][1:])
        list_VoltageFile.append(Tempt[5][-1])

        list_StandarDev.append(var)
        list_Noises.append(var_fit)
        list_Names.append(int(stringval))
        nSamp.append(int(header['NSAMP']))
        list_Exposure.append(int(header['EXPOSURE']))
        
        # Añade elementos al diccionario
        imgDict.setdefault('img'+stringval,{'stdv':[round(var[0],5), round(var[1],5), round(var[2],5), round(var[3],5)],
                            'noise':[round(var_fit[0],5), round(var_fit[1],5), round(var_fit[2],5), round(var_fit[3],5)]})


        datos_imgDict= pd.DataFrame([key for key in imgDict.keys()])
        datos_imgDict['Standard Deviation']=[value['stdv'] for value in imgDict.values()]
        datos_imgDict['Noise']=[value['noise'] for value in imgDict.values()]
		


#		print(float(stringval), var_fit[0], var_fit[1], var_fit[2], var_fit[3])
#		list_var.append([float(stringval), var[0], var[1], var[2], var[3]])
        list_var.append([float(stringval), var_fit[0], var_fit[1], var_fit[2], var_fit[3]])		# To use the var obtained from the gaussian fit

		# print(imgDict)

    arr_var=np.array(list_var)
    arr_var=arr_var[np.argsort(arr_var[:, 0])]	# Sort array by values on first column
#	print(arr_var)

    fig_all.legend(handles_all, labels_all, loc='upper right') # histogram figure  
    #plt.show()

#	fig_var.tight_layout()

    if graphicFlag == 1:
        fig_var, axs_var = plt.subplots(1, 4, figsize=(20, 5), sharey=True) # Noise figure
        for k in range(0, 4):
            axs_var[k].plot([row[0] for row in arr_var], [row[k+1] for row in arr_var], ".k")
            axs_var[k].plot([row[0] for row in arr_var], sqrt([row[0] for row in arr_var], arr_var[0, k+1]), "-r")		# Sqrt fit when doing noise vs nsamp
            axs_var[k].set_title('ext '+str(k+1))
            axs_var[k].set_xlabel(string)
            axs_var[k].set_ylabel('Noise (e-)')
            axs_var[k].grid(True)
    #		axs_var[k].set_yscale('log')
    #		axs_var[k].set_ylim([0, 200])
        #plt.show()				# Show plot
    
    Tempt_frame = pd.DataFrame(list_Temp, columns=["Temp"])
    names_frame = pd.DataFrame(list_Names, columns=["Image"])
    nSamp_frame = pd.DataFrame(nSamp, columns=["nSamp"])
    stdev_frame = pd.DataFrame(list_StandarDev, columns=['Std ext1','Std ext2','Std ext3','Std ext4'])
    noises_frame = pd.DataFrame(list_Noises, columns=['Noise ext1','Noise ext2','Noise ext3','Noise ext4'])
    exposure_frame = pd.DataFrame(list_Exposure, columns=['Exposure'] )
    voltage_frame = pd.DataFrame(list_VoltageFile, columns=['Voltage File'])

    if optionFlag == 0: #ID
        total_frame=pd.concat([names_frame, stdev_frame,noises_frame],axis=1)
        return total_frame

    elif optionFlag == 1:#nSamp
        total_frame=pd.concat([names_frame, nSamp_frame, stdev_frame,noises_frame],axis=1)
        nSampFrame = total_frame.sort_values('nSamp')

        if graphicFlag == 2:
            _, axes= plt.subplots(nrows=1,ncols=4, figsize=(20,5))
            nSampFrame.plot(kind='scatter',x='nSamp',y='Noise ext1', ax=axes[0])
            nSampFrame.plot(kind='scatter',x='nSamp',y='Noise ext2', ax=axes[1])
            nSampFrame.plot(kind='scatter',x='nSamp',y='Noise ext3', ax=axes[2])
            nSampFrame.plot(kind='scatter',x='nSamp',y='Noise ext4', ax=axes[3])

        return nSampFrame 

    elif optionFlag == 2: #Std ext1
        total_frame=pd.concat([names_frame, stdev_frame,noises_frame],axis=1)
        Std_ext1Frame = total_frame.sort_values('Std ext1')

        return Std_ext1Frame
    
    elif optionFlag == 3: #Noise ext1
        total_frame=pd.concat([names_frame, stdev_frame,noises_frame],axis=1)
        Noise_ext1Frame = total_frame.sort_values('Noise ext1')

        return Noise_ext1Frame
    
    elif optionFlag == 4: #Temp
        total_frame=pd.concat([names_frame,Tempt_frame, stdev_frame,noises_frame],axis=1)
        TempFrame = total_frame.sort_values('Temp')

        return TempFrame
    
    elif optionFlag == 5: #Exposure
        total_frame=pd.concat([names_frame,exposure_frame, stdev_frame,noises_frame],axis=1)
        ExpFrame = total_frame.sort_values('Exposure')

        return ExpFrame
    
    elif optionFlag == 6: #Voltage
        total_frame=pd.concat([names_frame,voltage_frame, stdev_frame,noises_frame],axis=1)
        VoltFrame = total_frame.sort_values('Voltage File')

        return VoltFrame

def parser():

    parser = argparse.ArgumentParser(prog='Temp Control',description=' ')
    
    parser.add_argument('--NSamp',type= str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--ID',type = str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--Temp',type = str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--StD',type = str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--Noise',type = str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--Exposure',type = str, nargs= '+', help = "If a '?' is entered")
    parser.add_argument('--Voltage',type = str, nargs= '+', help = "If a '?' is entered")

    argObj = parser.parse_args()
    return argObj

def main(argObj):
    value = os.fork()

    if argObj.ID is not None:
        files = argObj.ID
        graphicFlag = 1
        totalDFrame = hist_and_DataFr(files, graphicFlag = 1)
        if value == 0:
            plt.show() # Show hist and noise
        else: 
            print(totalDFrame)
            print('ID OK')
    
    elif argObj.NSamp is not None:
        files = argObj.NSamp
        optionFlag = 1
        graphicFlag = 2
        nSampFrame= hist_and_DataFr(files, optionFlag, graphicFlag)
        if value == 0:
            plt.show() # Show hist and nsamp

        else: 
            print(nSampFrame)
            print('nSamp OK')
    
    elif argObj.StD is not None:
        files = argObj.StD
        optionFlag = 2 
        graphicFlag = 1
        StD_ext1Frame= hist_and_DataFr(files,optionFlag, graphicFlag)
        if value==0:
            plt.show() # Show hist and noise 

        else:
            print(StD_ext1Frame)
            print('Std ext1 OK')
    
    elif argObj.Noise is not None:
        files = argObj.Noise
        optionFlag = 3
        graphicFlag = 1
        Noise_ext1Frame = hist_and_DataFr(files,optionFlag, graphicFlag)
        if value == 0:
            plt.show()
        else:
            print(Noise_ext1Frame)
            print('Noise ext1 OK')
    
    elif argObj.Temp is not None:
        files = argObj.Temp
        optionFlag = 4
        TempFrame = hist_and_DataFr(files,optionFlag)
        if value == 0:
            plt.show()
        else:    
            print(TempFrame)

    elif argObj.Exposure is not None:
        files = argObj.Exposure
        optionFlag = 5
        ExpFrame = hist_and_DataFr(files,optionFlag)
        if value == 0:
            plt.show()
        else:
            print(ExpFrame)
    
    elif argObj.Voltage is not None:
        files = argObj.Voltage
        optionFlag = 6
        VoltFrame = hist_and_DataFr(files,optionFlag)
        if value == 0:
            plt.show()
        else:
            print(VoltFrame)

if __name__ == "__main__":
   argObj=parser()
   exitcode=main(argObj)
   exit(code=exitcode)