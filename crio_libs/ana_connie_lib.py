from matplotlib import pyplot as plt
import numpy as np
from astropy.io import fits 
#import re
from scipy.optimize import curve_fit
from scipy import ndimage
import math

# ------------------------------------------------------------------------------
#
# ----  Single Gaussian for the noise computation 
def gaussian1(x,m1,s1,a1):
    return a1*np.exp(-1/2*((x-m1)/s1)**2)
#
# ---- Two Gaussians shifter by g = gain 
def gaussian2(x,m1,s,a1,g,a2):
    return a1*np.exp(-1/2*((x-m1)/s)**2)+a2*np.exp(-1/2*((x-m1-g)/s)**2)
#
# ---- 
def convolution(x, mu, sigma, A, lamb, Nmax=10):
    y = 0.
    for i in range(0, Nmax+1):
        y += (lamb**i)/float(math.factorial(i)) * \
            np.exp(-0.5*((x-i-mu)/float(sigma))**2)
    return A*np.exp(-lamb)*y/(np.sqrt(2*np.pi*sigma**2))
#
# ------------------------------------------------------------------------------

def GetSingleCCDImage(hdul,LTA_channel,ColInit,NCOL,step,NrOfMCMs):
	#hdul: list of hdu of the muxed fit file
	#LTA_channel
	#ColInit: First column in the muxed image
	#NCOL: Number of columns in the image
	MuxedImage=hdul[LTA_channel].data
	step2=step*NrOfMCMs
	LastCol=ColInit+(int(NCOL)-1)*step2
	indexCol=list(range((ColInit-1),LastCol,step2))
	DeMuxedImage=MuxedImage[:, indexCol]
	return DeMuxedImage #return demuxed image


# ------------------------------------------------------------------------------
#
# ---- To compute the baseline evolution in function of the row number
def Baseline(h, region_mask, iMCM, nCCDs, doPlot=False, pdfname='none.pdf'):
    mediana = []
    plt.figure(figsize=(15,6))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    for i in range(0,nCCDs):
        m = np.median(h[i+1].data[region_mask], axis=1,keepdims=True)
        mediana.append(m)
        x = np.arange(len(m))
        plt.plot(x,m-m[0],label='ohdu = {:d} - ref = {}'.format(i+1,m[0]))
        plt.xlim(0,len(m)*1.30)
        plt.xlabel('iROW', fontsize=14)
        plt.ylabel('Baseline (ADUs)', fontsize=14)
        plt.title('MCM {:d}'.format(iMCM),fontsize=16)
        plt.legend(fontsize=12)
    # to save the plot
    if doPlot:
        #pdf_filename = f'baseline_{pdfname}.pdf'
        #plt.savefig(pdf_filename, format='pdf')
        plt.show()
    else:
        plt.close()
    return mediana # array of nCCDs x nRows
# ---- To compute the Noise in a region-----------------------------------------
def Noise(h, region_mask, iMCM, nCCDs, dataOK, doPlot=False, pdfname='noise'):
    noise = []
    ANSAMP=h[1].header["ANSAMP"]
    fig, axs = plt.subplots(ncols=4,nrows=4,figsize=(15,15))

    i=0
    for ncol in axs:
       for nrow in ncol:
            #if int(ANSAMP)>1:
            hist,_,class_marks=plotHistogram(h[i+1].data[region_mask].flatten()/(int(h[1].header['ANSAMP'])), doPlot=False)
            nrow.bar(class_marks,hist)
            try:
                popt,pcov=curve_fit(gaussian1,class_marks,hist,p0=[0,50,1000])
                popt=abs(popt)
                nrow.plot(class_marks,gaussian1(class_marks,*popt),c='r',label="Gauss Fit $\sigma$: {:.3f} ADUs\nMCM {:d} – ohdu = {:d}".format(popt[1],iMCM,i+1))
                noise.append(popt[1])              
            except RuntimeError:
                print("Error - gain fit failed" + pdfname)
                noise.append(-1)
            nrow.set_ylim(1,25e3)
            nrow.set_yscale("log")
            nrow.legend()
            nrow.set_xlabel("Charge [ADUs]",fontsize=12)
        
            nrow.set_ylabel("Entries",fontsize=12)
            i+=1
    # to save the plot
    #pdf_filename = f'noise_'+pdfname+'_{iMCM+1}.pdf'i
    if doPlot:
        pdf_filename = f'noise_{pdfname}.pdf'
        #plt.savefig(pdf_filename, format='pdf')
        fig.suptitle('ANSAMP '+ANSAMP)
        plt.show()
    elif doPlot == False:
        plt.close()
    else:
        plt.close()
    return noise
