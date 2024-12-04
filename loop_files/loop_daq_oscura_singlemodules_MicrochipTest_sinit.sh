#!/bin/bash
###
#
#rutine in progress 24-Ago-2023: 
rutine="Changing  parameter"
#
##
timeStart=$(date)
Vvsub=70

sinit=74     #previous value 30
pinit=0     #previous value 0
ssamp=200
psamp=200

CLEAR=120


imgFOLDER=`dirname $BASH_SOURCE`/images/Microchip/18SEP2023_3/MicrochipTest/Ssamp-PSamp/LTA_3/ #END WITH / please!!!!
runname=m-009_microchip_T_170_
lockfilename=lockfile

clearseq=sequencers/sequencer_microchip_clear_brenda.xml

initscript=init/init_ICN_MM_230208.sh
#-----Acquire raw output data (as seen in the oscilloscope)-----
doRaw(){
	lta startseq
	sleep 0
	lta set bufSel 0	# Select ADC channel to capture (0-3)
	# Transfer raw data
	lta set packSource 4
	lta set packStart 1
	lta getraw
	lta set packSource 9
	lta set packStart 0
	}

#-----Clear without image-----
doClear(){
	if (( $CLEAR ))
	then
	lta sseq $clearseq
	lta NROW 1000000000	#max 32-bit	#>70 sec for NROW 1e5, so NROW 1e9 should run for >7 days
	lta startseq
	sleep $CLEAR
	lta readoff
	fi
	}

#-----Img settings-----
doSettings(){
	lta NROW $rows
	lta NCOL $cols
	lta NSAMP $nsmpls
	lta EXPOSURE $expo
	lta NBINROW $binrow
	lta NBINCOL $bincol

	lta set sinit $sinit #75     #previous value 30
	lta set pinit $pinit #0     #previous value 50
	lta set ssamp $ssamp #200
	lta set psamp $psamp #200
	lta set packSource 9
	lta set cdsout 2 #ped-sig: for mistica  

	
	
	}

#-----Set voltages-----
setVoltages(){
	echo "set voltages ok"
#	lta set vsub $Vvsub
#	lta set vr $Vvr
#	lta set vdd $Vvdd
#	lta set vdrain $Vvdrain
#	lta set swal $Vsl
#	lta set swbl $Vsl

#	lta set swah $Vsh
#	lta set swbh $Vsh
#	lta set ogah $Voh
#	lta set ogbh $Voh
#	lta set dgah $Vdh
#	lta set dgbh $Vdh

#	lta set h1ah $vhh
#	lta set h1bh $Vhh
#	lta set h3ah $Vhh
#	lta set h3bh $Vhh
#	lta set h2ch $Vhh	
#	lta set h1al $Vhl
#	lta set h1bl $Vhl
#	lta set h3al $Vhl
#	lta set h3bl $Vhl
#	lta set h2cl $Vhl
	}

#----------To start----------
touch $lockfilename
mkdir -p $imgFOLDER
source $initscript

doClear
lta sseq sequencers/sequencer_microchip_binned_brenda.xml

source voltage_skp_lta_microchip_vTested_20230518.sh

#----------LOOPS----------
#---Test sinit parameter---
#CLEAR=120
#cols=700; rows=100; binrow=1; bincol=1; nsmpls=1; expo=0;
#for pinit in {3..19}
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#		echo "Rutine $rutine"

#	for times in 1 2 3 4 5
#	do
#		source eraseANDepurge.sh
#		lta set vsub $Vvsub
#		doClear
#		lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#		cols=700; rows=650; binrow=1; bincol=1; nsmpls=1; expo=0;
#		doSettings

#		lta name $imgFOLDER/skp_${runname}_pinit_${pinit}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
#		lta read

		#use skipper to root to process the last image
		#lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
		#fullPathImg=$imgFOLDER$lastFileFZ
		#skp2rr $fullPathImg

		#newFitsImg=$(ls -rt | tail -1)
		#if [[ $newFitsImg == *.fits ]]
		#then
		#	mv $newFitsImg $imgFOLDER
		#else
		#	echo "is not an image"
		#	echo $newFitsImg
		#	sleep 2
		#fi


		#rows=50; nsmpls=324; expo=0;
	        #doSettings
	        #lta name $imgFOLDER/skp_${runname}_sinit_${sinit}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
	        #lta read

	        #use skipper to root to process the last image
	        #lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
	        #fullPathImg=$imgFOLDER$lastFileFZ
	        #skp2rr $fullPathImg

	        #newFitsImg=$(ls -rt | tail -1)
	        #if [[ $newFitsImg == *.fits ]]
	        #then
	        #       mv $newFitsImg $imgFOLDER
	        #else
	        #       echo "is not an image"
	        #       echo $newFitsImg
	        #       sleep 2
	        #fi

	#done
	#doRaw
#done

#end=$(date)

#echo "Start="$timeStart
#echo "End="$end
#echo "image: "$newFitsImg

# #---Test Vv1 Vv2 & Vv3 voltages---
# CLEAR=300
# cols=700; binrow=1; bincol=1;
# for vfile in 82 82 82 82
# do
# 	if [ ! -f "$lockfilename" ]; then break; fi
# 		echo "Rutine $rutine"
# 	#source voltage_skp_lta_v${j}_microchip.sh
# 	#voltage_skp_lta_v2_microchip.sh
# 	source voltages/voltage_skp_lta_v${vfile}_microchip.sh

# 	source eraseANDepurge.sh
# 	lta set vsub $Vvsub

# 	doClear
# 	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

# 	rows=700; nsmpls=1; expo=0;
# 	doSettings
	
# 	lta name $imgFOLDER/skp_${runname}_Vv${vfile}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
# 	lta read

# 	#use skipper to root to process the last image
# 	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
# 	fullPathImg=$imgFOLDER$lastFileFZ
# 	skp2rr $fullPathImg

# 	newFitsImg=$(ls -rt | tail -1)
# 	if [[ $newFitsImg == *.fits ]]
# 	then
# 		mv $newFitsImg $imgFOLDER
# 	else
# 		echo "is not an image"
# 		echo $newFitsImg
# 		sleep 2
# 	fi

# 	rows=50; nsmpls=81; expo=0;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_Vv${vfile}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
# 	lta read

# 	#use skipper to root to process the last image
# 	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
# 	fullPathImg=$imgFOLDER$lastFileFZ
# 	skp2rr $fullPathImg

# 	newFitsImg=$(ls -rt | tail -1)
# 	if [[ $newFitsImg == *.fits ]]
# 	then
# 		mv $newFitsImg $imgFOLDER
# 	else
# 		echo "is not an image"
# 		echo $newFitsImg
# 		sleep 2
# 	fi

# done

# end=$(date)

# echo "Start="$timeStart
# echo "End="$end
# echo "image: "$newFitsImg



#---Test changing nsamp---
# string=_
# CLEAR=120
# cols=700; binrow=1; bincol=1;
# for loop in 1
# do
# 	if [ ! -f "$lockfilename" ]; then break; fi
#         echo "Rutine $rutine"
# 	source eraseANDepurge.sh
# 	lta set vsub $Vvsub

# 	doClear
# 	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

# 	rows=650; nsmpls=$loop; expo=0;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_v${vfile}_seq${string}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
# 	lta read #Read the image

#     	#use skipper to root to process the last image
# 	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
# 	fullPathImg=$imgFOLDER$lastFileFZ
# 	skp2rB $fullPathImg

# 	newFitsImg=$(ls -rt | tail -1)
# 	if [[ $newFitsImg == *.fits ]]
# 	then
# 		mv $newFitsImg $imgFOLDER
# 	else
# 		echo "is not an image"
# 		echo $newFitsImg
# 		sleep 2
# 	fi

# done

# end=$(date)

# echo "Start="$timeStart
# echo "End="$end
# echo "image: "$newFitsImg


#---Generic loop---

# CLEAR=600
# cols=700; rows=10; nsmpls=1; expo=0; binrow=1; bincol=1;

# for loop in {1..10}
# do
# 	cols=700; rows=250; nsmpls=324; expo=0; binrow=1; bincol=1;  #Cambiar a Row = 50
# 	echo "start generic loop"

# 	if [ ! -f "$lockfilename" ]; then break; fi
# 	echo "Rutine $rutine"
# 	source eraseANDepurge.sh
# 	lta set vsub $Vvsub

# 	doClear
# 	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

# 	setVoltages
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read

# 	#use skipper to root to process the last image
# 	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
# 	fullPathImg=$imgFOLDER$lastFileFZ
# 	skp2rB $fullPathImg

# 	newFitsImg=$(ls -rt | tail -1)
# 	if [[ $newFitsImg == *.fits ]]
# 	then
# 		mv $newFitsImg $imgFOLDER
# 	else
# 		echo "is not an image"
# 		echo $newFitsImg
# 		sleep 2
# 	fi

# 	rows=650; nsmpls=1;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read
# 	echo "End of loop $loop in $rutine"
# done
# end=$(date)

# echo "Start="$timeStart
# echo "End="$end

#---Test changing voltages---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for Vvdrain in `seq -20.8 0.2 -20.2`
#for Vvdd in -22 -21 -20 -19 -18 -17
#for Vhl in -1 -0.5 0 0.5 1 1.5
#for Voh in -1.5 -0.5 0.5
#for Vdh in -1 4 9
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	setVoltages
#	doSettings
#	lta name $imgFOLDER/skp_${runname}_hl${Vhl}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#----------STANDARD TESTS----------