# ---- To compute the gain of the image-----------------------------------------
def Gain(h, active_mask, iMCM, nCCDs, dataOK=True, doPlot=False, pdfname='gain'):
    gain = []

    ANSAMP=h[1].header["ANSAMP"]
    fig, axs = plt.subplots(ncols=4,nrows=4,figsize=(15,15))

    i=0
    for ncol in axs:
       for nrow in ncol:
        
        hist,_,class_marks=plotHistogram(h[i+1].data[active_mask].flatten()/(int(h[1].header['ANSAMP'])), doPlot=False)
        nrow.bar(class_marks,hist)
        try:
            popt,pcov=curve_fit(gaussian2,class_marks,hist,p0=[0,10,1000,60,100]) #gaussian2(x,m1,s,a1,g,a2)
            popt=abs(popt)
            nrow.plot(class_marks,gaussian2(class_marks,*popt),c='r',label="Gauss Fit $\sigma$: {:.3f} ADUs\nMCM {:d} ohdu = {:d} \n Gain = {:.3f}".format(popt[1],iMCM,i+1, popt[3]))
            gain.append(popt[1])              
        except RuntimeError:
            print("Error - gain fit failed" + pdfname)
            gain.append(-1)
        nrow.set_ylim(1,25e3)
        nrow.set_yscale("log")
        nrow.legend()
        nrow.set_xlabel("Charge [ADUs]",fontsize=12)
    
        nrow.set_ylabel("Entries",fontsize=12)
        i+=1
     
    # to save the plot
    if doPlot:
        pdf_filename = f'gain_{pdfname}.pdf'
        #plt.savefig(pdf_filename, format='pdf')
        plt.show()
    else:
        plt.close()
    return gain

    # plt.figure(figsize=(24,24))
    # plt.xticks(fontsize=13)
    # plt.yticks(fontsize=13)
    # plt.title("MCM {:d}".format(iMCM), fontsize=18)
    # for i in range(nCCDs):
    #     if dataOK:
    #         plt.subplot(4,4,i+1)
    #         y,xb=np.histogram(h[i+1].data[active_mask].flatten(), bins=np.linspace(-100,500,300))
    #         x=(xb[1:]+xb[:-1])/2
    #         plt.plot(x,y,label='MCM {:d} – ohdu = {:d}'.format(iMCM,i+1))
    #         # gaussian2 fit
# ---- To compute Single electron rate------------------------------------------
def Ser(h, active_mask, iMCM, nCCDs, dataOK, gain, doPlot, pdfname, itera=10, thr=5):
    ser = []
    plt.figure(figsize=(24,24))
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.title("MCM {:d}".format(iMCM), fontsize=18)
    for i in range(nCCDs):
        if True:
            data = h[i+1].data/gain[i]
            event_mask = data > thr
            event_halo_mask = ndimage.binary_dilation(
                              event_mask,
                              iterations = itera,
                              structure = ndimage.generate_binary_structure(rank=2, connectivity=2))
            dataMasked = np.where(event_halo_mask, np.nan, data )
            #mask = ndimage.binary_dilation(data>thr,iterations=itera,structure=[[1,1,1],[1,1,1],[1,1,1]])
            #dataMasked = data - 1000000*mask.astype(data.dtype)
            #dataMasked = np.ma.masked_less(dataMasked, -50000)
            plt.subplot(4,4,i+1)
            y, xb = np.histogram(dataMasked[active_mask].flatten()/(int(h[1].header['ANSAMP'])),range=[-2,6],bins='fd')
            x = (xb[1:]+xb[:-1])/2
            plt.plot(x, y,label='MCM {:d} – ohdu = {:d}'.format(iMCM,i+1))
            try:
                popt, pcov = curve_fit(convolution, x, y, p0=[-0.4, 0.2, 1000, 0.1])
                plt.plot(x, convolution(x, *popt), label="Noise: {:.3f}  SER: {:.4f} ".format(abs(popt[1]),popt[3]),color='red')
                if popt[3]>0 and popt[3]<100:
                    ser.append(popt[3])
                else: ser.append(-1)
            except RuntimeError:
                print("Error - convolution fit failed " + pdfname)
                ser.append(-1)
            plt.xlabel("e-",fontsize=12)
            plt.ylabel("Entries",fontsize=12)
            plt.yscale("log")
            plt.legend(fontsize=13)
        else: ser.append(-1)
    # to save the ploti
    if doPlot:
        pdf_filename = f'ser_{pdfname}.pdf'
        #plt.savefig(pdf_filename, format='pdf')
    plt.show()
    return ser