#---Test Vv1 Vv2 & Vv3 voltages---

# CLEAR=300
# cols=700; binrow=1; bincol=1;
# for j in 3 2 1
# do
# 	if [ ! -f "$lockfilename" ]; then break; fi
# 	#source voltage_skp_lta_v${j}_microchip.sh
# 	source voltage_skp_lta_v${j}_mitll.sh

# 	source eraseANDepurge.sh
# 	lta set vsub $Vvsub

# 	doClear
# 	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

# 	rows=650; nsmpls=1; expo=150;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_Vv${j}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read

# 	rows=50; nsmpls=324; expo=0;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_Vv${j}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read
# done





#---Test changing ssamp/psamp---

CLEAR=120
cols=700; rows=650; binrow=1; bincol=1; nsmpls=3; expo=0;

doSettings

for smp in `seq 20 20 600`   #from 20, in steps of 20, count up to 600
do
	if [ ! -f "$lockfilename" ]; then break; fi
	delay=$(echo ${smp}+75 | bc)
	delay=$((smp+75))
	lta set ssamp $smp
	lta set psamp $smp
	lta delay_Integ_ped $delay
	lta delay_Integ_sig $delay
	lta name $imgFOLDER/skp_${runname}_loopSSAMP_SSAMP_${smp}_PSAMP_${smp}_delay_${delay}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
	lta read
	#use skipper to root to process the last image
        lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
        fullPathImg=$imgFOLDER$lastFileFZ
        skipper2root -Sird $fullPathImg

        newFitsImg=$(ls -rt | tail -1)
        if [[ $newFitsImg == *.fits ]]
        then
               mv $newFitsImg $imgFOLDER
        else
               echo "is not an image"
               echo $newFitsImg
               sleep 2
        fi
	doRaw

end=$(date)

echo "Start="$timeStart
echo "End="$end
echo "image: "$newFitsImg

done


#---Test changing NSAMP---

#CLEAR=120
#cols=700; rows=100; expo=0; binrow=1; bincol=1;

#for nsmpls in 1 4 9 16 25 49 100 225 400 625 900 1225
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_loopNSAMP_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#---Test changing EXPOSURE---

#CLEAR=300
#cols=700; rows=100; nsmpls=324; binrow=1; bincol=1;

#for loop in `seq 1 1 10`
#do
#for expo in `seq 0 600 1800`
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source eraseANDepurge.sh
#	lta set vsub $Vvsub

#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_loopEXPOSURE_clear${CLEAR}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


#----------TRAP PUMPING AND LED ILLUMINATION----------


#---Loop dtph---

# CLEAR=120
# dtphshort=4; npumps=40000; il_secs=120;
# rows=50; cols=700; nsmpls=10; expo=0; binrow=1; bincol=1;

#for string in a b c d e f
#do
#for dtph in 75 100 200 500 1000 1500 2000 2500 3500 5000 7500 10000 25000 50000 100000 150000 300000 500000 1000000 2000000
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source voltage_skp_microchip_looptraps_${string}.sh

#	doClear
#	lta sseq sequencers/sequencer_microchip_ppump_horizontal.xml

#	doSettings  
#	lta delay_Tph $dtph
#	lta NPUMPS $npumps
#	lta delay_Tphshort $dtphshort
#	python ard_led_ctrl.py $il_secs
#	lta name $imgFOLDER/skp_${runname}_loopdtph_wledon${il_secs}_npump${npumps}_dtph${dtph}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta name $imgFOLDER/skp_${runname}_Vv${string}_loopdtph_wledon${il_secs}_npump${npumps}_dtph${dtph}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


#---Test LED illumination---

#CLEAR=120                                
#rows=650; cols=700; nsmpls=1; expo=0; binrow=1; bincol=1;

#for il_secs in 0.4
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	python ard_led_ctrl.py $il_secs
#	lta name $imgFOLDER/skp_${runname}_wledon${il_secs}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#----------EXTRA TESTS----------


#---Test changing delays---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for delay in `seq 150 50 300`
#do  
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#       doSettings       
#       lta delay_H_overlap $delay
#	lta delay_V_Overlap $delay
#       lta name $imgFOLDER/skp_${runname}_delayH${delay}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#       lta read
#done


#---Test of manual eraseANDepurge---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for slope in 0.05 0.15 0.25
#do
#for sleep in 0.5 1.5 2.5
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source eraseANDepurge_microchip.sh $slope $sleep

#	doClear
#	lta sseq sequencers/sequencer_microchip_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_eANDemicrochip_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