# -------------------------------------------------------------------------

def plotHistogram(data, range =(-200,300), doPlot=True):
    histo, bins_edges = np.histogram(data,bins='fd',range=range)
    class_marks = (bins_edges[:-1]+bins_edges[1:])/2
    if doPlot:
        plt.bar(class_marks,histo)
        plt.yscale('log')
        plt.grid(True)
    return histo, bins_edges, class_marks

def histoFit(hdu, ext, region,range =(-200,300), porDefecto=[0,3,1500, 44, 100]): #data, mean, stdDev, h1, gain, h2
    hist,bins,class_mark=plotHistogram(hdu[ext].data[region].flatten(),range=range)
    popt,pcov=curve_fit(gaussian2,class_mark,hist,p0=porDefecto) 
    #popt=abs(popt)
    plt.grid(True)
    plt.plot(class_mark,gaussian2(class_mark,*popt),linewidth=1,c='r', label=r'$\sigma$={:.2f}  gain={:.2f}'.format(abs(popt[1]),abs(popt[3])))
    plt.ylim(1,25e3)  
    plt.legend()
    return popt

def comp2regions(data_1,data_2,range_1=(-300,850), range_2=(-300,850),default_1=[0,13,1000,50,200],default_2=[0,8,1000,75,200], title_1="data_1", title_2="data_2"):
    fig, (hist_1, hist_2) = plt.subplots(ncols=2, figsize=(12, 4))# plt.subplots(2,1)

    #ansamp=int(OHDU_File[1].header['ANSAMP'])
    limits_1=range_1
    histogram_1, bins_edges_1 = np.histogram(data_1,bins='fd',range=limits_1)
    class_marks_1 = (bins_edges_1[:-1]+bins_edges_1[1:])/2
    popt,pcov=curve_fit(gaussian2,class_marks_1,histogram_1,p0=default_1)
    left = hist_1.bar(class_marks_1,histogram_1)
    left = hist_1.plot(class_marks_1,gaussian2(class_marks_1,*popt),linewidth=1,c='r', label=r'$\sigma$={:.2f}  gain={:.2f}'.format(abs(popt[1]),abs(popt[3])))        
    left = hist_1.grid(True)
    left = hist_1.set_ylim(1,25e3)  
    left = hist_1.legend()
    left = hist_1.set_yscale('log')
    left = hist_1.grid(True)
    left = hist_1.set_title(title_1)

    limits_2=range_2
    histogram_2, bins_edges_2 = np.histogram(data_2,bins='fd',range=limits_2)
    class_marks_2 = (bins_edges_2[:-1]+bins_edges_2[1:])/2
    popt_2,pcov_2=curve_fit(gaussian2,class_marks_2,histogram_2,p0=default_2)

    right = hist_2.bar(class_marks_2,histogram_2)
    right = hist_2.plot(class_marks_2,gaussian2(class_marks_2,*popt_2),linewidth=1,c='r', label=r'$\sigma$={:.2f}  gain={:.2f}'.format(abs(popt_2[1]),abs(popt_2[3])))        
    right = hist_2.grid(True)
    right = hist_2.set_ylim(1,25e3)  
    right = hist_2.legend()
    right = hist_2.set_yscale('log')
    right = hist_2.grid(True)
    right = hist_2.set_title(title_2)
    plt.show()
    return 'ok'

